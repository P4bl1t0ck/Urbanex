from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('property', 'doc_type', 'version', 'is_current_version',
                    'validation_status', 'expiration_date', 'uploaded_by')
    list_filter = ('doc_type', 'validation_status', 'is_current_version', 'is_critical')
    search_fields = ('property__title', 'original_filename')

    # El expediente es inmutable: el admin de Django solo sirve para consultar.
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
