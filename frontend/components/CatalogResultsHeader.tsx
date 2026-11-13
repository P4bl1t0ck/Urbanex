"use client";

import { useTransition } from "react";
import { useRouter } from "next/navigation";
import type { PropertyCatalogFilters } from "@/types/property";
import { catalogHref } from "@/lib/catalogFilters";

export default function CatalogResultsHeader({ count, filters, errors }: {
  count?: number;
  filters: PropertyCatalogFilters;
  errors?: string[];
}) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  return <div className="mb-4" aria-busy={pending}>
    <div className="flex flex-wrap items-center justify-between gap-3">
      <p className="text-sm text-slate-600" aria-live="polite">
        {count === undefined ? "Resultados" : `${count} ${count === 1 ? "propiedad encontrada" : "propiedades encontradas"}`}
      </p>
      <div className="ml-auto flex min-w-0 max-w-full items-center gap-2">
        <label htmlFor="catalog-sort" className="shrink-0 text-sm font-medium text-slate-600">Ordenar por</label>
        <select id="catalog-sort" value={filters.sort || "recent"} disabled={pending}
          onChange={(event) => {
            const sort = event.target.value;
            startTransition(() => router.push(catalogHref(filters, { sort }), { scroll: false }));
          }}
          aria-invalid={!!errors} aria-describedby={errors ? "catalog-sort-error" : undefined}
          className="min-h-11 min-w-0 rounded-lg border border-slate-300 bg-white px-2 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600">
          <option value="recent">Más recientes</option>
          <option value="price_asc">Precio: menor a mayor</option>
          <option value="price_desc">Precio: mayor a menor</option>
          {filters.sort && !["recent", "price_asc", "price_desc"].includes(filters.sort) && <option value={filters.sort}>Orden no válido</option>}
        </select>
      </div>
    </div>
    {pending && <p role="status" className="sr-only">Actualizando resultados</p>}
    {errors && <p id="catalog-sort-error" role="alert" className="mt-2 text-sm text-red-700">{errors.join(" ")}</p>}
  </div>;
}
