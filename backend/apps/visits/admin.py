from django.contrib import admin

from .models import AgentAvailability, AvailabilityException


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
