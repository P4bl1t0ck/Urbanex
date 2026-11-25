import type { Metadata } from "next";
import Link from "next/link";
import PropertyCard from "@/components/PropertyCard";
import CatalogFilters from "@/components/CatalogFilters";
import CatalogResultsHeader from "@/components/CatalogResultsHeader";
import { ApiError, getProperties } from "@/lib/api";
import type { PropertyCatalogFilters, PropertyCatalogPage } from "@/types/property";

export const metadata: Metadata = {
  title: "Catálogo de propiedades | Urbanex",
  description: "Explora propiedades disponibles y reservadas. Filtra por tipo, precio, ubicación, habitaciones y superficie.",
};

const filterKeys = ["property_type", "price_min", "price_max", "bedrooms", "bathrooms", "area_min", "parking_spaces", "location", "page", "sort"] as const;
export default async function PropertiesPage({ searchParams }: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const query = await searchParams;
  const filters: PropertyCatalogFilters = {};
  for (const key of filterKeys) {
    const value = query[key];
    const first = Array.isArray(value) ? value[0] : value;
    if (first?.trim() && !(["bedrooms", "bathrooms", "parking_spaces"].includes(key) && Number(first) === 0)) filters[key] = first.trim();
  }
  let data: PropertyCatalogPage | null = null;
  let errorMessage = "";
  let fieldErrors: Record<string, string[]> = {};
  try {
    data = await getProperties(filters);
  } catch (error) {
    if (error instanceof ApiError && error.status === 400) {
      errorMessage = "Revisa los filtros indicados e intenta nuevamente.";
      if (error.body && typeof error.body === "object") {
        fieldErrors = Object.fromEntries(Object.entries(error.body).map(([key, value]) => [
          key, Array.isArray(value) ? value.map(String) : [String(value)],
        ]));
      }
    } else if (error instanceof ApiError && error.status === 404) {
      errorMessage = "La página solicitada no existe. Vuelve a la primera página o cambia los filtros.";
    } else {
      errorMessage = "No pudimos cargar el catálogo. Intenta nuevamente en unos momentos.";
    }
  }
  const page = Number(filters.page || "1");
  const hasFilters = filterKeys.some((key) => key !== "page" && key !== "sort" && filters[key]);
  function pageHref(target: number) {
    const params = new URLSearchParams();
    for (const key of filterKeys) {
      if (key !== "page" && filters[key]) params.set(key, filters[key]!);
    }
    if (target > 1) params.set("page", String(target));
    return `/properties${params.size ? `?${params}` : ""}`;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-[1600px]">
        <header className="mb-5">
          <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Encuentra tu próximo hogar</p>
          <h1 className="mt-1 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">Catálogo de propiedades</h1>
          <p className="mt-2 text-slate-600">Explora propiedades disponibles y reservadas. Los precios se muestran en USD y son referenciales.</p>
        </header>

        <CatalogFilters key={JSON.stringify([filters, fieldErrors])} filters={filters} fieldErrors={fieldErrors} distribution={data?.price_distribution} />
        <section aria-label="Resultados del catálogo" className="min-w-0">
            <CatalogResultsHeader count={data?.count} filters={filters} errors={fieldErrors.sort} />
            {errorMessage ? (
              <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-800">
                <p>{errorMessage}</p>
                <Link href={pageHref(1)} className="mt-2 inline-block font-semibold underline">Volver a la primera página</Link>
              </div>
            ) : data && (
              <>
                {data.results.length === 0 ? (
                  <p className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-600">
                    {hasFilters ? "No hay propiedades que coincidan con estos filtros. Prueba con otros valores o limpia los filtros." : "No hay propiedades disponibles por ahora."}
                  </p>
                ) : (
                  <div className="grid grid-cols-[repeat(auto-fill,minmax(min(100%,280px),1fr))] gap-5">
                    {data.results.map((property) => <PropertyCard key={property.id} property={property} />)}
                  </div>
                )}
                {(data.previous || data.next) && (
                  <nav aria-label="Páginas del catálogo" className="mt-8 flex flex-wrap items-center justify-center gap-5">
                    {data.previous && <Link rel="prev" href={pageHref(page - 1)} className="rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold text-blue-700 hover:bg-blue-50">Anterior</Link>}
                    <span aria-current="page" className="text-sm text-slate-700">Página {page} de {Math.ceil(data.count / 20)}</span>
                    {data.next && <Link rel="next" href={pageHref(page + 1)} className="rounded-lg border border-slate-300 bg-white px-4 py-2 font-semibold text-blue-700 hover:bg-blue-50">Siguiente</Link>}
                  </nav>
                )}
              </>
            )}
        </section>
      </div>
    </main>
  );
}
