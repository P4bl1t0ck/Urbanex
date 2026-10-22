from django.http import FileResponse
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer


class DocumentViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    '''
    Expediente digital (HU-03). Sin update ni delete: los documentos son inmutables
    y un reemplazo se sube como nueva version con POST.

    GET  /api/documents/?property=<id>[&all_versions=1]  -> versiones vigentes (o todas)
    POST /api/documents/                                  -> multipart: property, doc_type, file,
                                                             issue_date, expiration_date, is_critical
    GET  /api/documents/<uuid>/                           -> metadatos
    GET  /api/documents/<uuid>/file/                      -> descarga protegida por permisos
    '''
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        queryset = Document.objects.select_related('uploaded_by', 'property')
        # Permiso por objeto: el asesor nunca ve expedientes ajenos (RNF-04).
        if user.role != 'admin':
            queryset = queryset.filter(property__agent=user)

        property_id = self.request.query_params.get('property')
        if property_id:
            if not property_id.isdigit():
                return queryset.none()
            queryset = queryset.filter(property_id=property_id)
        if self.request.query_params.get('all_versions') != '1':
            queryset = queryset.filter(is_current_version=True)
        return queryset

    def get_serializer_class(self):
        return DocumentUploadSerializer if self.action == 'create' else DocumentSerializer

    @action(detail=True, methods=['get'])
    def file(self, request, pk=None):
        # Provisional hasta las URLs firmadas de Supabase Storage (HU-38, Sprint 6).
        document = self.get_object()
        return FileResponse(
            document.file.open('rb'),
            as_attachment=True,
            filename=document.original_filename,
            content_type=document.mime_type,
        )
