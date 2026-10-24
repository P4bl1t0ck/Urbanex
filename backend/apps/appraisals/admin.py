from django.contrib import admin

from .models import Appraisal


@admin.register(Appraisal)
class AppraisalAdmin(admin.ModelAdmin):
    list_display = ('folio', 'property', 'status', 'suggested_value', 'calibrated_value',
                    'difference_percentage', 'confidence_level', 'agent', 'approved_at')
    list_filter = ('status', 'confidence_level', 'is_manual_fallback')
    search_fields = ('folio', 'property__title')

    # El avaluo es inmutable: el admin de Django solo sirve para auditar (A-05).
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
