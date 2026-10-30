from datetime import timedelta

from django.utils import timezone

from apps.users.models import Property
from .engine import Sample, rank_key, same_zone
from .engine.calculator import MAX_COMPARABLES

'''
Seleccion de comparables (HU-04, DS-21 §3.2 paso 2). Une el motor puro con la base de datos:
mismo tipo, estados de theta, dato reciente, misma zona (radio provisional) y orden determinista.
La usan el endpoint de candidatos y Appraisal.create_draft(), que vuelve a validar los
comparables que envia el cliente.
'''


def subject_blocker(property_obj):
    '''Motivo por el que no se puede calcular (HU-05: datos minimos), o None.'''
    if not property_obj.area_m2 or property_obj.area_m2 <= 0:
        return 'La propiedad no tiene una superficie válida.'
    if property_obj.latitude is None or property_obj.longitude is None:
        return ('La propiedad no tiene coordenadas: márcalas en la pestaña Ubicación '
                '(mientras no exista la zona, DS-21 §7) o registra el avalúo manual.')
    return None


def find_candidates(property_obj, params, now=None):
    '''Lista de (Property, Sample) candidatos, ordenada como sugiere el motor.'''
    if subject_blocker(property_obj):
        return []
    now = now or timezone.now()
    subject = Sample.from_property(property_obj)
    queryset = (
        Property.objects
        .filter(
            property_type=property_obj.property_type,
            status__in=params['estados_comparables'],
            price__gt=0,
            area_m2__gt=0,
            latitude__isnull=False,
            longitude__isnull=False,
            # updated_at es la mejor aproximacion disponible a la fecha del dato (N-02).
            updated_at__gte=now - timedelta(days=int(params['antiguedad_max_dias'])),
        )
        .exclude(pk=property_obj.pk)
    )
    pairs = [(candidate, Sample.from_property(candidate)) for candidate in queryset]
    in_zone = [pair for pair in pairs if same_zone(subject, pair[1], params)]
    return sorted(in_zone, key=lambda pair: rank_key(subject, pair[1]))


def suggested_ids(candidates):
    return [candidate.id for candidate, _ in candidates[:MAX_COMPARABLES]]
