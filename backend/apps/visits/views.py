from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.http import Http404
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from apps.appraisals.serializers import to_drf_error
from apps.opportunities.views import IsInternalUser
from apps.users.models import Property
from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, ecuador_today
from .serializers import AvailabilityExceptionSerializer, AvailabilitySerializer
from .services import free_slots, resolve_target_agent

User = get_user_model()

# HU-18: solo se agenda sobre propiedades publicadas (Disponible). Una propiedad en captacion o
# reservada no admite visitas (RF-04; decision de Pablo, 2026-11-06).
SCHEDULABLE_PROPERTY_STATUSES = ('disponible',)
DEFAULT_RANGE_DAYS = 14
MAX_RANGE_DAYS = 31


class AgentScopedViewSet(viewsets.ModelViewSet):
    '''
    Disponibilidad del asesor (HU-22, I-09, RF-09).

    GET    <base>/?agent=     -> el asesor ve lo suyo; el admin todo, o el de un asesor
    POST   <base>/            -> el asesor, a su nombre (403 si pide otro); el admin indica
                                 'agent' (400 si falta o no es un asesor activo)
    GET/PATCH/PUT/DELETE <base>/<id>/ -> lo ajeno responde 404 (el queryset ya viene filtrado);
                                 el asesor de la franja no se cambia (400)
    Anonimo: 401.
    '''
    permission_classes = [permissions.IsAuthenticated, IsInternalUser]
    pagination_class = None  # Un asesor tiene pocas franjas: la pantalla las muestra todas

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.select_related('agent')
        if user.role != 'admin':
            return queryset.filter(agent=user)
        agent_id = self.request.query_params.get('agent')
        if agent_id:
            if not agent_id.isdigit():
                raise serializers.ValidationError({'agent': 'Debe ser un id numérico.'})
            queryset = queryset.filter(agent_id=agent_id)
        return queryset

    def lock_agent(self, agent):
        # Serializa las altas y ediciones del mismo asesor para que dos franjas que se cruzan no
        # pasen la validacion a la vez (en PostgreSQL; SQLite ya serializa las escrituras).
        User.objects.select_for_update().filter(pk=agent.pk).first()

    def create(self, request, *args, **kwargs):
        try:
            agent = resolve_target_agent(request.user, request.data.get('agent'))
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        with transaction.atomic():
            self.lock_agent(agent)
            serializer = self.get_serializer(
                data=request.data, context={**self.get_serializer_context(), 'agent': agent},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(agent=agent)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        requested_agent = request.data.get('agent')
        if requested_agent not in (None, '') and str(requested_agent) != str(instance.agent_id):
            raise serializers.ValidationError({'agent': 'No se cambia el asesor de un registro.'})
        with transaction.atomic():
            self.lock_agent(instance.agent)
            serializer = self.get_serializer(
                instance, data=request.data, partial=kwargs.get('partial', False),
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)


class AvailabilityViewSet(AgentScopedViewSet):
    queryset = AgentAvailability.objects.all()
    serializer_class = AvailabilitySerializer


class AvailabilityExceptionViewSet(AgentScopedViewSet):
    queryset = AvailabilityException.objects.all()
    serializer_class = AvailabilityExceptionSerializer


class FreeSlotsThrottle(SimpleRateThrottle):
    '''
    Limite de peticiones solo para el endpoint publico de HU-18, por IP (o por usuario si hay
    sesion). Se define aqui y no en la configuracion global de DRF (decision de Pablo,
    2026-11-06). Usa la cache por defecto de Django.
    '''
    scope = 'visits_free_slots'
    rate = '30/minute'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = f'user-{request.user.pk}'
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


def parse_range(params):
    '''from y to (AAAA-MM-DD, hora de Ecuador): 14 dias desde hoy por defecto, 31 como maximo.'''
    errors = {}
    days = {}
    for field in ('from', 'to'):
        value = params.get(field)
        if value:
            try:
                days[field] = date.fromisoformat(value)
            except ValueError:
                errors[field] = 'Use el formato AAAA-MM-DD.'
    if errors:
        raise serializers.ValidationError(errors)

    today = ecuador_today()
    date_from = days.get('from', today)
    date_to = days.get('to', date_from + timedelta(days=DEFAULT_RANGE_DAYS - 1))
    if date_from < today:
        errors['from'] = 'La fecha inicial no puede estar en el pasado.'
    elif date_to < date_from:
        errors['to'] = 'La fecha final no puede ser anterior a la inicial.'
    elif (date_to - date_from).days + 1 > MAX_RANGE_DAYS:
        errors['to'] = f'El rango no puede superar {MAX_RANGE_DAYS} días.'
    if errors:
        raise serializers.ValidationError(errors)
    return date_from, date_to


class PropertyFreeSlotsView(APIView):
    '''
    HU-18 (P-07, RF-09): franjas libres del asesor responsable de una propiedad publicada.

    GET /api/visits/properties/<id>/free-slots/?from=AAAA-MM-DD&to=AAAA-MM-DD   (publico)
    -> {"property": id, "timezone": "America/Guayaquil",
        "slots": [{"start": "...-05:00", "end": "...-05:00"}, ...]}

    Solo franjas libres: ni el asesor, ni contactos, ni visitas (pedido de Pablo, 2026-11-06).
    404 si la propiedad no existe o no esta Disponible; slots vacio si su asesor responsable
    no existe o esta inactivo. Sin autenticacion: un token vencido no bloquea la ficha publica.
    '''
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [FreeSlotsThrottle]

    def get(self, request, property_id):
        property_obj = (Property.objects.select_related('agent')
                        .filter(pk=property_id, status__in=SCHEDULABLE_PROPERTY_STATUSES).first())
        if property_obj is None:
            raise Http404
        date_from, date_to = parse_range(request.query_params)

        agent = property_obj.agent
        if agent is None or not agent.is_active or agent.role != 'asesor':
            slots = []
        else:
            slots = free_slots(agent, date_from, date_to)
        return Response({
            'property': property_obj.pk,
            'timezone': str(ECUADOR_TZ),
            'slots': [
                {'start': slot.start.isoformat(), 'end': slot.end.isoformat()} for slot in slots
            ],
        })
