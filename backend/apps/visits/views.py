from datetime import date, time, timedelta

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
from .models import ECUADOR_TZ, AgentAvailability, AvailabilityException, Visit, ecuador_today
from .serializers import (
    AgendaVisitSerializer,
    AvailabilityExceptionSerializer,
    AvailabilitySerializer,
    CancelVisitSerializer,
    OutcomeSerializer,
    PublicVisitSerializer,
    VisitRequestSerializer,
)
from .services import (
    SCHEDULABLE_PROPERTY_STATUSES,
    OutcomeAlreadyRecorded,
    SlotUnavailable,
    VisitAlreadyScheduled,
    VisitNotCancellable,
    cancel_visit,
    free_slots,
    local_datetime,
    public_visit_by_token,
    record_outcome,
    request_visit,
    resolve_target_agent,
)

User = get_user_model()

# HU-18: solo se agenda sobre propiedades publicadas (Disponible). Una propiedad en captacion o
# reservada no admite visitas (RF-04; decision de Pablo, 2026-11-06). La constante vive en
# services.py para que HU-19 use la misma regla.
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


def parse_agenda_range(params):
    '''
    HU-24: semana actual (lunes a domingo, hora de Ecuador) por defecto; maximo 31 dias. Se
    aceptan fechas pasadas: la agenda es tambien el historial para registrar resultados (HU-25).
    Con solo una de las fechas, el rango es la semana de 7 dias que empieza o termina en ella.
    '''
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

    if 'from' in days and 'to' in days:
        date_from, date_to = days['from'], days['to']
    elif 'from' in days:
        date_from = days['from']
        date_to = date_from + timedelta(days=6)
    elif 'to' in days:
        date_to = days['to']
        date_from = date_to - timedelta(days=6)
    else:
        today = ecuador_today()
        date_from = today - timedelta(days=today.weekday())
        date_to = date_from + timedelta(days=6)

    if date_to < date_from:
        raise serializers.ValidationError({'to': 'La fecha final no puede ser anterior a la inicial.'})
    if (date_to - date_from).days + 1 > MAX_RANGE_DAYS:
        raise serializers.ValidationError({'to': f'El rango no puede superar {MAX_RANGE_DAYS} días.'})
    return date_from, date_to


class AgendaView(APIView):
    '''
    HU-24 (I-08, RF-04): agenda de visitas del asesor, ordenada por hora de inicio.

    GET /api/visits/agenda/?from=AAAA-MM-DD&to=AAAA-MM-DD&agent=&status=
    - el asesor ve solo su agenda; ?agent= se ignora (igual que en HU-22);
    - el admin elige el asesor con ?agent= (400 si falta o no es un asesor);
    - status: por defecto todas menos CANCELADA; ?status=<estado> filtra uno (incluida
      CANCELADA); ?status=all las muestra todas;
    - anonimo: 401.
    Filtra por Visit.agent: una visita sigue con su asesor aunque se reasigne la propiedad.
    '''
    permission_classes = [permissions.IsAuthenticated, IsInternalUser]

    def resolve_agent(self, request):
        user = request.user
        if user.role != 'admin':
            return user
        agent_id = request.query_params.get('agent')
        if not agent_id:
            raise serializers.ValidationError({'agent': 'Elija el asesor de la agenda.'})
        if not agent_id.isdigit():
            raise serializers.ValidationError({'agent': 'Debe ser un id numérico.'})
        # Tambien un asesor inactivo: su historial de visitas sigue siendo consultable.
        agent = User.objects.filter(pk=agent_id, role='asesor').first()
        if agent is None:
            raise serializers.ValidationError({'agent': 'Debe ser un asesor.'})
        return agent

    def get(self, request):
        agent = self.resolve_agent(request)
        date_from, date_to = parse_agenda_range(request.query_params)

        visits = (Visit.objects
                  .filter(agent=agent,
                          scheduled_start__gte=local_datetime(date_from, time.min),
                          scheduled_start__lt=local_datetime(date_to + timedelta(days=1),
                                                             time.min))
                  .select_related('property', 'opportunity__contact',
                                  'opportunity__assigned_agent', 'outcome_recorded_by')
                  .order_by('scheduled_start', 'id'))
        status_value = request.query_params.get('status')
        if not status_value:
            visits = visits.exclude(status=Visit.Status.CANCELADA)
        elif status_value != 'all':
            if status_value not in Visit.Status.values:
                raise serializers.ValidationError({'status': 'Estado no válido.'})
            visits = visits.filter(status=status_value)

        return Response({
            'agent': agent.pk,
            'from': date_from.isoformat(),
            'to': date_to.isoformat(),
            'timezone': str(ECUADOR_TZ),
            'visits': AgendaVisitSerializer(visits, many=True).data,
        })


class IPRateThrottle(SimpleRateThrottle):
    '''Limite por IP para endpoints publicos sin sesion (DS-39). Cache por defecto de Django.'''

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class VisitRequestBurstThrottle(IPRateThrottle):
    scope = 'visits_request_burst'
    rate = '3/minute'


class VisitRequestDailyThrottle(IPRateThrottle):
    scope = 'visits_request_daily'
    rate = '10/day'


class PublicVisitThrottle(IPRateThrottle):
    scope = 'visits_public_token'
    rate = '30/minute'


# Mismo texto exista o no el contacto: la respuesta no revela datos de otros clientes (DS-39).
REQUEST_OK_MESSAGE = 'Tu solicitud de visita quedó registrada.'


class VisitRequestView(APIView):
    '''
    HU-19 (P-07, RF-04): el cliente sin cuenta solicita una visita en una franja libre.

    POST /api/visits/properties/<id>/request/   (publico; 3/min y 10/dia por IP)
    {"start": "AAAA-MM-DDTHH:MM:SS-05:00", "full_name", "phone", "email", "email_opt_in",
     "privacy_accepted"}
    -> 201 {"detail", "scheduled_start", "scheduled_end", "confirmation": "email"|"whatsapp"}
       Sin token, sin datos del asesor ni de otros clientes.
    -> 400 datos invalidos o franja que no es (o ya no es) una de las ofrecidas
    -> 404 propiedad inexistente o no Disponible
    -> 409 la oportunidad ya tiene una visita Programada
    '''
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [VisitRequestBurstThrottle, VisitRequestDailyThrottle]

    def post(self, request, property_id):
        property_obj = (Property.objects.select_related('agent')
                        .filter(pk=property_id, status__in=SCHEDULABLE_PROPERTY_STATUSES).first())
        if property_obj is None:
            raise Http404
        serializer = VisitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            visit = request_visit(
                property_obj=property_obj, start=data['start'], full_name=data.get('full_name'),
                phone=data.get('phone'), email=data.get('email'),
                email_opt_in=data['email_opt_in'], privacy_accepted=data['privacy_accepted'],
            )
        except DjangoValidationError as error:
            raise to_drf_error(error)
        except SlotUnavailable:
            raise serializers.ValidationError({
                'start': 'Ese horario ya no está disponible. Actualiza y elige otro.',
            })
        except VisitAlreadyScheduled:
            return Response(
                {'detail': 'Ya tienes una visita programada para esta propiedad. '
                           'Para cambiarla, comunícate con tu asesor.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response({
            'detail': REQUEST_OK_MESSAGE,
            'scheduled_start': visit.scheduled_start.astimezone(ECUADOR_TZ).isoformat(),
            'scheduled_end': visit.scheduled_end.astimezone(ECUADOR_TZ).isoformat(),
            'confirmation': 'email' if visit.confirmation_email else 'whatsapp',
        }, status=status.HTTP_201_CREATED)


class PublicVisitView(APIView):
    '''
    HU-20 (P-08): datos de la visita por su enlace unico, solo lectura y solo hasta la hora de
    inicio. GET /api/visits/public/<token>/ ; token inexistente o vencido: el mismo 404.
    HU-21 (DS-52): incluye can_cancel y cancel_until; la cancelacion es PublicVisitCancelView.
    '''
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PublicVisitThrottle]

    def get(self, request, token):
        visit = public_visit_by_token(token)
        if visit is None:
            raise Http404
        return Response(PublicVisitSerializer(visit).data)


class PublicVisitCancelView(APIView):
    '''
    HU-21 (P-08, DS-52): el cliente cancela su visita con el enlace unico.
    POST /api/visits/public/<token>/cancel/   (publico; mismo limite que P-08, 30/min por IP)
    -> 200 con los datos de P-08 (estado Cancelada)
    -> 400 si falta menos de 1 hora para el inicio
    -> 404 token inexistente o visita ya empezada (mismo 404 que P-08)
    -> 409 si ya no esta Programada
    '''
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PublicVisitThrottle]

    def post(self, request, token):
        visit = public_visit_by_token(token)
        if visit is None:
            raise Http404
        try:
            cancel_visit(visit_id=visit.pk)
        except DjangoValidationError as error:
            raise to_drf_error(error)
        except VisitNotCancellable:
            return Response({'detail': 'Esta visita ya no está programada.'},
                            status=status.HTTP_409_CONFLICT)
        visit = public_visit_by_token(token)
        return Response(PublicVisitSerializer(visit).data)


def internal_visit_or_404(request, visit_id):
    '''Visita para el asesor (solo las suyas) o el admin (todas); lo ajeno responde 404.'''
    visits = Visit.objects.select_related(
        'property', 'opportunity__contact', 'opportunity__assigned_agent', 'outcome_recorded_by',
    )
    if request.user.role != 'admin':
        visits = visits.filter(agent=request.user)
    visit = visits.filter(pk=visit_id).first()
    if visit is None:
        raise Http404
    return visit


class VisitCancelView(APIView):
    '''
    HU-21 (I-08, DS-52): el asesor de la visita o el admin la cancelan desde la agenda.
    POST /api/visits/<id>/cancel/  {"reason": "..."}  (motivo obligatorio)
    -> 200 con la visita de la agenda; 400 sin motivo o si ya empezo; 404 visita ajena;
       409 si ya no esta Programada. Aviso al cliente por correo si lo dio.
    '''
    permission_classes = [permissions.IsAuthenticated, IsInternalUser]

    def post(self, request, visit_id):
        visit = internal_visit_or_404(request, visit_id)
        serializer = CancelVisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            cancel_visit(visit_id=visit.pk, user=request.user,
                         reason=serializer.validated_data['reason'])
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        except VisitNotCancellable:
            return Response({'detail': 'Esta visita ya no está programada.'},
                            status=status.HTTP_409_CONFLICT)
        return Response(AgendaVisitSerializer(internal_visit_or_404(request, visit_id)).data)


class VisitOutcomeView(APIView):
    '''
    HU-25 (I-08, RF-04): resultado de la visita.

    POST /api/visits/<id>/outcome/  {"status": "REALIZADA"|"NO_ASISTIDA"|"CANCELADA",
                                     "outcome_notes": "..."}
    - el asesor de la visita o el admin; otro asesor: 404 (no ve visitas ajenas);
    - solo despues de la hora de inicio (400) y una sola vez (409);
    - NO_ASISTIDA o CANCELADA de la unica visita activa: Visita Programada -> Contacto Inicial.
    '''
    permission_classes = [permissions.IsAuthenticated, IsInternalUser]

    def post(self, request, visit_id):
        visits = Visit.objects.select_related(
            'property', 'opportunity__contact', 'opportunity__assigned_agent',
        )
        if request.user.role != 'admin':
            visits = visits.filter(agent=request.user)
        visit = visits.filter(pk=visit_id).first()
        if visit is None:
            raise Http404
        serializer = OutcomeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            visit = record_outcome(
                visit=visit, user=request.user, outcome=serializer.validated_data['status'],
                notes=serializer.validated_data.get('outcome_notes'),
            )
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        except OutcomeAlreadyRecorded:
            return Response({'detail': 'El resultado de esta visita ya fue registrado.'},
                            status=status.HTTP_409_CONFLICT)
        visit = (Visit.objects.select_related('property', 'opportunity__contact',
                                              'opportunity__assigned_agent',
                                              'outcome_recorded_by')
                 .get(pk=visit.pk))
        return Response(AgendaVisitSerializer(visit).data)
