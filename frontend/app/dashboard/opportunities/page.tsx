"use client";

// Pantalla I-06 (HU-34): cartera de oportunidades con filtros combinables por asesor, propiedad,
// estado y fecha de apertura. El asesor ve la suya y el admin todas: lo decide el servidor.
// Sin detalle (I-06A) ni cambios de estado en este corte (RF-06 llega después).

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api";
import { getAgents, getEligibleProperties, listOpportunities } from "@/lib/opportunities";
import {
  OPPORTUNITY_STATUS_LABELS,
  type AgentOption,
  type EligibleProperty,
  type OpportunityFilters,
  type OpportunityPage,
  type OpportunityStatus,
} from "@/types/opportunity";

const EMPTY_FILTERS: OpportunityFilters = {
  assigned_agent: "",
  property: "",
  status: "",
  created_from: "",
  created_to: "",
};

function formatDate(value: string) {
  return new Date(value).toLocaleString("es-EC", {
    timeZone: "America/Guayaquil",
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function fieldErrors(error: unknown): Record<string, string> {
  if (!(error instanceof ApiError) || !error.body || typeof error.body !== "object" || Array.isArray(error.body)) {
    return {};
  }
  const result: Record<string, string> = {};
  for (const [key, value] of Object.entries(error.body as Record<string, unknown>)) {
    result[key] = Array.isArray(value) ? String(value[0]) : String(value);
  }
  return result;
}

type ListResult = {
  key: string;
  data: OpportunityPage | null;
  error: string;
  errors: Record<string, string>;
};

type Session = { isAdmin: boolean; openedId: string | null };

export default function OpportunitiesPage() {
  const router = useRouter();
  const [session, setSession] = useState<Session>({ isAdmin: false, openedId: null });
  const [draft, setDraft] = useState<OpportunityFilters>(EMPTY_FILTERS);
  const [filters, setFilters] = useState<OpportunityFilters>(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [result, setResult] = useState<ListResult | null>(null);
  const [properties, setProperties] = useState<EligibleProperty[]>([]);
  const [agents, setAgents] = useState<AgentOption[]>([]);

  // "Cargando" mientras el último resultado no corresponda a los filtros y la página actuales.
  const requestKey = `${JSON.stringify(filters)}|${page}`;
  const loading = result?.key !== requestKey;
  const data = loading ? null : result?.data ?? null;
  const error = loading ? "" : result?.error ?? "";
  const errors = result?.errors ?? {};
  const { isAdmin, openedId } = session;

  const handleAuthError = useCallback(
    (err: unknown) => {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return true;
      }
      return false;
    },
    [router],
  );

  // Opciones de los filtros. La lista de propiedades son las disponibles (las únicas donde se
  // abre una oportunidad en este corte, DS-28).
  useEffect(() => {
    if (!sessionStorage.getItem("access")) {
      router.replace("/login");
      return;
    }
    // El rol solo decide qué controles se muestran; los permisos los aplica el servidor.
    const admin = sessionStorage.getItem("userRole") === "admin";
    const query = new URLSearchParams(window.location.search);
    const opened = query.get("opened");
    // ?property=<id> llega desde el aviso de I-07 cuando ya existe una oportunidad activa.
    const initialProperty = query.get("property") ?? "";
    let isActive = true;

    async function loadOptions() {
      try {
        const [rows, agentRows] = await Promise.all([
          getEligibleProperties(),
          admin ? getAgents() : Promise.resolve([] as AgentOption[]),
        ]);
        if (!isActive) return;
        setProperties(rows);
        setAgents(agentRows);
      } catch (err) {
        handleAuthError(err);
      } finally {
        if (isActive) {
          setSession({ isAdmin: admin, openedId: opened });
          if (/^\d+$/.test(initialProperty)) {
            const initial = { ...EMPTY_FILTERS, property: initialProperty };
            setDraft(initial);
            setFilters(initial);
          }
        }
      }
    }

    void loadOptions();
    return () => {
      isActive = false;
    };
  }, [router, handleAuthError]);

  useEffect(() => {
    if (!sessionStorage.getItem("access")) return;
    let isActive = true;
    const key = `${JSON.stringify(filters)}|${page}`;
    listOpportunities(filters, page)
      .then((rows) => {
        if (isActive) setResult({ key, data: rows, error: "", errors: {} });
      })
      .catch((err) => {
        if (!isActive || handleAuthError(err)) return;
        const byField = fieldErrors(err);
        setResult({
          key,
          data: null,
          errors: byField,
          error: Object.keys(byField).length
            ? "Revisa los filtros marcados."
            : err instanceof Error ? err.message : "No se pudo cargar la cartera.",
        });
      });
    return () => {
      isActive = false;
    };
  }, [filters, page, handleAuthError]);

  function applyFilters(event: FormEvent) {
    event.preventDefault();
    setPage(1);
    setFilters({ ...draft });
  }

  function clearFilters() {
    setDraft(EMPTY_FILTERS);
    setPage(1);
    setFilters(EMPTY_FILTERS);
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.count / 20)) : 1;
  const inputClass =
    "mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-600 focus:outline-none";

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">
              ← Volver al panel
            </Link>
            <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">Seguimiento de oportunidades</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
              {isAdmin ? "Oportunidades del equipo" : "Mi cartera de oportunidades"}
            </h1>
          </div>
          <Link
            href="/dashboard/opportunities/new"
            className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800"
          >
            + Abrir oportunidad
          </Link>
        </header>

        {openedId && (
          <div role="status" className="rounded-lg border border-green-200 bg-green-50 p-4 text-green-800">
            Oportunidad #{openedId} abierta en Contacto inicial.
          </div>
        )}

        <form onSubmit={applyFilters} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {isAdmin && (
              <label className="text-sm font-medium text-slate-700">
                Asesor
                <select
                  className={inputClass}
                  value={draft.assigned_agent}
                  onChange={(e) => setDraft({ ...draft, assigned_agent: e.target.value })}
                >
                  <option value="">Todos</option>
                  {agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>{agent.name}</option>
                  ))}
                </select>
                {errors.assigned_agent && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.assigned_agent}</span>}
              </label>
            )}
            <label className="text-sm font-medium text-slate-700">
              Propiedad
              <select
                className={inputClass}
                value={draft.property}
                onChange={(e) => setDraft({ ...draft, property: e.target.value })}
              >
                <option value="">Todas</option>
                {properties.map((property) => (
                  <option key={property.id} value={property.id}>{property.title}</option>
                ))}
              </select>
              {errors.property && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.property}</span>}
            </label>
            <label className="text-sm font-medium text-slate-700">
              Estado
              <select
                className={inputClass}
                value={draft.status}
                onChange={(e) => setDraft({ ...draft, status: e.target.value as OpportunityStatus | "" })}
              >
                <option value="">Todos</option>
                {Object.entries(OPPORTUNITY_STATUS_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              {errors.status && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.status}</span>}
            </label>
            <label className="text-sm font-medium text-slate-700">
              Abierta desde
              <input
                type="date"
                className={inputClass}
                value={draft.created_from}
                onChange={(e) => setDraft({ ...draft, created_from: e.target.value })}
              />
              {errors.created_from && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.created_from}</span>}
            </label>
            <label className="text-sm font-medium text-slate-700">
              Abierta hasta
              <input
                type="date"
                className={inputClass}
                value={draft.created_to}
                onChange={(e) => setDraft({ ...draft, created_to: e.target.value })}
              />
              {errors.created_to && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.created_to}</span>}
            </label>
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button type="submit" className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-800">
              Filtrar
            </button>
            <button type="button" onClick={clearFilters} className="rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">
              Limpiar
            </button>
            <p className="text-xs text-slate-500">Las fechas se interpretan en hora de Ecuador.</p>
          </div>
        </form>

        {error && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {error}
          </div>
        )}

        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          {loading ? (
            <p className="animate-pulse text-sm text-slate-600">Cargando oportunidades...</p>
          ) : !data ? null : data.results.length === 0 ? (
            <p className="text-sm text-slate-600">
              No hay oportunidades con estos filtros.{" "}
              <Link href="/dashboard/opportunities/new" className="font-semibold text-blue-700 hover:underline">
                Abrir una oportunidad
              </Link>
            </p>
          ) : (
            <>
              <p className="mb-3 text-sm text-slate-500">{data.count} oportunidad(es)</p>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="py-2 pr-3">#</th>
                      <th className="py-2 pr-3">Contacto</th>
                      <th className="py-2 pr-3">Propiedad</th>
                      <th className="py-2 pr-3">Estado</th>
                      {isAdmin && <th className="py-2 pr-3">Asesor</th>}
                      <th className="py-2 pr-3">Canal</th>
                      <th className="py-2">Apertura</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {data.results.map((row) => (
                      <tr key={row.id} className={String(row.id) === openedId ? "bg-green-50/60" : ""}>
                        <td className="py-2 pr-3 text-slate-500">{row.id}</td>
                        <td className="py-2 pr-3">
                          <span className="block font-medium text-slate-800">{row.contact.full_name}</span>
                          <span className="text-xs text-slate-500">{row.contact.phone}</span>
                        </td>
                        <td className="py-2 pr-3">
                          <span className="block text-slate-800">{row.property.title}</span>
                          <span className="text-xs text-slate-500">{row.property.sector}</span>
                        </td>
                        <td className="py-2 pr-3">
                          <span className="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-800">
                            {row.status_display}
                          </span>
                        </td>
                        {isAdmin && <td className="py-2 pr-3 text-slate-700">{row.assigned_agent.name}</td>}
                        <td className="py-2 pr-3 text-slate-600">{row.origin_channel_display}</td>
                        <td className="py-2 text-slate-600">{formatDate(row.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {totalPages > 1 && (
                <div className="mt-4 flex items-center justify-end gap-2 text-sm">
                  <button
                    type="button"
                    disabled={!data.previous}
                    onClick={() => setPage((p) => p - 1)}
                    className="rounded-lg border border-slate-300 px-3 py-1 font-semibold text-slate-700 disabled:opacity-50"
                  >
                    Anterior
                  </button>
                  <span className="text-slate-600">Página {page} de {totalPages}</span>
                  <button
                    type="button"
                    disabled={!data.next}
                    onClick={() => setPage((p) => p + 1)}
                    className="rounded-lg border border-slate-300 px-3 py-1 font-semibold text-slate-700 disabled:opacity-50"
                  >
                    Siguiente
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </main>
  );
}
