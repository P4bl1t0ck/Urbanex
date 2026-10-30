from django.contrib import admin

from .models import Contact, Opportunity, OpportunityStatusHistory


class ReadOnlyAdmin(admin.ModelAdmin):
    # Solo para consultar: altas y cambios van por los servicios de dominio y la API.
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Contact)
class ContactAdmin(ReadOnlyAdmin):
    list_display = ('full_name', 'phone', 'email', 'origin_channel', 'created_at')
    search_fields = ('full_name', 'phone', 'email')


@admin.register(Opportunity)
class OpportunityAdmin(ReadOnlyAdmin):
    list_display = ('id', 'contact', 'property', 'assigned_agent', 'status', 'origin_channel',
                    'created_at')
    list_filter = ('status', 'origin_channel')
    search_fields = ('contact__full_name', 'contact__phone', 'property__title')


@admin.register(OpportunityStatusHistory)
class OpportunityStatusHistoryAdmin(ReadOnlyAdmin):
    list_display = ('opportunity', 'previous_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status',)
