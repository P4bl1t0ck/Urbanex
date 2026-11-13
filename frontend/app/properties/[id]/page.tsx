import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { cache } from "react";
import FreeSlotsPicker from "@/components/FreeSlotsPicker";
import InterestForm from "@/components/InterestForm";
import SiteNav from "@/components/SiteNav";
import WhatsAppContactButton from "@/components/WhatsAppContactButton";
import { getPropertyById } from "@/lib/api";
import {
  buildPropertyMetadata,
  UNAVAILABLE_PROPERTY_METADATA,
} from "@/lib/propertyMetadata";

// Una sola consulta a la API por petición, compartida por generateMetadata y la página.
const getProperty = cache(getPropertyById);

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

type PropertyDetailParams = { params: Promise<{ id: string }> };

// HU-12 / URB-17: metaetiquetas para compartir la ficha. La API devuelve 404 a
// las fichas no públicas sin sesión; buildPropertyMetadata lo vuelve a comprobar.
export async function generateMetadata({
  params,
}: PropertyDetailParams): Promise<Metadata> {
  const { id } = await params;
  const metadataBase = new URL(SITE_URL);

  try {
    return { metadataBase, ...buildPropertyMetadata(await getProperty(id)) };
  } catch {
    return { metadataBase, ...UNAVAILABLE_PROPERTY_METADATA };
  }
}

export default async function PropertyDetailPage({
  params,
}: PropertyDetailParams) {
  const { id } = await params;
  let property: Awaited<ReturnType<typeof getPropertyById>>;

  try {
    property = await getProperty(id);
  } catch {
    return (
      <>
        
        <main className="mx-auto flex min-h-screen max-w-7xl flex-col items-center justify-center px-4 text-center">
          <h1 className="text-2xl font-bold text-slate-900">
            No se pudo cargar esta propiedad
          </h1>
          <p className="mt-2 text-slate-600">
            Verifica la conexión con el servidor e intenta nuevamente.
          </p>
          <Link
            href="/properties"
            className="mt-6 rounded-lg bg-blue-700 px-4 py-2 font-semibold text-white hover:bg-blue-800"
          >
            Volver al catálogo
          </Link>
        </main>
      </>
    );
  }

  const mainImage = property.images?.[0]?.image;

  return (
    <>
      <SiteNav />
      <main className="min-h-screen bg-white px-4 py-8 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-6">
            <Link
              href="/properties"
              className="font-medium text-blue-700 hover:text-blue-900"
            >
              &larr; Volver al catálogo
            </Link>
          </div>

          <div className="grid grid-cols-1 gap-10 lg:grid-cols-2 lg:gap-12">
            <div className="relative h-[400px] w-full overflow-hidden rounded-2xl bg-slate-100 shadow-lg lg:h-[500px]">
              {mainImage ? (
                <Image
                  src={mainImage}
                  alt={property.title}
                  fill
                  className="object-cover"
                  unoptimized
                />
              ) : (
                <div className="flex h-full items-center justify-center text-slate-500">
                  Imagen no disponible
                </div>
              )}
            </div>

            <div className="flex flex-col justify-center">
              <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">
                {property.property_type}
              </p>
              <h1 className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
                {property.title}
              </h1>
              <p className="mt-2 text-lg text-slate-600">{property.location}</p>

              <p className="mt-6 text-3xl font-bold text-blue-800">
                {Number(property.price).toLocaleString("es-EC", {
                  style: "currency",
                  currency: "USD",
                })}
              </p>

              {/* HU-15 (P-07, DS-50): se oculta solo si el asesor no tiene celular válido. */}
              {property.status === "disponible" && (
                <WhatsAppContactButton propertyId={property.id} title={property.title} />
              )}

              <section className="mt-8 rounded-xl border border-slate-200 bg-slate-50 p-6">
                <h2 className="text-xl font-bold text-slate-900">
                  Características principales
                </h2>
                <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                  <div className="rounded-lg bg-white p-3">
                    <p className="text-xl font-bold text-slate-900">
                      {property.bedrooms}
                    </p>
                    <p className="text-xs text-slate-600">Habitaciones</p>
                  </div>
                  <div className="rounded-lg bg-white p-3">
                    <p className="text-xl font-bold text-slate-900">
                      {property.bathrooms}
                    </p>
                    <p className="text-xs text-slate-600">Baños</p>
                  </div>
                  <div className="rounded-lg bg-white p-3">
                    <p className="text-xl font-bold text-slate-900">
                      {property.area_m2}
                    </p>
                    <p className="text-xs text-slate-600">Metros²</p>
                  </div>
                </div>
              </section>

              <section className="mt-8">
                <h2 className="text-xl font-bold text-slate-900">
                  Descripción
                </h2>
                <p className="mt-3 whitespace-pre-line leading-relaxed text-slate-600">
                  {property.description}
                </p>
              </section>

              {/* HU-16 (P-07, DS-50): formulario de interés; solo en propiedades Disponibles. */}
              {property.status === "disponible" && <InterestForm propertyId={property.id} />}

              {/* HU-18 (P-07): franjas libres; solo en propiedades publicadas (Disponible). */}
              {property.status === "disponible" && (
                <FreeSlotsPicker propertyId={property.id} />
              )}
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
