from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Appraisal
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
    POST  /api/appraisals/                    -> {property}; crea un borrador
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

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        appraisal = self.get_object()
        try:
            appraisal.approve()
        except DjangoValidationError as error:
            raise to_drf_error(error)
        return Response(AppraisalSerializer(appraisal, context={'request': request}).data,
                        status=status.HTTP_200_OK)
