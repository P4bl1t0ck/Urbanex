"use client";

// Pantalla I-11 (HU-04): el asesor confirma de 3 a 5 comparables y el motor (HU-06, DS-21)
// crea el borrador con el valor sugerido. Sin comparables suficientes ofrece el registro
// manual (DS-02, C-02). Crear un avalúo genera un folio que no se puede eliminar (DS-11),
// por eso se confirma en un modal.

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import Dialog from "@/components/Dialog";
import { ApiError, authFetch } from "@/lib/api";
import type { Appraisal, AppraisalCreatePayload, CandidatesResponse } from "@/types/appraisal";

const STATUS_LABELS: Record<string, string> = {
  disponible: "Disponible (oferta)",
  reservador: "Reservado (oferta)",
  vendido: "Vendido",
};

function formatMoney(value: string | number) {
  return Number(value).toLocaleString("es-EC", { style: "currency", currency: "USD" });
}

function errorMessage(error: unknown) {
  if (error instanceof ApiError && error.body && typeof error.body === "object" && !Array.isArray(error.body)) {
    const body = error.body as Record<string, unknown>;
    for (const key of ["comparables", "property", "non_field_errors", "detail"]) {
      const value = body[key];
      if (Array.isArray(value)) return String(value[0]);
      if (typeof value === "string") return value;
    }
  }
  return error instanceof Error ? error.message : "Ocurrió un error inesperado.";
}

export default function ComparablesPage() {
  const { id: propertyId } = useParams<{ id: string }>();
  const router = useRouter();

  const [data, setData] = useState<CandidatesResponse | null>(null);
  const [hasDraft, setHasDraft] = useState(false);
  const [selected, setSelected] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState<"engine" | "manual" | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!sessionStorage.getItem("access")) {
      router.replace("/login");
      return;
    }
    let isActive = true;

    async function load() {
      try {
        const [candidates, appraisals] = await Promise.all([
          authFetch<CandidatesResponse>(`/api/appraisals/candidates/?property=${propertyId}`),
          authFetch<Appraisal[]>(`/api/appraisals/?property=${propertyId}`),
        ]);
        if (!isActive) return;
        setData(candidates);
        setSelected(candidates.suggested_ids);
        setHasDraft(appraisals.some((a) => a.status === "BORRADOR"));
      } catch (err) {
        if (!isActive) return;
        if (err instanceof ApiError && err.status === 401) {
          router.replace("/login");
          return;
        }
        setLoadError(
          err instanceof ApiError && err.status === 404
            ? "La propiedad no existe o no tienes acceso a ella."
            : errorMessage(err),
        );
      } finally {
        if (isActive) setLoading(false);
      }
    }

    void load();
    return () => {
      isActive = false;
    };
  }, [propertyId, router]);

  function toggle(id: number) {
    setError("");
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  async function create(mode: "engine" | "manual") {
    setBusy(true);
    setError("");
    const payload: AppraisalCreatePayload = { property: Number(propertyId) };
    if (mode === "engine") payload.comparables = selected;
    try {
      await authFetch<Appraisal>("/api/appraisals/", { method: "POST", body: JSON.stringify(payload) });
      router.push(`/dashboard/properties/${propertyId}/appraisal`);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }
      setError(errorMessage(err));
      setPending(null);
      setBusy(false);
    }
  }

  const appraisalHref = `/dashboard/properties/${propertyId}/appraisal`;

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <p className="mx-auto max-w-5xl animate-pulse text-slate-600">Buscando comparables...</p>
      </main>
    );
  }

  if (loadError || !data) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <div className="mx-auto max-w-5xl space-y-4">
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {loadError || "No se pudieron cargar los comparables."}
          </div>
          <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver a mis propiedades
          </Link>
        </div>
      </main>
    );
  }

  const count = selected.length;
  const inRange = count >= data.min_comparables && count <= data.max_comparables;

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header>
          <Link href={appraisalHref} className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver al avalúo
          </Link>
          <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">Comparables del avalúo</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">{data.property.title}</h1>
          <p className="mt-2 text-sm text-slate-600">
            {data.property.area_m2} m² · {data.property.property_type} · precio actual {formatMoney(data.property.price)}
          </p>
        </header>

        {hasDraft && (
          <div role="status" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
            Esta propiedad ya tiene un avalúo en borrador: calíbralo o apruébalo antes de crear otro.{" "}
            <Link href={appraisalHref} className="font-semibold underline">
              Ir al borrador
            </Link>
          </div>
        )}
        {data.blocker && (
          <div role="status" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
            {data.blocker}
          </div>
        )}
        {error && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {error}
          </div>
        )}

        <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-lg font-semibold text-slate-900">Candidatos del mismo tipo y zona</h2>
            <p className={`text-sm font-semibold ${inRange ? "text-green-700" : "text-slate-500"}`}>
              {count} seleccionado(s) · elige de {data.min_comparables} a {data.max_comparables}
            </p>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Vienen preseleccionados los de superficie más parecida. Zona provisional: hasta 1,5 km de distancia
            (DS-21 §7). Parámetros del motor: versión {data.parameters_version ?? "—"}.
          </p>

          {data.candidates.length === 0 ? (
            <p className="mt-4 text-sm text-slate-600">No hay comparables del mismo tipo en la zona.</p>
          ) : (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
                  <tr>
                    <th className="py-2 pr-3">Usar</th>
                    <th className="py-2 pr-3">Propiedad</th>
                    <th className="py-2 pr-3">Estado</th>
                    <th className="py-2 pr-3 text-right">Precio</th>
                    <th className="py-2 pr-3 text-right">m²</th>
                    <th className="py-2 pr-3 text-right">USD/m²</th>
                    <th className="py-2 text-right">Distancia</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {data.candidates.map((c) => (
                    <tr key={c.id} className={selected.includes(c.id) ? "bg-blue-50/50" : ""}>
                      <td className="py-2 pr-3">
                        <input
                          type="checkbox"
                          aria-label={`Usar ${c.title}`}
                          checked={selected.includes(c.id)}
                          onChange={() => toggle(c.id)}
                          className="h-4 w-4 accent-blue-700"
                        />
                      </td>
                      <td className="py-2 pr-3 text-slate-800">{c.title}</td>
                      <td className="py-2 pr-3 text-slate-600">{STATUS_LABELS[c.status] ?? c.status}</td>
                      <td className="py-2 pr-3 text-right text-slate-700">{formatMoney(c.price)}</td>
                      <td className="py-2 pr-3 text-right text-slate-700">{c.area_m2}</td>
                      <td className="py-2 pr-3 text-right text-slate-700">{formatMoney(c.unit_price)}</td>
                      <td className="py-2 text-right text-slate-500">{c.distance_km.toFixed(2)} km</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-6 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => setPending("engine")}
              disabled={busy || hasDraft || !inRange || !data.property.has_coordinates}
              className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Calcular y crear borrador
            </button>
            <button
              type="button"
              onClick={() => setPending("manual")}
              disabled={busy || hasDraft}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Registrar avalúo manual
            </button>
          </div>
          <p className="mt-3 text-xs text-slate-500">
            El valor que calcule el motor es una sugerencia: el valor final lo calibras y lo apruebas tú.
          </p>
        </section>
      </div>

      <Dialog
        open={pending !== null}
        title={pending === "engine" ? "¿Calcular el avalúo con estos comparables?" : "¿Registrar el avalúo manual?"}
        confirmLabel={pending === "engine" ? "Calcular" : "Registrar manual"}
        busy={busy}
        onConfirm={() => pending && void create(pending)}
        onCancel={() => setPending(null)}
      >
        <p>
          {pending === "engine"
            ? `El motor calculará el valor sugerido con ${count} comparable(s) y creará un borrador.`
            : "Se creará un borrador sin valor sugerido y con confianza baja."}{" "}
          El avalúo recibe un folio que no se puede eliminar.
        </p>
      </Dialog>
    </main>
  );
}
