from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='DailyMapLoads',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('screen', models.CharField(choices=[('detail', 'Ficha')], max_length=16)),
                ('provider', models.CharField(default='leaflet', max_length=16)),
                ('loads', models.PositiveBigIntegerField(default=0)),
            ],
            options={'constraints': [models.UniqueConstraint(fields=('day', 'screen', 'provider'), name='unique_daily_map_loads')]},
        ),
    ]
