from dataclasses import dataclass
from decimal import Decimal

'''
Factores de ajuste del motor (DS-21, capa 2).

Cada factor se registra por nombre y version ('superficie@1'). Cambiar una formula = registrar
una version nueva, para que los avaluos antiguos se puedan recalcular igual. Los parametros
de cada factor vienen de theta (capa 3); aqui no hay valores fijos de negocio.
'''

ONE = Decimal('1')
FACTOR_STEP = Decimal('0.000001')


@dataclass(frozen=True)
class FactorResult:
    value: Decimal
    detail: str


class Factor:
    key = ''
    param_names = ()

    def compute(self, subject, comparable, params):
        raise NotImplementedError

    def validate_params(self, params):
        missing = [name for name in self.param_names if name not in params]
        if missing:
            raise ValueError(f'{self.key}: faltan los parametros {", ".join(missing)}.')
        extra = set(params) - set(self.param_names)
        if extra:
            raise ValueError(f'{self.key}: parametros desconocidos {", ".join(sorted(extra))}.')


REGISTRY = {}


def register(factor_class):
    factor = factor_class()
    if factor.key in REGISTRY:
        raise ValueError(f'Factor duplicado: {factor.key}.')
    REGISTRY[factor.key] = factor
    return factor_class


def get_factor(key):
    try:
        return REGISTRY[key]
    except KeyError:
        raise ValueError(f'Factor no registrado: {key}.') from None


def clamp(value, low, high):
    return min(max(value, low), high)


@register
class AreaFactor(Factor):
    '''
    Factor tamano de la Norma Tecnica de Valoracion DMQ 2025 (F5 en DS-21):
    Fta = a * S_sujeto / S_comparable + b, acotado a [min, max]; f = (1 / Fta) ^ intensidad.
    El sujeto hace de "lote tipo". La intensidad (0..1) permite suavizar o anular el factor
    por tipo de propiedad sin cambiar codigo.
    '''
    key = 'superficie@1'
    param_names = ('a', 'b', 'min', 'max', 'intensidad')

    def validate_params(self, params):
        super().validate_params(params)
        values = {name: Decimal(str(params[name])) for name in self.param_names}
        if not values['min'] <= values['max'] or values['min'] <= 0:
            raise ValueError(f'{self.key}: se requiere 0 < min <= max.')
        if not Decimal('0') <= values['intensidad'] <= ONE:
            raise ValueError(f'{self.key}: la intensidad debe estar entre 0 y 1.')

    def compute(self, subject, comparable, params):
        a, b = Decimal(str(params['a'])), Decimal(str(params['b']))
        low, high = Decimal(str(params['min'])), Decimal(str(params['max']))
        intensity = Decimal(str(params['intensidad']))
        fta = clamp(a * subject.area / comparable.area + b, low, high)
        value = ((ONE / fta) ** intensity).quantize(FACTOR_STEP)
        return FactorResult(
            value,
            f'Superficie {comparable.area} m² frente a {subject.area} m²: '
            f'Fta = {fta.quantize(FACTOR_STEP)}, intensidad {intensity}.',
        )


@register
class NegotiationFactor(Factor):
    '''
    Precio de oferta frente a transaccion (F2 num. 2.2.4 y F5 en DS-21). Un comparable
    disponible o reservado es una oferta; uno vendido es una transaccion (factor 1).
    '''
    key = 'negociacion@1'
    param_names = ('factor_oferta',)
    OFFER_STATUSES = {'disponible', 'reservador'}

    def validate_params(self, params):
        super().validate_params(params)
        if Decimal(str(params['factor_oferta'])) <= 0:
            raise ValueError(f'{self.key}: factor_oferta debe ser mayor que 0.')

    def compute(self, subject, comparable, params):
        if comparable.status in self.OFFER_STATUSES:
            value = Decimal(str(params['factor_oferta'])).quantize(FACTOR_STEP)
            return FactorResult(value, f'Precio de oferta ({comparable.status}).')
        return FactorResult(ONE.quantize(FACTOR_STEP), f'Precio de transacción ({comparable.status}).')
