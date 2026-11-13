"use client";

// Pantalla I-08 (HU-24, RF-04): agenda semanal de visitas, de lunes a domingo en hora de Ecuador.
// El asesor ve la suya; el admin elige el asesor (el servidor responde 400 sin él). Por defecto
// muestra todas menos las canceladas.
// Lote 3 (DS-39): "Confirmar por WhatsApp" si el cliente no pidió confirmación por correo (HU-20),
// el asesor de seguimiento si no es el de la visita, y el modal para registrar el resultado
// (HU-25): solo después de la hora de inicio, una vez y con observación obligatoria.
// Lotes 5 y 6 (DS-52): "Cancelar" (HU-21) en las visitas Programadas que aún no empiezan, con
// confirmación y motivo obligatorio; se avisa al cliente por correo si lo dio.

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Dialog from "@/components/Dialog";
import { ApiError } from "@/lib/api";
import { getAuthSessionSnapshot, subscribeToAuthSession } from "@/lib/auth-session";
import { getAgents } from "@/lib/opportunities";
import { cancelVisit, getAgenda, recordVisitOutcome } from "@/lib/visits";
import {
  addDays,
  ecuadorDateOf,
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
  type AgendaVisit,
  type VisitOutcome,
  type VisitStatus,
} from "@/types/visit";

const OUTCOME_OPTIONS: VisitOutcome[] = ["REALIZADA", "NO_ASISTIDA", "CANCELADA"];

// wa.me usa el número sin "+" (+5939XXXXXXXX -> 5939XXXXXXXX).
function whatsappLink(phone: string) {
  return `https://wa.me/${phone.replace(/\D/g, "")}`;
}

type OutcomeForm = { visit: AgendaVisit; status: VisitOutcome | ""; notes: string; error: string };
type CancelForm = { visit: AgendaVisit; reason: string; error: string };

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
  const [outcome, setOutcome] = useState<OutcomeForm | null>(null);
  const [savingOutcome, setSavingOutcome] = useState(false);
  const [cancelForm, setCancelForm] = useState<CancelForm | null>(null);
  const [savingCancel, setSavingCancel] = useState(false);

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

  // Reemplaza una visita en la agenda cargada, sin volver a pedirla.
  function replaceVisit(updated: AgendaVisit) {
    setLoaded((current) =>
      current?.data
        ? { ...current, data: { ...current.data, visits: current.data.visits.map((v) => (v.id === updated.id ? updated : v)) } }
        : current,
    );
  }

  async function saveCancel() {
    if (!cancelForm) return;
    const reason = cancelForm.reason.trim();
    if (!reason) {
      setCancelForm({ ...cancelForm, error: "Escribe el motivo de la cancelación." });
      return;
    }
    setSavingCancel(true);
    try {
      replaceVisit(await cancelVisit(cancelForm.visit.id, { reason }));
      setCancelForm(null);
    } catch (err) {
      if (handleAuthError(err)) return;
      setCancelForm({ ...cancelForm, error: err instanceof Error ? err.message : "No se pudo cancelar la visita." });
    } finally {
      setSavingCancel(false);
    }
  }

  async function saveOutcome() {
    if (!outcome) return;
    const notes = outcome.notes.trim();
    if (!outcome.status || !notes) {
      setOutcome({ ...outcome, error: "Elige el resultado y escribe la observación." });
      return;
    }
    setSavingOutcome(true);
    try {
      replaceVisit(await recordVisitOutcome(outcome.visit.id, { status: outcome.status, outcome_notes: notes }));
      setOutcome(null);
    } catch (err) {
      if (handleAuthError(err)) return;
      setOutcome({ ...outcome, error: err instanceof Error ? err.message : "No se pudo registrar el resultado." });
    } finally {
      setSavingOutcome(false);
    }
  }

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
                          {visit.followup_agent_name && (
                            <p className="mt-1 text-xs text-slate-500">Seguimiento de la oportunidad: {visit.followup_agent_name}</p>
                          )}
                          {visit.needs_whatsapp_confirmation && (
                            <a
                              href={whatsappLink(visit.client.phone)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="mt-2 inline-block rounded-full border border-emerald-300 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-800 hover:bg-emerald-100"
                            >
                              Confirmar por WhatsApp
                            </a>
                          )}
                          {visit.outcome_recorded_at && (
                            <p className="mt-2 rounded-lg bg-slate-50 p-2 text-xs text-slate-600">
                              <span className="font-semibold text-slate-700">Resultado:</span> {visit.outcome_notes}
                              {visit.outcome_recorded_by_name && <> · {visit.outcome_recorded_by_name}</>}
                            </p>
                          )}
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${STATUS_BADGE[visit.status]}`}>
                            {visit.status_display}
                          </span>
                          {visit.can_record_outcome && (
                            <button
                              type="button"
                              onClick={() => setOutcome({ visit, status: "", notes: "", error: "" })}
                              className="rounded-lg border border-blue-300 bg-white px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-50"
                            >
                              Registrar resultado
                            </button>
                          )}
                          {visit.can_cancel && (
                            <button
                              type="button"
                              onClick={() => setCancelForm({ visit, reason: "", error: "" })}
                              className="rounded-lg border border-red-300 bg-white px-2.5 py-1 text-xs font-semibold text-red-700 hover:bg-red-50"
                            >
                              Cancelar
                            </button>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            ))}
          </section>
        )}
      </div>

      <Dialog
        open={outcome !== null}
        title="Registrar resultado de la visita"
        confirmLabel={savingOutcome ? "Guardando…" : "Guardar resultado"}
        busy={savingOutcome}
        onConfirm={saveOutcome}
        onCancel={() => setOutcome(null)}
      >
        {outcome && (
          <div className="space-y-3">
            <p>
              {outcome.visit.property.title} · {outcome.visit.client.full_name} ·{" "}
              {formatTime(outcome.visit.scheduled_start)}
            </p>
            <p className="text-xs text-slate-500">Se registra una sola vez y no se puede editar después.</p>
            <fieldset>
              <legend className="text-sm font-semibold text-slate-700">Resultado</legend>
              <div className="mt-1 flex flex-wrap gap-3">
                {OUTCOME_OPTIONS.map((option) => (
                  <label key={option} className="flex items-center gap-1.5 text-sm text-slate-800">
                    <input
                      type="radio"
                      name="visit-outcome"
                      value={option}
                      checked={outcome.status === option}
                      onChange={() => setOutcome({ ...outcome, status: option, error: "" })}
                    />
                    {VISIT_STATUS_LABELS[option]}
                  </label>
                ))}
              </div>
            </fieldset>
            <label className="block text-sm font-semibold text-slate-700">
              Observación (respuesta del cliente)
              <textarea
                rows={3}
                maxLength={2000}
                value={outcome.notes}
                onChange={(event) => setOutcome({ ...outcome, notes: event.target.value, error: "" })}
                className={inputClass}
              />
            </label>
            {outcome.error && (
              <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-2 text-sm text-red-800">{outcome.error}</p>
            )}
          </div>
        )}
      </Dialog>

      <Dialog
        open={cancelForm !== null}
        title="¿Cancelar la visita?"
        confirmLabel={savingCancel ? "Cancelando…" : "Cancelar visita"}
        cancelLabel="Volver"
        tone="danger"
        busy={savingCancel}
        onConfirm={saveCancel}
        onCancel={() => setCancelForm(null)}
      >
        {cancelForm && (
          <div className="space-y-3">
            <p>
              {cancelForm.visit.property.title} · {cancelForm.visit.client.full_name} ·{" "}
              {formatDayLabel(ecuadorDateOf(cancelForm.visit.scheduled_start))} {formatTime(cancelForm.visit.scheduled_start)}
            </p>
            <p className="text-xs text-slate-500">
              La franja queda libre y no se puede deshacer.{" "}
              {cancelForm.visit.needs_whatsapp_confirmation
                ? "El cliente no dio correo: avísale por WhatsApp."
                : "Se avisará al cliente por correo."}
            </p>
            <label className="block text-sm font-semibold text-slate-700">
              Motivo
              <textarea
                rows={3}
                maxLength={1000}
                value={cancelForm.reason}
                onChange={(event) => setCancelForm({ ...cancelForm, reason: event.target.value, error: "" })}
                className={inputClass}
              />
            </label>
            {cancelForm.error && (
              <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-2 text-sm text-red-800">{cancelForm.error}</p>
            )}
          </div>
        )}
      </Dialog>
    </main>
  );
}
