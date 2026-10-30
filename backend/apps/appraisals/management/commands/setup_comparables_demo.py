from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.users.models import Property

'''
Comparables sinteticos para desarrollo (DS-23, fase 3 del motor DS-21).

- Solo corre con DEBUG=True. Son datos de mercado inventados, no propiedades reales.
- Excepcion acotada a DS-17: se crean directamente en 'vendido' (no pasan por HU-53) porque
  representan transacciones de mercado. 'vendido' no es un estado publico, asi que no salen
  en el catalogo; tampoco tienen asesor, asi que no aparecen en "Mis propiedades".
- Rodean a las propiedades de setup_demo_data para cubrir los casos del contexto maestro:
  3+ comparables con baja dispersion, dispersion alta, 1-2 comparables y ninguno.
- Es idempotente: identifica cada comparable por su titulo.
'''

PREFIX = '[COMP-SINT]'
DESCRIPTION = 'Dato de mercado sintético para desarrollo (DS-23). No es una propiedad real.'

# escenario -> (ubicacion, [(titulo, tipo, precio, m2, dormitorios, banos, lat, lon)]).
# Los departamentos de La Carolina son los del ejemplo resuelto de DS-21 §8 (el 5 es el
# atipico) mas uno extra, para que el asesor tenga que elegir 5 de 6.
SCENARIOS = {
    'La Carolina (departamento, 6 comparables, confianza ALTA)': ('La Carolina, Quito', [
        ('Departamento vendido La Carolina 1', 'departamento', '150000', 100, 2, 2, '-0.184000', '-78.482000'),
        ('Departamento vendido La Carolina 2', 'departamento', '128000', 80, 2, 1, '-0.187500', '-78.485500'),
        ('Departamento vendido La Carolina 3', 'departamento', '168000', 120, 3, 2, '-0.183200', '-78.486100'),
        ('Departamento vendido La Carolina 4', 'departamento', '139500', 90, 2, 2, '-0.188900', '-78.481300'),
        ('Departamento vendido La Carolina 5 (atipico)', 'departamento', '92000', 90, 2, 1, '-0.186400', '-78.479800'),
        ('Departamento vendido La Carolina 6', 'departamento', '142000', 95, 2, 2, '-0.182600', '-78.483900'),
    ]),
    'Cumbayá (casa, 3 comparables dispersos, confianza MEDIA)': ('Cumbayá, Quito', [
        ('Casa vendida Cumbaya 1', 'casa', '310000', 260, 4, 3, '-0.198800', '-78.430100'),
        ('Casa vendida Cumbaya 2', 'casa', '290000', 230, 4, 3, '-0.202900', '-78.433400'),
        ('Casa vendida Cumbaya 3', 'casa', '205000', 250, 3, 2, '-0.199700', '-78.434200'),
    ]),
    'La Mariscal (local, 2 comparables, avalúo manual por C-02)': ('La Mariscal, Quito', [
        ('Local vendido La Mariscal 1', 'local', '115000', 75, 0, 1, '-0.204800', '-78.490600'),
        ('Local vendido La Mariscal 2', 'local', '128000', 90, 0, 1, '-0.201900', '-78.493500'),
    ]),
    'Tumbaco (terreno, sin comparables, avalúo manual)': ('Tumbaco, Quito', []),
}


class Command(BaseCommand):
    help = 'Crea comparables sinteticos en estado vendido para probar el motor (solo desarrollo, DS-23).'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('setup_comparables_demo solo se ejecuta en desarrollo (DEBUG=True).')

        created = 0
        with transaction.atomic():
            for location, rows in SCENARIOS.values():
                for title, property_type, price, area, bedrooms, bathrooms, lat, lon in rows:
                    _, was_created = Property.objects.get_or_create(
                        title=f'{PREFIX} {title}',
                        agent=None,
                        defaults={
                            'description': DESCRIPTION,
                            'property_type': property_type,
                            'status': 'vendido',
                            'price': Decimal(price),
                            'area_m2': float(area),
                            'bedrooms': bedrooms,
                            'bathrooms': bathrooms,
                            'location': location,
                            'latitude': Decimal(lat),
                            'longitude': Decimal(lon),
                        },
                    )
                    created += was_created

        self.stdout.write(self.style.SUCCESS(f'Comparables sintéticos listos ({created} nuevos).'))
        for scenario, (_, rows) in SCENARIOS.items():
            self.stdout.write(f'  {scenario}: {len(rows)} en "vendido".')
