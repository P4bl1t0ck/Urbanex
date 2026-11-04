from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.appraisals.serializers import to_drf_error
from .models import Opportunity
from .serializers import (
    AgentOptionSerializer,
    EligiblePropertySerializer,
    OpportunityOpenSerializer,
    OpportunitySerializer,
)
from .services import (
    OpportunityConflict,
    assignable_agents,
    eligible_properties,
    is_internal_user,
    open_manual_opportunity,
)

# DT-01: TIME_ZONE sigue en UTC. El rango de fechas de HU-34 se interpreta en hora de Ecuador
# (DS-28), para que una oportunidad abierta de noche no aparezca en el dia siguiente.
ECUADOR_TZ = ZoneInfo('America/Guayaquil')


class IsInternalUser(permissions.BasePermission):
    message = 'Solo los usuarios internos acceden a las oportunidades.'

    def has_permission(self, request, view):
        return is_internal_user(request.user)


class OpportunityPagination(PageNumberPagination):
    page_size = 20


def local_day_start(day):
    return datetime.combine(day, time.min, tzinfo=ECUADOR_TZ)


def filter_opportunities(queryset, params):
    '''HU-34: los filtros se combinan. Un valor mal formado responde 400, nunca se ignora.'''
    errors = {}
    for field in ('assigned_agent', 'property'):
        value = params.get(field)
        if value:
            if value.isdigit():
                queryset = queryset.filter(**{f'{field}_id': value})
            else:
                errors[field] = 'Debe ser un id numérico.'

    status_value = params.get('status')
    if status_value:
        if status_value in Opportunity.Status.values:
            queryset = queryset.filter(status=status_value)
        else:
            errors['status'] = 'Estado no válido.'

    days = {}
    for field in ('created_from', 'created_to'):
        value = params.get(field)
        if value:
            try:
                days[field] = date.fromisoformat(value)
            except ValueError:
                errors[field] = 'Use el formato AAAA-MM-DD.'
    if 'created_from' in days and 'created_to' in days and days['created_from'] > days['created_to']:
        errors['created_to'] = 'La fecha final no puede ser anterior a la inicial.'

    if errors:
        raise serializers.ValidationError(errors)
    if 'created_from' in days:
        queryset = queryset.filter(created_at__gte=local_day_start(days['created_from']))
    if 'created_to' in days:
        queryset = queryset.filter(
            created_at__lt=local_day_start(days['created_to'] + timedelta(days=1))
        )
    return queryset


class OpportunityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    '''
    Oportunidades (RF-05, HU-27 y HU-34). Primer corte: sin detalle ni cambios de estado
    (I-06A y RF-06 llegan despues).

    GET  /api/opportunities/?assigned_agent=&property=&status=&created_from=&created_to=
         -> cartera paginada; el asesor ve la suya y el admin todas (HU-34)
    POST /api/opportunities/  -> apertura manual (HU-27, I-07); 409 si ya hay una activa
    GET  /api/opportunities/eligible-properties/  -> propiedades disponibles, datos publicos
    GET  /api/opportunities/agents/  -> asesores activos (solo admin, para elegir responsable)
    '''
    permission_classes = [permissions.IsAuthenticated, IsInternalUser]
    http_method_names = ['get', 'post', 'head', 'options']
    serializer_class = OpportunitySerializer
    pagination_class = OpportunityPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Opportunity.objects.select_related('contact', 'property', 'assigned_agent')
        # Permiso por objeto: el asesor solo ve su cartera (RNF-04, HU-34).
        if user.role != 'admin':
            queryset = queryset.filter(assigned_agent=user)
        return filter_opportunities(queryset, self.request.query_params)

    def create(self, request):
        data = OpportunityOpenSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        try:
            opportunity, contact_reused = open_manual_opportunity(
                registered_by=request.user,
                property_obj=values['property'],
                full_name=values['full_name'],
                phone=values['phone'],
                email=values['email'],
                privacy_accepted=values['privacy_accepted'],
                assigned_agent=values['assigned_agent'],
            )
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        except OpportunityConflict as conflict:
            return Response({
                'detail': str(conflict),
                'existing_opportunity_id': conflict.existing.id if conflict.existing else None,
            }, status=status.HTTP_409_CONFLICT)
        return Response({
            'opportunity': OpportunitySerializer(opportunity, context={'request': request}).data,
            'contact_reused': contact_reused,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='eligible-properties')
    def eligible_properties(self, request):
        properties = eligible_properties().prefetch_related('images').order_by('title')
        return Response(
            EligiblePropertySerializer(properties, many=True, context={'request': request}).data
        )

    @action(detail=False, methods=['get'])
    def agents(self, request):
        if request.user.role != 'admin':
            raise PermissionDenied('Solo el administrador elige el asesor responsable.')
        agents = assignable_agents().order_by('first_name', 'last_name', 'username')
        return Response(AgentOptionSerializer(agents, many=True).data)
