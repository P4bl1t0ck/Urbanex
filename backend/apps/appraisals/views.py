from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.documents.serializers import user_can_access_property
from apps.users.models import Property
from .engine import Sample
from .engine.calculator import MAX_COMPARABLES, MIN_COMPARABLES, distance_km, money
from .models import Appraisal, EngineParameters
from .services import find_candidates, subject_blocker, suggested_ids
from .serializers import (
    AppraisalCalibrateSerializer,
    AppraisalCreateSerializer,
    AppraisalSerializer,
    to_drf_error,
)


class AppraisalViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    '''
    Avaluos (RF-11, HU-08). Sin PUT ni DELETE: un avaluo aprobado es inmutable.

    GET   /api/appraisals/?property=<id>      -> historial de avaluos de la propiedad
    GET   /api/appraisals/candidates/?property=<id> -> comparables sugeridos (HU-04, I-11)
    POST  /api/appraisals/                    -> {property[, comparables]}; crea un borrador
                                                 (manual, o calculado por el motor, HU-06)
    GET   /api/appraisals/<uuid>/             -> detalle
    PATCH /api/appraisals/<uuid>/             -> {calibrated_value, final_justification}; solo borrador
    POST  /api/appraisals/<uuid>/approve/     -> congela el avaluo
    '''
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        queryset = Appraisal.objects.select_related('agent', 'property')
        # Permiso por objeto: el asesor solo ve avaluos de sus propiedades (RNF-04).
        if user.role != 'admin':
            queryset = queryset.filter(property__agent=user)

        property_id = self.request.query_params.get('property')
        if property_id:
            if not property_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(property_id=property_id)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return AppraisalCreateSerializer
        if self.action == 'partial_update':
            return AppraisalCalibrateSerializer
        return AppraisalSerializer

    # Limite de filas que se muestran en I-11; el asesor elige de 3 a 5.
    CANDIDATES_SHOWN = 20

    @action(detail=False, methods=['get'])
    def candidates(self, request):
        '''
        HU-04: candidatos del mismo tipo y zona para la propiedad (DS-21 §3.2). Muestra datos
        de mercado de la base interna (titulo, precio, superficie, estado), tambien de
        propiedades de otros asesores: es la fuente de comparables de RF-11.
        '''
        property_id = request.query_params.get('property', '')
        property_obj = (Property.objects.filter(pk=property_id).first()
                        if property_id.isdigit() else None)
        if property_obj is None or not user_can_access_property(request.user, property_obj):
            raise Http404

        parameters = EngineParameters.active()
        blocker = subject_blocker(property_obj)
        if parameters is None:
            blocker = 'No hay una versión activa de los parámetros del motor.'
        candidates = find_candidates(property_obj, parameters.parameters) if parameters else []
        subject = Sample.from_property(property_obj)
        rows = []
        for candidate, sample in candidates[:self.CANDIDATES_SHOWN]:
            rows.append({
                'id': candidate.id,
                'title': candidate.title,
                'property_type': candidate.property_type,
                'status': candidate.status,
                'location': candidate.location,
                'price': str(candidate.price),
                'area_m2': candidate.area_m2,
                'unit_price': str(money(sample.price / sample.area)),
                'distance_km': round(distance_km(subject, sample), 2),
            })
        if not blocker and len(candidates) < MIN_COMPARABLES:
            blocker = (f'Hay {len(candidates)} comparable(s) del mismo tipo y zona; se necesitan '
                       f'{MIN_COMPARABLES}. Registra el avalúo manual (C-02).')
        return Response({
            'property': {
                'id': property_obj.id,
                'title': property_obj.title,
                'property_type': property_obj.property_type,
                'price': str(property_obj.price),
                'area_m2': property_obj.area_m2,
                'has_coordinates': property_obj.latitude is not None
                and property_obj.longitude is not None,
            },
            'can_calculate': blocker is None,
            'blocker': blocker,
            'parameters_version': parameters.version if parameters else None,
            'min_comparables': MIN_COMPARABLES,
            'max_comparables': MAX_COMPARABLES,
            'candidates': rows,
            'suggested_ids': suggested_ids(candidates),
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        appraisal = self.get_object()
        try:
            appraisal.approve()
        except DjangoValidationError as error:
            raise to_drf_error(error)
        return Response(AppraisalSerializer(appraisal, context={'request': request}).data,
                        status=status.HTTP_200_OK)
