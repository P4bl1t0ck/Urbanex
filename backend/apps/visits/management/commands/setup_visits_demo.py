from datetime import time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.opportunities.models import Opportunity
from apps.visits.models import AgentAvailability, Visit, Weekday, ecuador_today
from apps.visits.services import free_slots

'''
Visitas de ejemplo para la demo de HU-18 y HU-24 (lote 2; decision de Pablo, 2026-11-06).

- Solo corre con DEBUG=True, como los demas seeders: nunca contra Supabase.
- Toma las oportunidades en Contacto Inicial sobre propiedades Disponibles cuyo asesor
  responsable esta activo, y a cada una le programa UNA visita en la primera franja libre de
  los proximos 14 dias (free_slots: respeta reglas, excepciones, antelacion y otras visitas).
- NO cambia el estado de la oportunidad: llevarla a Visita Programada es de HU-19 (lote 3).
- Es idempotente: se salta las oportunidades que ya tienen una visita programada.
- --with-availability: al asesor sin disponibilidad le crea lunes a viernes de 09:00 a 13:00
  (visitas de 60 min) para que haya franjas. Sin la opcion, ese asesor se salta.
'''

DEMO_WEEKDAYS = (Weekday.LUNES, Weekday.MARTES, Weekday.MIERCOLES, Weekday.JUEVES,
                 Weekday.VIERNES)
DEMO_START = time(9)
DEMO_END = time(13)
DEMO_RANGE_DAYS = 14


class Command(BaseCommand):
    help = ('Programa visitas de ejemplo sobre oportunidades en Contacto Inicial, sin cambiar su '
            'estado (solo desarrollo; demo de HU-18 y HU-24).')

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-availability', action='store_true',
            help='Crea disponibilidad de lunes a viernes, 09:00-13:00, al asesor que no tenga.',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('setup_visits_demo solo se ejecuta en desarrollo (DEBUG=True).')

        opportunities = (
            Opportunity.objects
            .filter(status=Opportunity.Status.CONTACTO_INICIAL, property__status='disponible',
                    property__agent__is_active=True, property__agent__role='asesor')
            .select_related('property__agent', 'contact')
            .order_by('created_at', 'id')
        )
        today = ecuador_today()
        created = skipped = 0
        with transaction.atomic():
            for opportunity in opportunities:
                agent = opportunity.property.agent
                label = f'Oportunidad #{opportunity.pk} ({opportunity.property.title})'
                if opportunity.visits.filter(status=Visit.Status.PROGRAMADA).exists():
                    self.stdout.write(f'- {label}: ya tiene una visita programada.')
                    skipped += 1
                    continue
                if not agent.availability_rules.exists():
                    if not options['with_availability']:
                        self.stdout.write(f'- {label}: el asesor {agent} no tiene disponibilidad '
                                          '(use --with-availability).')
                        skipped += 1
                        continue
                    for weekday in DEMO_WEEKDAYS:
                        AgentAvailability.objects.create(
                            agent=agent, day_of_week=weekday, start_time=DEMO_START,
                            end_time=DEMO_END,
                        )
                    self.stdout.write(f'  Disponibilidad de demo creada para {agent}.')

                slots = free_slots(agent, today, today + timedelta(days=DEMO_RANGE_DAYS - 1))
                if not slots:
                    self.stdout.write(f'- {label}: el asesor no tiene franjas libres.')
                    skipped += 1
                    continue
                visit = Visit(
                    opportunity=opportunity, property=opportunity.property, agent=agent,
                    scheduled_start=slots[0].start, scheduled_end=slots[0].end,
                )
                visit.full_clean()
                visit.save()
                created += 1
                self.stdout.write(f'+ {label}: visita {slots[0].start:%Y-%m-%d %H:%M} '
                                  '(hora de Ecuador).')

        self.stdout.write(self.style.SUCCESS(
            f'Visitas creadas: {created}. Oportunidades omitidas: {skipped}. '
            'Las oportunidades siguen en Contacto Inicial (HU-19 las movera).'
        ))
