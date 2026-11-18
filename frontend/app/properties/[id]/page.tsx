import type { Metadata } from "next";
import Link from "next/link";
import { cache } from "react";
import { notFound } from "next/navigation";
import PropertyLocationMap from "@/components/PropertyLocationMap";
import PropertyGallery from "@/components/PropertyGallery";
import PropertyActions from "@/components/PropertyActions";
import PropertyCard from "@/components/PropertyCard";
import { principalFeatures, similarProperties } from "@/lib/propertyDetail";
import { ApiError, getProperties, getPropertyById } from "@/lib/api";
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
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
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


  const typeLabel = {
    casa: "Casa", departamento: "Departamento", local: "Local comercial", terreno: "Terreno",
  }[property.property_type];
  const features = principalFeatures(property);
  let related: typeof property[] = [];
  try {
    const candidates = await getProperties({ property_type: property.property_type });
    related = similarProperties(property, candidates.results);
  } catch {
    // Una búsqueda relacionada fallida no impide consultar la ficha principal.
  }

  return (
    <>
      <main className="min-h-screen bg-white px-4 py-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="mb-4">
            <Link
              href="/properties"
              className="inline-flex items-center py-1 text-sm font-medium text-blue-700 hover:text-blue-900 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
            >
              &larr; Volver al catálogo
            </Link>
          </div>

          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,0.85fr)] lg:gap-10">
            <div className="order-2 min-w-0 py-2 lg:py-4">
              <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                {typeLabel}
              </p>
              <h1 className="mt-2 text-3xl font-extrabold text-slate-900 sm:text-4xl">
                {property.title}
              </h1>
              <p className="mt-1 text-base text-slate-600">{property.location}</p>

              <p className="mt-4 text-sm font-medium text-slate-600">{property.operation_type === "arriendo" ? "Alquiler mensual · USD" : "Precio de venta · USD"}</p>
              <p className="mt-1 text-3xl font-bold text-blue-800">
                {Number(property.price).toLocaleString("es-EC", {
                  style: "currency",
                  currency: "USD",
                })}
                {property.operation_type === "arriendo" && <span className="ml-1 text-base font-medium text-slate-500">/ mes</span>}
              </p>

              {features.length > 0 && <section aria-labelledby="principal-features" className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
                <h2 id="principal-features" className="text-center text-sm font-bold text-slate-900">Características principales</h2>
              <dl className={`mt-3 grid gap-2 ${features.length === 1 ? "grid-cols-1" : features.length === 3 ? "grid-cols-3" : features.length === 4 ? "grid-cols-2 sm:grid-cols-4" : "grid-cols-2"}`}>
                {features.map((feature) => (
                  <div key={feature.label} className="flex min-w-0 flex-col items-center justify-center rounded-lg bg-white px-2 py-3 text-center">
                    <dt className="order-2 mt-1 text-xs text-slate-500">{feature.label}</dt>
                    <dd className="order-1 text-lg font-bold text-slate-900">{feature.value}</dd>
                  </div>
                ))}
              </dl>
              </section>}
              <PropertyActions key={property.id} property={property} />
            </div>
            <div className="order-1 min-w-0">
              <PropertyGallery key={property.id} images={property.images ?? []}
                title={property.title} status={property.status} />
            </div>
          </div>

          <div className="mt-10 space-y-8 border-t border-slate-200 pt-8 pb-8">
              <section>
                <h2 className="text-xl font-bold text-slate-900">
                  Descripción
                </h2>
                <p className="mt-3 whitespace-pre-line leading-relaxed text-slate-600">
                  {property.description || "Descripción no disponible."}
                </p>
              </section>

              <PropertyLocationMap key={property.id} propertyId={property.id} latitude={property.latitude}
                longitude={property.longitude} title={property.title} location={property.location} />

              {related.length > 0 && <section aria-labelledby="similar-properties">
                <h2 id="similar-properties" className="text-xl font-bold text-slate-900">{typeLabel === "Casa" ? "Casas" : typeLabel === "Departamento" ? "Departamentos" : typeLabel === "Terreno" ? "Terrenos" : "Locales"} similares</h2>
                <div className="mt-5 flex snap-x snap-proximity gap-5 overflow-x-auto pb-4" aria-label="Propiedades similares">
                  {related.map((candidate) => <div key={candidate.id} className="w-[min(82vw,300px)] shrink-0 snap-start">
                    <PropertyCard property={candidate} />
                  </div>)}
                </div>
              </section>}
          </div>
        </div>
        <div aria-hidden="true" className="h-[calc(8rem+env(safe-area-inset-bottom))] sm:h-[calc(6rem+env(safe-area-inset-bottom))]" />
      </main>
    </>
  );
}
