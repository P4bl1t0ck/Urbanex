"use client";

// Pantalla I-08 (HU-24, RF-04): agenda semanal de visitas, de lunes a domingo en hora de Ecuador.
// El asesor ve la suya; el admin elige el asesor (el servidor responde 400 sin él). Por defecto
// muestra todas menos las canceladas. El registro del resultado de la visita es de HU-25.

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ApiError } from "@/lib/api";
import { getAuthSessionSnapshot, subscribeToAuthSession } from "@/lib/auth-session";
import { getAgents } from "@/lib/opportunities";
import { getAgenda } from "@/lib/visits";
import {
  addDays,
  ecuadorToday,
  formatDayLabel,
  formatTime,
  formatWeekLabel,
  groupByEcuadorDay,
  weekRange,
} from "@/lib/visitsCalendar";
import type { AgentOption } from "@/types/opportunity";
import {
  VISIT_STATUS_LABELS,
  type AgendaResponse,
  type AgendaStatusFilter,
  type VisitStatus,
} from "@/types/visit";

const STATUS_OPTIONS: { value: AgendaStatusFilter; label: string }[] = [
  { value: "", label: "Activas (sin canceladas)" },
  ...(Object.keys(VISIT_STATUS_LABELS) as VisitStatus[]).map((status) => ({
    value: status as AgendaStatusFilter,
    label: VISIT_STATUS_LABELS[status],
  })),
  { value: "all", label: "Todas" },
];

const STATUS_BADGE: Record<VisitStatus, string> = {
  PROGRAMADA: "bg-blue-50 text-blue-800 border-blue-200",
  REALIZADA: "bg-green-50 text-green-800 border-green-200",
  NO_ASISTIDA: "bg-amber-50 text-amber-900 border-amber-200",
  CANCELADA: "bg-slate-100 text-slate-500 border-slate-200",
};

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-600 focus:outline-none";

type Loaded = { key: string; data: AgendaResponse | null; error: string };

export default function AgendaPage() {
  const router = useRouter();
  const sessionSnapshot = useSyncExternalStore(subscribeToAuthSession, getAuthSessionSnapshot, () => "");
  const session = sessionSnapshot
    ? (JSON.parse(sessionSnapshot) as { access: string | null; role: string | null })
    : null;
  const isAdmin = session?.role === "admin";

  const [agents, setAgents] = useState<AgentOption[]>([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [weekFrom, setWeekFrom] = useState(() => weekRange(ecuadorToday()).from);
  const [status, setStatus] = useState<AgendaStatusFilter>("");
  const [loaded, setLoaded] = useState<Loaded | null>(null);

  const weekTo = addDays(weekFrom, 6);
  const agentId = isAdmin ? (selectedAgent ? Number(selectedAgent) : undefined) : undefined;
  const canLoad = Boolean(session?.access) && (!isAdmin || agentId !== undefined);
  const requestKey = `${agentId ?? "own"}|${weekFrom}|${status}`;
  const loading = canLoad && loaded?.key !== requestKey;
  const data = !loading ? loaded?.data ?? null : null;
  const error = !loading ? loaded?.error ?? "" : "";

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

  useEffect(() => {
    if (sessionSnapshot && !session?.access) router.replace("/login");
  }, [router, sessionSnapshot, session?.access]);

  useEffect(() => {
    if (!isAdmin) return;
    let isActive = true;
    getAgents()
      .then((rows) => {
        if (isActive) setAgents(rows);
      })
      .catch(handleAuthError);
    return () => {
      isActive = false;
    };
  }, [isAdmin, handleAuthError]);

  useEffect(() => {
    if (!canLoad) return;
    let isActive = true;
    const key = requestKey;
    getAgenda({ from: weekFrom, to: weekTo, agent: agentId, status })
      .then((response) => {
        if (isActive) setLoaded({ key, data: response, error: "" });
      })
      .catch((err) => {
        if (!isActive || handleAuthError(err)) return;
        setLoaded({ key, data: null, error: err instanceof Error ? err.message : "No se pudo cargar la agenda." });
      });
    return () => {
      isActive = false;
    };
  }, [canLoad, requestKey, weekFrom, weekTo, agentId, status, handleAuthError]);

  const days = data
    ? groupByEcuadorDay(data.visits, (visit) => visit.scheduled_start, weekFrom, weekTo)
    : [];
  const today = ecuadorToday();
  const isCurrentWeek = weekFrom === weekRange(today).from;

  // Sin la sesión del navegador (prerender y primer render) no se pintan fechas: "hoy" depende
  // del momento en que se abre la página y no debe salir distinto en el servidor y el cliente.
  if (!sessionSnapshot) {
    return <main className="min-h-screen bg-slate-50 px-4 py-10 text-sm text-slate-500">Cargando…</main>;
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header>
          <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver al panel
          </Link>
          <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">Agendamiento de visitas</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            {isAdmin ? "Agenda de visitas" : "Mi agenda"}
          </h1>
          <p className="mt-2 text-sm text-slate-600">Horas de Ecuador.</p>
        </header>

        <section className="grid gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2">
          {isAdmin && (
            <label className="text-sm font-semibold text-slate-700">
              Asesor
              <select value={selectedAgent} onChange={(event) => setSelectedAgent(event.target.value)} className={inputClass}>
                <option value="">Elija un asesor…</option>
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>{agent.name}</option>
                ))}
              </select>
            </label>
          )}
          <label className="text-sm font-semibold text-slate-700">
            Estado
            <select value={status} onChange={(event) => setStatus(event.target.value as AgendaStatusFilter)} className={inputClass}>
              {STATUS_OPTIONS.map((option) => (
                <option key={option.value || "default"} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <div className="flex flex-wrap items-center gap-2 sm:col-span-2">
            <button type="button" onClick={() => setWeekFrom(addDays(weekFrom, -7))} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">
              ‹ Semana anterior
            </button>
            <span className="px-2 text-sm font-semibold text-slate-800">{formatWeekLabel(weekFrom, weekTo)}</span>
            <button type="button" onClick={() => setWeekFrom(addDays(weekFrom, 7))} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">
              Siguiente ›
            </button>
            {!isCurrentWeek && (
              <button type="button" onClick={() => setWeekFrom(weekRange(today).from)} className="rounded-lg px-3 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50">
                Esta semana
              </button>
            )}
          </div>
        </section>

        {isAdmin && !selectedAgent ? (
          <p className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
            Elija un asesor para ver su agenda.
          </p>
        ) : loading ? (
          <p className="text-sm text-slate-500">Cargando…</p>
        ) : error ? (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{error}</div>
        ) : (
          <section className="space-y-3">
            {data && data.visits.length === 0 && (
              <p className="rounded-xl border border-dashed border-slate-300 bg-white p-6 text-center text-slate-600">
                No hay visitas en esta semana con el filtro elegido.
              </p>
            )}
            {days.map(({ day, items }) => (
              <article
                key={day}
                className={`rounded-xl border bg-white p-4 shadow-sm ${day === today ? "border-blue-300" : "border-slate-200"}`}
              >
                <h2 className="text-sm font-bold capitalize text-slate-900">
                  {formatDayLabel(day)}
                  {day === today && <span className="ml-2 rounded bg-blue-100 px-2 py-0.5 text-xs font-semibold normal-case text-blue-800">Hoy</span>}
                </h2>
                {items.length === 0 ? (
                  <p className="mt-2 text-sm text-slate-400">Sin visitas.</p>
                ) : (
                  <ul className="mt-3 divide-y divide-slate-100">
                    {items.map((visit) => (
                      <li key={visit.id} className="flex flex-wrap items-start gap-x-6 gap-y-2 py-3 text-sm">
                        <span className="w-28 shrink-0 font-semibold text-slate-900">
                          {formatTime(visit.scheduled_start)}–{formatTime(visit.scheduled_end)}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="font-semibold text-slate-800">
                            {visit.property.title}
                            <span className="font-normal text-slate-500"> · {visit.property.location}</span>
                          </p>
                          <p className="mt-1 text-slate-600">
                            {visit.client.full_name}
                            {" · "}
                            <a href={`tel:${visit.client.phone}`} className="text-blue-700 hover:underline">{visit.client.phone}</a>
                            {visit.client.email && (
                              <>
                                {" · "}
                                <a href={`mailto:${visit.client.email}`} className="text-blue-700 hover:underline">{visit.client.email}</a>
                              </>
                            )}
                          </p>
                        </div>
                        <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${STATUS_BADGE[visit.status]}`}>
                          {visit.status_display}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            ))}
          </section>
        )}
      </div>
    </main>
  );
}
