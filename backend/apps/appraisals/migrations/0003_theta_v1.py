from django.db import migrations

'''
Theta v1 del motor (DS-21 §5.1), aprobado por Pablo el 2026-10-28 como provisional.
Se copia aqui (y no se importa de engine/theta.py) para que la migracion produzca siempre
los mismos datos aunque el codigo cambie despues.
'''

THETA_V1 = {
    'factores_por_tipo': {
        'default': {
            'superficie@1': {'a': '0.25', 'b': '0.75', 'min': '0.75', 'max': '1.20', 'intensidad': '1'},
            'negociacion@1': {'factor_oferta': '1.00'},
        },
    },
    'factor_total_min': '0.85',
    'factor_total_max': '1.20',
    'desvio_max': '0.30',
    'alfa': '5',
    'cv_max': '0.15',
    'estados_comparables': ['disponible', 'reservador', 'vendido'],
    'antiguedad_max_dias': 365,
    'radio_km_sin_zona': '1.5',
}

SOURCES_V1 = {
    'superficie@1': 'Norma Tecnica de Valoracion DMQ 2025 (F5, POR CONFIRMAR); intensidad: ajuste de Pablo',
    'negociacion@1.factor_oferta': 'Sin fuente: neutro hasta tenerla',
    'factor_total_min/max': 'Codigo Municipal DMQ art. III.5.15 (F3), por analogia',
    'desvio_max': 'Diseno propio; la Norma Tecnica DMQ pide excluir atipicos sin fijar la regla',
    'alfa': 'Diseno propio; con 0 se obtiene el promedio de la Norma Tecnica DMQ',
    'cv_max': 'Norma Tecnica DMQ 2025 (F5, POR CONFIRMAR)',
    'estados_comparables': 'N-02, decision de Pablo (DS-21)',
    'antiguedad_max_dias': 'Diseno propio; SB-2020-0573 solo dice "recientemente"',
    'radio_km_sin_zona': 'Diseno propio, provisional hasta Property.zone (N-03)',
}


def create_theta_v1(apps, schema_editor):
    EngineParameters = apps.get_model('appraisals', 'EngineParameters')
    if not EngineParameters.objects.filter(version=1).exists():
        EngineParameters.objects.create(
            version=1,
            parameters=THETA_V1,
            sources=SOURCES_V1,
            note='Theta v1 de DS-21, aprobado como provisional (EN OBSERVACION) el 2026-10-28.',
            is_active=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('appraisals', '0002_engine_parameters'),
    ]

    operations = [
        # Sin reversa de datos: las versiones de theta no se eliminan.
        migrations.RunPython(create_theta_v1, migrations.RunPython.noop),
    ]
