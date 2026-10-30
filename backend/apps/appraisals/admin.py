from django.contrib import admin, messages

from .models import Appraisal, EngineParameters


@admin.register(Appraisal)
class AppraisalAdmin(admin.ModelAdmin):
    list_display = ('folio', 'property', 'status', 'suggested_value', 'calibrated_value',
                    'difference_percentage', 'confidence_level', 'engine_parameters', 'agent',
                    'approved_at')
    list_filter = ('status', 'confidence_level', 'is_manual_fallback')
    search_fields = ('folio', 'property__title')

    # El avaluo es inmutable: el admin de Django solo sirve para auditar (A-05).
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def is_role_admin(request):
    return getattr(request.user, 'role', None) == 'admin'


@admin.register(EngineParameters)
class EngineParametersAdmin(admin.ModelAdmin):
    '''
    Theta del motor (DS-21). Una version guardada no se edita: "Agregar" crea la siguiente
    version (precargada con la activa) y la activa; la accion permite volver a una anterior.
    Solo el rol admin crea o activa versiones.
    '''
    list_display = ('version', 'is_active', 'created_by', 'created_at', 'note')
    actions = ['activate_selected']
    fields = ('parameters', 'sources', 'note')

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        return ('version', 'parameters', 'sources', 'note', 'created_by', 'created_at', 'is_active')

    def get_fields(self, request, obj=None):
        if obj is None:
            return self.fields
        return self.get_readonly_fields(request, obj)

    def get_changeform_initial_data(self, request):
        active = EngineParameters.active()
        if active is None:
            return {}
        return {'parameters': active.parameters, 'sources': active.sources}

    # El rol admin de la app no trae permisos de modelo de Django: sin esto, un admin que
    # no es superusuario no ve la app ni la lista (V-25). Se conservan los permisos normales.
    def has_module_permission(self, request):
        return is_role_admin(request) or super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return is_role_admin(request) or super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return is_role_admin(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:
            return
        created = EngineParameters.create_version(
            parameters=obj.parameters, sources=obj.sources, note=obj.note,
            created_by=request.user,
        )
        obj.pk, obj.version = created.pk, created.version

    @admin.action(description='Activar la versión seleccionada')
    def activate_selected(self, request, queryset):
        if not is_role_admin(request):
            self.message_user(request, 'Solo el rol admin activa versiones.', messages.ERROR)
            return
        if queryset.count() != 1:
            self.message_user(request, 'Selecciona exactamente una versión.', messages.ERROR)
            return
        version = queryset.first().activate()
        self.message_user(request, f'{version} activada.', messages.SUCCESS)
