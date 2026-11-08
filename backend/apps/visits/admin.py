from django.contrib import admin

from .models import AgentAvailability, AvailabilityException, Visit


@admin.register(AgentAvailability)
class AgentAvailabilityAdmin(admin.ModelAdmin):
    # El admin puede editar la disponibilidad de cualquier asesor (RF-09); clean() aplica las reglas.
    list_display = ('agent', 'day_of_week', 'start_time', 'end_time', 'slot_duration_minutes')
    list_filter = ('day_of_week',)
    search_fields = ('agent__username', 'agent__first_name', 'agent__last_name')


@admin.register(AvailabilityException)
class AvailabilityExceptionAdmin(admin.ModelAdmin):
    list_display = ('agent', 'exception_date', 'start_time', 'end_time', 'reason')
    list_filter = ('exception_date',)
    search_fields = ('agent__username', 'agent__first_name', 'agent__last_name', 'reason')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    '''
    Lote 2 (demo de HU-18 y HU-24): el admin crea visitas a mano; clean() rechaza las que se
    cruzan con otra visita programada del asesor. No cambia el estado de la oportunidad (HU-19).
    '''
    list_display = ('id', 'property', 'agent', 'scheduled_start', 'scheduled_end', 'status',
                    'opportunity')
    list_filter = ('status',)
    search_fields = ('property__title', 'agent__username', 'opportunity__contact__full_name')
    raw_id_fields = ('opportunity', 'property', 'agent')
    readonly_fields = ('cancellation_token', 'created_at')
