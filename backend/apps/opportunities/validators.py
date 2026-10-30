import re

from django.core.exceptions import ValidationError

'''
Telefono valido (HU-27, DS-28): celular de Ecuador. Se acepta 09XXXXXXXX o +5939XXXXXXXX,
con espacios, guiones, puntos o parentesis, y se guarda siempre como +5939XXXXXXXX para que
Contact.phone sea unico sin importar como se escribio. Fijos y numeros extranjeros: no.
'''

_SEPARATORS = re.compile(r'[\s\-.()]')
_LOCAL_MOBILE = re.compile(r'09\d{8}')
_E164_MOBILE = re.compile(r'\+5939\d{8}')

INVALID_PHONE_MESSAGE = 'Ingrese un celular de Ecuador válido: 09XXXXXXXX o +5939XXXXXXXX.'


def normalize_phone(raw):
    value = _SEPARATORS.sub('', raw or '')
    if _LOCAL_MOBILE.fullmatch(value):
        return '+593' + value[1:]
    if _E164_MOBILE.fullmatch(value):
        return value
    raise ValidationError(INVALID_PHONE_MESSAGE, code='invalid_phone')


def validate_normalized_phone(value):
    # Invariante del modelo: lo guardado ya paso por normalize_phone().
    if not _E164_MOBILE.fullmatch(value or ''):
        raise ValidationError(INVALID_PHONE_MESSAGE, code='invalid_phone')
