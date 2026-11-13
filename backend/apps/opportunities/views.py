from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import mixins, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from apps.appraisals.serializers import to_drf_error
from .models import Opportunity
from .serializers import (
    AgentOptionSerializer,
    EligiblePropertySerializer,
    InteractionCreateSerializer,
    InteractionSerializer,
    MarkLostSerializer,
    OpportunityDetailSerializer,
    OpportunityOpenSerializer,
    OpportunitySerializer,
    StatusChangeSerializer,
    WebInterestSerializer,
)
from .services import (
    InterestNotAccepted,
    OpportunityConflict,
    add_interaction,
    advance_status,
    agent_whatsapp_number,
    assignable_agents,
    eligible_properties,
    is_internal_user,
    mark_lost,
    open_manual_opportunity,
    register_web_interest,
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


class OpportunityViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    '''
    Oportunidades (RF-05, RF-06; HU-27, HU-34, HU-29 y HU-30).

    GET  /api/opportunities/?assigned_agent=&property=&status=&created_from=&created_to=
         -> cartera paginada; el asesor ve la suya y el admin todas (HU-34)
    POST /api/opportunities/  -> apertura manual (HU-27, I-07); 409 si ya hay una activa
    GET  /api/opportunities/eligible-properties/  -> propiedades disponibles, datos publicos
    GET  /api/opportunities/agents/  -> asesores activos (solo admin, para elegir responsable)

    Lote 4 (DS-50), I-06A. El asesor asignado o el admin; otro asesor recibe 404, como en la
    cartera (no ve oportunidades ajenas):
    GET  /api/opportunities/<id>/  -> detalle con historial, interacciones y visitas
    POST /api/opportunities/<id>/status/  {"status", "agreed_final_price"?}  -> HU-29
    GET  /api/opportunities/<id>/interactions/  -> HU-30, orden cronologico
    POST /api/opportunities/<id>/interactions/
         {"interaction_type": "NOTA"|"CONTRAOFERTA", "notes", "offered_price"?, "visit"?}

    Lotes 5 y 6 (DS-52):
    GET  /api/opportunities/<id>/ -> tambien los documentos de la propiedad (HU-33)
    POST /api/opportunities/<id>/lose/ {"loss_reason", "notes"?}  -> HU-31, Perdida
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
        if self.action != 'list':
            # Los filtros de la cartera no aplican al detalle ni a sus acciones.
            return queryset.prefetch_related(
                'status_history__changed_by', 'interactions__author', 'visits',
                'property__documents__uploaded_by',  # HU-33 (DS-52)
            )
        return filter_opportunities(queryset, self.request.query_params)

    def retrieve(self, request, pk=None):
        return Response(OpportunityDetailSerializer(self.get_object()).data)

    @action(detail=True, methods=['post'], url_path='status')
    def change_status(self, request, pk=None):
        opportunity = self.get_object()
        data = StatusChangeSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        try:
            advance_status(
                opportunity_id=opportunity.pk, user=request.user,
                target_status=data.validated_data['status'],
                agreed_final_price=data.validated_data['agreed_final_price'],
            )
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        return Response(OpportunityDetailSerializer(self.get_object()).data)

    @action(detail=True, methods=['post'])
    def lose(self, request, pk=None):
        '''HU-31 (DS-52): POST /api/opportunities/<id>/lose/ {"loss_reason", "notes"?}.'''
        opportunity = self.get_object()
        data = MarkLostSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        try:
            mark_lost(opportunity_id=opportunity.pk, user=request.user,
                      loss_reason=data.validated_data['loss_reason'],
                      notes=data.validated_data['notes'])
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        return Response(OpportunityDetailSerializer(self.get_object()).data)

    @action(detail=True, methods=['get', 'post'])
    def interactions(self, request, pk=None):
        opportunity = self.get_object()
        if request.method == 'GET':
            return Response(InteractionSerializer(opportunity.interactions.all(), many=True).data)
        data = InteractionCreateSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        try:
            interaction = add_interaction(
                opportunity_id=opportunity.pk, user=request.user,
                interaction_type=values['interaction_type'], notes=values['notes'],
                offered_price=values['offered_price'], visit_id=values['visit'],
            )
        except DjangoPermissionDenied as error:
            raise PermissionDenied(str(error))
        except DjangoValidationError as error:
            raise to_drf_error(error)
        return Response(InteractionSerializer(interaction).data, status=status.HTTP_201_CREATED)

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


# ---------------------------------------------------------------------------------------------
# Lote 4 (DS-50): endpoints publicos de la ficha P-07, sin sesion
# ---------------------------------------------------------------------------------------------

class IPRateThrottle(SimpleRateThrottle):
    '''
    Limite por IP para los endpoints publicos. Cache por defecto de Django.

    Tasa configurable (DS-50): si REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] tiene una entrada
    para el scope, manda esa; si no, default_rate. Hoy no se toca settings.py (archivo
    compartido): los valores por defecto viven aqui, como en el lote 3 (DS-39), y se unifican
    despues con el lote 3 y la rama HU-46 agregando las entradas en settings.
    '''
    default_rate = None

    def get_rate(self):
        return api_settings.DEFAULT_THROTTLE_RATES.get(self.scope) or self.default_rate

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class WebInterestBurstThrottle(IPRateThrottle):
    scope = 'opportunities_interest_burst'
    default_rate = '3/minute'


class WebInterestDailyThrottle(IPRateThrottle):
    scope = 'opportunities_interest_daily'
    default_rate = '10/day'


class WhatsAppContactThrottle(IPRateThrottle):
    # Frena la recoleccion masiva de telefonos de asesores (DT-117).
    scope = 'opportunities_whatsapp'
    default_rate = '30/minute'


def public_property_or_404(property_id):
    property_obj = (eligible_properties().select_related('agent')
                    .filter(pk=property_id).first())
    if property_obj is None:
        raise Http404
    return property_obj


class PropertyWhatsAppView(APIView):
    '''
    HU-15 (P-07, RF-02, DS-50): numero del asesor captador para el enlace wa.me.

    GET /api/opportunities/public/properties/<id>/whatsapp/   (publico; 30/min por IP)
    -> 200 {"property": id, "whatsapp_phone": "5939XXXXXXXX" | null}
       null: asesor inactivo o telefono que no es un celular de Ecuador valido (DS-28); el
       frontend oculta el boton. El mensaje (titulo e id de la propiedad) lo arma el frontend.
    -> 404 propiedad inexistente o no Disponible.
    Sin registro en el backend: simplificacion aprobada frente a RF-02 (DS-50).
    '''
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [WhatsAppContactThrottle]

    def get(self, request, property_id):
        property_obj = public_property_or_404(property_id)
        return Response({
            'property': property_obj.pk,
            'whatsapp_phone': agent_whatsapp_number(property_obj),
        })


# Mismo texto exista o no el contacto u oportunidad: no revela datos de otros clientes.
INTEREST_OK_MESSAGE = 'Tu interés quedó registrado. Un asesor se comunicará contigo.'


class PropertyInterestView(APIView):
    '''
    HU-16 (P-07, RF-03, DS-50): el visitante sin cuenta registra su interes.

    POST /api/opportunities/public/properties/<id>/interest/   (publico; 3/min y 10/dia por IP)
    {"full_name", "phone", "email", "email_opt_in", "message", "privacy_accepted"}
    -> 201 {"detail"}: siempre el mismo, sin ids ni datos del asesor o de otros clientes.
    -> 400 datos invalidos (celular DS-28, LOPDP, correo, largo del mensaje).
    -> 404 propiedad inexistente, no Disponible o sin asesor captador activo.
    '''
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [WebInterestBurstThrottle, WebInterestDailyThrottle]

    def post(self, request, property_id):
        property_obj = public_property_or_404(property_id)
        serializer = WebInterestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            register_web_interest(
                property_obj=property_obj, full_name=data.get('full_name'),
                phone=data.get('phone'), email=data.get('email'),
                email_opt_in=data['email_opt_in'], message=data.get('message'),
                privacy_accepted=data['privacy_accepted'],
            )
        except DjangoValidationError as error:
            raise to_drf_error(error)
        except InterestNotAccepted:
            raise Http404
        return Response({'detail': INTEREST_OK_MESSAGE}, status=status.HTTP_201_CREATED)
