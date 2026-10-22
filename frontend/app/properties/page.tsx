import PropertyCard from "@/components/PropertyCard";
import SiteNav from "@/components/SiteNav";
import { getProperties } from "@/lib/api";
import type { Property } from "@/types/property";

export default async function PropertiesPage() {
  let properties: Property[] = [];
  let loadFailed = false;
  /*This is the main page. */
  try {
    properties = await getProperties();
  } catch {
    loadFailed = true;
  }

  return (
    <>
      
      <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <header className="mb-8">
            <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">
              Encuentra tu próximo hogar
            </p>
            <h1 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900">
              Catálogo de propiedades
            </h1>
            <p className="mt-2 text-slate-600">
              Explora las propiedades disponibles en Urbanex.
            </p>
          </header>

          {loadFailed ? (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-6 text-red-800"
            >
              No pudimos cargar el catálogo. Verifica que Django esté en
              ejecución e intenta nuevamente.
            </div>
          ) : properties.length === 0 ? (
            <p className="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-600">
              No hay propiedades registradas aún.
            </p>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {properties.map((property) => (
                <PropertyCard key={property.id} property={property} />
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
