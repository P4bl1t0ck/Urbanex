import math
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext

from .factors import FACTOR_STEP, ONE, clamp, get_factor

'''
Motor de avaluos, capa 1 (DS-21): metodo comparativo de mercado, determinista (HU-06).

Funciones puras, sin acceso a la base de datos: reciben el sujeto, los comparables
confirmados por el asesor y theta, y devuelven el resultado con su traza completa.
Todo el calculo usa Decimal con redondeos fijos (factores a 6 decimales, montos a 2,
CV a 4) y un contexto propio, asi que el mismo snapshot con el mismo theta da siempre
el mismo resultado.
'''

ENGINE_ID = 'DS-21'
MIN_COMPARABLES = 3  # HU-04, SB-2020-0573 Anexo 1 num. 2.2.4, Norma Tecnica DMQ
MAX_COMPARABLES = 5  # HU-04

CENTS = Decimal('0.01')
CV_STEP = Decimal('0.0001')
HUNDRED = Decimal('100')

CONFIDENCE_HIGH = 'ALTO'
CONFIDENCE_MEDIUM = 'MEDIO'
CONFIDENCE_LOW = 'BAJO'

REQUIRED_PARAMS = (
    'factores_por_tipo', 'factor_total_min', 'factor_total_max', 'desvio_max', 'alfa',
    'cv_max', 'estados_comparables', 'antiguedad_max_dias', 'radio_km_sin_zona',
)
DEFAULT_TYPE = 'default'


class EngineError(ValueError):
    '''Entrada que el motor rechaza (no es un caso de registro manual).'''


@dataclass(frozen=True)
class Sample:
    '''Sujeto o comparable, ya convertido a Decimal (area_m2 es Float en Property).'''
    id: int
    property_type: str
    status: str
    price: Decimal
    area: Decimal
    latitude: Decimal = None
    longitude: Decimal = None

    @classmethod
    def from_property(cls, property_obj):
        return cls(
            id=property_obj.id,
            property_type=property_obj.property_type,
            status=property_obj.status,
            price=Decimal(property_obj.price),
            area=Decimal(str(property_obj.area_m2)),
            latitude=property_obj.latitude,
            longitude=property_obj.longitude,
        )

    def has_coordinates(self):
        return self.latitude is not None and self.longitude is not None


@dataclass(frozen=True)
class EngineResult:
    suggested_value: Decimal
    confidence_level: str
    is_manual_fallback: bool
    snapshot: dict


def money(value):
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def round_to_hundreds(value):
    '''Valor mostrado en la interfaz (ajuste de Pablo); el guardado es exacto.'''
    return (value / HUNDRED).quantize(ONE, rounding=ROUND_HALF_UP) * HUNDRED


# ---------- Validacion de theta ----------

def validate_params(params):
    '''Lanza ValueError si theta no es valido. La usa EngineParameters.clean().'''
    if not isinstance(params, dict):
        raise ValueError('theta debe ser un objeto JSON.')
    missing = [name for name in REQUIRED_PARAMS if name not in params]
    if missing:
        raise ValueError(f'Faltan parametros: {", ".join(missing)}.')

    by_type = params['factores_por_tipo']
    if not isinstance(by_type, dict) or DEFAULT_TYPE not in by_type:
        raise ValueError('factores_por_tipo debe tener una entrada "default".')
    for property_type, factors in by_type.items():
        if not isinstance(factors, dict):
            raise ValueError(f'factores_por_tipo.{property_type} debe ser un objeto.')
        for key, factor_params in factors.items():
            get_factor(key).validate_params(factor_params)

    low, high = Decimal(str(params['factor_total_min'])), Decimal(str(params['factor_total_max']))
    if not Decimal('0') < low <= ONE <= high:
        raise ValueError('Se requiere 0 < factor_total_min <= 1 <= factor_total_max.')
    if Decimal(str(params['desvio_max'])) <= 0:
        raise ValueError('desvio_max debe ser mayor que 0.')
    if Decimal(str(params['alfa'])) < 0:
        raise ValueError('alfa no puede ser negativo.')
    if not Decimal('0') < Decimal(str(params['cv_max'])) < ONE:
        raise ValueError('cv_max debe estar entre 0 y 1.')
    if not params['estados_comparables'] or 'captacion' in params['estados_comparables']:
        raise ValueError('estados_comparables no puede estar vacio ni incluir captacion.')
    if int(params['antiguedad_max_dias']) <= 0 or Decimal(str(params['radio_km_sin_zona'])) <= 0:
        raise ValueError('antiguedad_max_dias y radio_km_sin_zona deben ser positivos.')


def factors_for_type(params, property_type):
    by_type = params['factores_por_tipo']
    return by_type.get(property_type, by_type[DEFAULT_TYPE])


# ---------- Zona y orden de candidatos (HU-04) ----------

def distance_km(first, second):
    '''Haversine. Solo filtra y ordena; no interviene en el valor.'''
    lat1, lon1 = math.radians(float(first.latitude)), math.radians(float(first.longitude))
    lat2, lon2 = math.radians(float(second.latitude)), math.radians(float(second.longitude))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def same_zone(subject, comparable, params):
    '''
    Provisional mientras no exista Property.zone (DS-21 §7, opcion 2): misma zona =
    distancia <= radio_km_sin_zona. Cuando exista zone, solo cambia esta funcion.
    '''
    if not (subject.has_coordinates() and comparable.has_coordinates()):
        return False
    return distance_km(subject, comparable) <= float(params['radio_km_sin_zona'])


def rank_key(subject, comparable):
    '''Orden determinista: superficie mas parecida, luego distancia, luego id.'''
    with localcontext() as ctx:
        ctx.prec = 28
        size_gap = abs((comparable.area / subject.area).ln())
    distance = (distance_km(subject, comparable)
                if subject.has_coordinates() and comparable.has_coordinates() else math.inf)
    return (size_gap, distance, comparable.id)


# ---------- Calculo (HU-06) ----------

def _sample_snapshot(sample):
    return {
        'id': sample.id,
        'property_type': sample.property_type,
        'status': sample.status,
        'price': str(sample.price),
        'area_m2': str(sample.area),
    }


def _manual(subject, comparables, params_version, reason):
    return EngineResult(
        suggested_value=None,
        confidence_level=CONFIDENCE_LOW,
        is_manual_fallback=True,
        snapshot={
            'engine': ENGINE_ID,
            'parameters_version': params_version,
            'subject': _sample_snapshot(subject),
            'manual_reason': reason,
            # Con 1-2 comparables se guardan como referencia para el asesor (C-02, opcion A).
            'comparables': [
                dict(_sample_snapshot(c), unit_price=str(money(c.price / c.area)))
                for c in comparables
            ],
        },
    )


def compute(subject, comparables, params, params_version=None):
    '''
    Aplica la capa 1 de DS-21 sobre los comparables confirmados por el asesor.
    - Menos de 3 comparables: registro manual (C-02, opcion A, provisional).
    - Mas de 5, de otro tipo o el propio sujeto: EngineError.
    '''
    if subject.area <= 0:
        raise EngineError('La propiedad no tiene una superficie válida para calcular.')
    ids = [c.id for c in comparables]
    if len(ids) != len(set(ids)) or subject.id in ids:
        raise EngineError('Los comparables no pueden repetirse ni incluir la propia propiedad.')
    if len(comparables) > MAX_COMPARABLES:
        raise EngineError(f'Se permiten como máximo {MAX_COMPARABLES} comparables.')
    if any(c.property_type != subject.property_type for c in comparables):
        raise EngineError('Los comparables deben ser del mismo tipo de propiedad.')
    if any(c.price <= 0 or c.area <= 0 for c in comparables):
        raise EngineError('Todos los comparables deben tener precio y superficie mayores que 0.')

    if len(comparables) < MIN_COMPARABLES:
        return _manual(subject, comparables, params_version,
                       f'Menos de {MIN_COMPARABLES} comparables (C-02, opción A).')

    with localcontext() as ctx:
        ctx.prec = 28
        ctx.rounding = ROUND_HALF_UP
        return _compute(subject, comparables, params, params_version)


def _compute(subject, comparables, params, params_version):
    total_low = Decimal(str(params['factor_total_min']))
    total_high = Decimal(str(params['factor_total_max']))
    alpha = Decimal(str(params['alfa']))
    max_deviation = Decimal(str(params['desvio_max']))
    cv_max = Decimal(str(params['cv_max']))
    active_factors = factors_for_type(params, subject.property_type)

    rows = []
    for comparable in sorted(comparables, key=lambda c: c.id):
        unit_price = money(comparable.price / comparable.area)
        factors, product, gross = [], ONE, Decimal('0')
        for key in sorted(active_factors):
            result = get_factor(key).compute(subject, comparable, active_factors[key])
            factors.append({'key': key, 'value': str(result.value), 'detail': result.detail})
            product *= result.value
            gross += abs(result.value - ONE)
        total = clamp(product, total_low, total_high).quantize(FACTOR_STEP)
        gross = gross.quantize(FACTOR_STEP)
        rows.append({
            'sample': comparable,
            'unit_price': unit_price,
            'factors': factors,
            'total_factor': total,
            'adjusted_unit_price': money(unit_price * total),
            'gross_adjustment': gross,
            'weight': (ONE / (ONE + alpha * gross)).quantize(FACTOR_STEP),
            'deviation': None,
            'discarded': False,
        })

    median = _median([row['adjusted_unit_price'] for row in rows])
    for row in rows:
        row['deviation'] = (abs(row['adjusted_unit_price'] - median) / median).quantize(CV_STEP)

    # Atipicos (Norma Tecnica DMQ): solo con 4 o mas; nunca se baja de 3.
    if len(rows) > MIN_COMPARABLES:
        for row in sorted(rows, key=lambda r: (-r['deviation'], r['sample'].id)):
            kept = sum(1 for r in rows if not r['discarded'])
            if kept <= MIN_COMPARABLES or row['deviation'] <= max_deviation:
                break
            row['discarded'] = True

    kept_rows = [row for row in rows if not row['discarded']]
    weight_sum = sum(row['weight'] for row in kept_rows)
    weighted_unit_price = money(
        sum(row['weight'] * row['adjusted_unit_price'] for row in kept_rows) / weight_sum
    )
    suggested_value = money(weighted_unit_price * subject.area)

    values = [row['adjusted_unit_price'] for row in kept_rows]
    mean = sum(values) / len(values)
    std = (sum((v - mean) ** 2 for v in values) / (len(values) - 1)).sqrt()
    cv = (std / mean).quantize(CV_STEP)
    confidence = CONFIDENCE_HIGH if cv <= cv_max else CONFIDENCE_MEDIUM

    return EngineResult(
        suggested_value=suggested_value,
        confidence_level=confidence,
        is_manual_fallback=False,
        snapshot={
            'engine': ENGINE_ID,
            'parameters_version': params_version,
            'subject': _sample_snapshot(subject),
            'comparables': [
                dict(
                    _sample_snapshot(row['sample']),
                    unit_price=str(row['unit_price']),
                    factors=row['factors'],
                    total_factor=str(row['total_factor']),
                    adjusted_unit_price=str(row['adjusted_unit_price']),
                    gross_adjustment=str(row['gross_adjustment']),
                    weight=str(row['weight']),
                    deviation=str(row['deviation']),
                    discarded=row['discarded'],
                )
                for row in rows
            ],
            'median_unit_price': str(median),
            'weighted_unit_price': str(weighted_unit_price),
            'mean_unit_price': str(money(mean)),
            'std_unit_price': str(money(std)),
            'cv': str(cv),
            'confidence_level': confidence,
            'suggested_value': str(suggested_value),
            'display_value': str(round_to_hundreds(suggested_value)),
        },
    )


def _median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2
