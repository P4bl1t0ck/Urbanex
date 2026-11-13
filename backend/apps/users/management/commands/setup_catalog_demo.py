from copy import deepcopy
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.users.management.commands.setup_demo_data import Command as DemoDataCommand, DEMO_PROPERTIES
from apps.users.models import Property
from apps.users.views import PropertyPublishView


class Command(BaseCommand):
    help = "Prepara propiedades de prueba para paginar HU-10, solo en SQLite local; no cambia usuarios."

    def add_arguments(self, parser):
        parser.add_argument("--agent-id", type=int, help="ID de un asesor activo ya existente.")
        parser.add_argument("--count", type=int, default=24, help="Total de ejemplos, entre 21 y 60.")

    def handle(self, *args, **options):
        if not settings.DEBUG or connection.vendor != "sqlite":
            raise CommandError("setup_catalog_demo requiere DEBUG=True y SQLite local.")
        count = options["count"]
        if not 21 <= count <= 60:
            raise CommandError("--count debe estar entre 21 y 60.")
        agents = get_user_model().objects.filter(role="asesor", is_active=True)
        if options["agent_id"] is not None:
            agents = agents.filter(pk=options["agent_id"])
        if agents.count() != 1:
            raise CommandError("Indica --agent-id de un asesor activo existente; no se crean usuarios.")
        agent = agents.get()
        helper = DemoDataCommand(stdout=self.stdout, stderr=self.stderr)
        factory = APIRequestFactory()
        created = skipped = 0
        with transaction.atomic():
            for index in range(1, count + 1):
                spec = deepcopy(DEMO_PROPERTIES[(index - 1) % len(DEMO_PROPERTIES)])
                spec.update(
                    title=f"[CAT-HU10] Ejemplo {index:02d}",
                    description="Datos ficticios para filtros y paginación de HU-10. Sin operación real.",
                    location="Sector DEMO HU10, Quito",
                    price=Decimal("80000") + Decimal(index * 5000),
                    area_m2=60 + index * 5,
                    bedrooms=index % 5,
                    bathrooms=index % 3 + 1,
                    requirements={"image", "brokerage_contract", "appraisal"},
                )
                # Los ejemplos existentes nunca se actualizan ni se vuelven a publicar.
                if Property.objects.filter(title=spec["title"], agent=agent).exists():
                    skipped += 1
                    continue
                # Nace en captación; reutiliza requisitos demo sin ejecutar su alta de usuarios.
                property_obj = helper._setup_property(spec, agent)
                request = factory.post(f"/api/auth/properties/{property_obj.pk}/publish/")
                force_authenticate(request, user=agent)
                response = PropertyPublishView.as_view()(request, pk=property_obj.pk)
                if response.status_code != 200:
                    raise CommandError(f"No se pudo publicar el ejemplo {index}; se revierte la transacción.")
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"Catálogo demo: {created} creadas/publicadas por HU-53; {skipped} existentes sin cambios."
        ))
        self.stdout.write("Busca ubicación 'DEMO HU10' para probar páginas de 20 resultados.")
        self.stdout.write("No se crean reservas, usuarios ni se cambian contraseñas o propiedades anteriores.")
