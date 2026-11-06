from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.appraisals.serializers import to_drf_error
from apps.opportunities.views import IsInternalUser
from .models import AgentAvailability, AvailabilityException
from .serializers import AvailabilityExceptionSerializer, AvailabilitySerializer
from .services import resolve_target_agent

User = get_user_model()


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
