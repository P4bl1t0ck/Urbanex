from django.db import models


class DailyMapLoads(models.Model):
    """Agregados anónimos; no son eventos facturados ni visitantes únicos."""

    day = models.DateField()
    screen = models.CharField(max_length=16, choices=[('detail', 'Ficha')])
    provider = models.CharField(max_length=16, default='leaflet')
    loads = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['day', 'screen', 'provider'], name='unique_daily_map_loads'),
        ]
