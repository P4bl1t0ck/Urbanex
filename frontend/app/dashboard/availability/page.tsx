"use client";

// Pantalla I-09 (HU-22, RF-09): disponibilidad semanal del asesor y excepciones puntuales.
// El asesor gestiona la suya; el admin primero elige el asesor y luego ve y edita sus franjas
// (decisión de Pablo, 2026-11-06). Las reglas (mínimo 30 min, sin cruces, sin fechas pasadas)
// las valida el servidor; aquí solo se muestran sus errores junto a cada campo.

import { useCallback, useEffect, useState, useSyncExternalStore, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Dialog from "@/components/Dialog";
import { ApiError } from "@/lib/api";
import { getAuthSessionSnapshot, subscribeToAuthSession } from "@/lib/auth-session";
import { getAgents } from "@/lib/opportunities";
import {
  createAvailability,
  createException,
  deleteAvailability,
  deleteException,
  listAvailability,
  listExceptions,
  updateAvailability,
} from "@/lib/visits";
import { ecuadorToday, formatDayLabel, toHourMinute } from "@/lib/visitsCalendar";
import type { AgentOption } from "@/types/opportunity";
import {
  WEEKDAY_LABELS,
  type AvailabilityException,
  type AvailabilityRule,
  type Weekday,
} from "@/types/visit";

const WEEKDAYS = Object.keys(WEEKDAY_LABELS).map(Number) as Weekday[];
const DURATIONS = [30, 45, 60, 90];

const EMPTY_RULE = { day_of_week: "0", start_time: "09:00", end_time: "12:00", slot_duration_minutes: "60" };
const EMPTY_EXCEPTION = { exception_date: "", full_day: true, start_time: "", end_time: "", reason: "" };

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-600 focus:outline-none";

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

function FieldError({ message }: { message?: string }) {
  return message ? <span role="alert" className="mt-1 block text-xs text-red-700">{message}</span> : null;
}

// Confirmación con el modal del proyecto (DS-15: sin alert ni confirm nativos).
type PendingDelete = { kind: "rule" | "exception"; id: number; label: string };

type Loaded = {
  key: string;
  rules: AvailabilityRule[];
  exceptions: AvailabilityException[];
  error: string;
};

export default function AvailabilityPage() {
  const router = useRouter();
  const sessionSnapshot = useSyncExternalStore(subscribeToAuthSession, getAuthSessionSnapshot, () => "");
  const session = sessionSnapshot
    ? (JSON.parse(sessionSnapshot) as { access: string | null; role: string | null })
    : null;
  const isAdmin = session?.role === "admin";

  const [agents, setAgents] = useState<AgentOption[]>([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [reload, setReload] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);

  const [ruleForm, setRuleForm] = useState(EMPTY_RULE);
  const [editingRuleId, setEditingRuleId] = useState<number | null>(null);
  const [ruleErrors, setRuleErrors] = useState<Record<string, string>>({});
  const [exceptionForm, setExceptionForm] = useState(EMPTY_EXCEPTION);
  const [exceptionErrors, setExceptionErrors] = useState<Record<string, string>>({});
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<PendingDelete | null>(null);

  // Para el admin, sin asesor elegido no se pide nada al servidor.
  const agentId = isAdmin ? (selectedAgent ? Number(selectedAgent) : undefined) : undefined;
  const canLoad = Boolean(session?.access) && (!isAdmin || agentId !== undefined);
  const requestKey = `${agentId ?? "own"}|${reload}`;
  const loading = canLoad && loaded?.key !== requestKey;
  const rules = !loading && loaded ? loaded.rules : [];
  const exceptions = !loading && loaded ? loaded.exceptions : [];
  const loadError = !loading ? loaded?.error ?? "" : "";

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
    Promise.all([listAvailability(agentId), listExceptions(agentId)])
      .then(([ruleRows, exceptionRows]) => {
        if (isActive) setLoaded({ key, rules: ruleRows, exceptions: exceptionRows, error: "" });
      })
      .catch((err) => {
        if (!isActive || handleAuthError(err)) return;
        setLoaded({
          key,
          rules: [],
          exceptions: [],
          error: err instanceof Error ? err.message : "No se pudo cargar la disponibilidad.",
        });
      });
    return () => {
      isActive = false;
    };
  }, [canLoad, requestKey, agentId, handleAuthError]);

  function chooseAgent(value: string) {
    setSelectedAgent(value);
    cancelRuleEdit();
    setExceptionForm(EMPTY_EXCEPTION);
    setExceptionErrors({});
    setNotice("");
  }

  function cancelRuleEdit() {
    setEditingRuleId(null);
    setRuleForm(EMPTY_RULE);
    setRuleErrors({});
  }

  function startRuleEdit(rule: AvailabilityRule) {
    setEditingRuleId(rule.id);
    setRuleForm({
      day_of_week: String(rule.day_of_week),
      start_time: toHourMinute(rule.start_time),
      end_time: toHourMinute(rule.end_time),
      slot_duration_minutes: String(rule.slot_duration_minutes),
    });
    setRuleErrors({});
    setNotice("");
  }

  async function submitRule(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setRuleErrors({});
    setNotice("");
    const payload = {
      day_of_week: Number(ruleForm.day_of_week) as Weekday,
      start_time: ruleForm.start_time,
      end_time: ruleForm.end_time,
      slot_duration_minutes: Number(ruleForm.slot_duration_minutes),
    };
    try {
      if (editingRuleId) {
        await updateAvailability(editingRuleId, payload);
        setNotice("Franja actualizada.");
      } else {
        await createAvailability(isAdmin ? { ...payload, agent: agentId } : payload);
        setNotice("Franja agregada.");
      }
      cancelRuleEdit();
      setReload((value) => value + 1);
    } catch (err) {
      if (handleAuthError(err)) return;
      const byField = fieldErrors(err);
      setRuleErrors(Object.keys(byField).length ? byField : { detail: err instanceof Error ? err.message : "No se pudo guardar." });
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    setSaving(true);
    try {
      if (pendingDelete.kind === "rule") {
        await deleteAvailability(pendingDelete.id);
        if (editingRuleId === pendingDelete.id) cancelRuleEdit();
        setNotice("Franja eliminada.");
      } else {
        await deleteException(pendingDelete.id);
        setNotice("Excepción eliminada.");
      }
      setReload((value) => value + 1);
    } catch (err) {
      if (!handleAuthError(err)) setNotice(err instanceof Error ? err.message : "No se pudo eliminar.");
    } finally {
      setSaving(false);
      setPendingDelete(null);
    }
  }

  async function submitException(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setExceptionErrors({});
    setNotice("");
    const payload = {
      exception_date: exceptionForm.exception_date,
      start_time: exceptionForm.full_day ? null : exceptionForm.start_time || null,
      end_time: exceptionForm.full_day ? null : exceptionForm.end_time || null,
      reason: exceptionForm.reason.trim(),
    };
    try {
      await createException(isAdmin ? { ...payload, agent: agentId } : payload);
      setExceptionForm(EMPTY_EXCEPTION);
      setNotice("Excepción registrada.");
      setReload((value) => value + 1);
    } catch (err) {
      if (handleAuthError(err)) return;
      const byField = fieldErrors(err);
      setExceptionErrors(Object.keys(byField).length ? byField : { detail: err instanceof Error ? err.message : "No se pudo guardar." });
    } finally {
      setSaving(false);
    }
  }

  const rulesByDay = WEEKDAYS.map((day) => ({ day, items: rules.filter((rule) => rule.day_of_week === day) }));
  const selectedAgentName = agents.find((agent) => String(agent.id) === selectedAgent)?.name;

  // Sin la sesión del navegador (prerender y primer render) no se pinta la fecha mínima de hoy.
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
            {isAdmin ? "Disponibilidad de los asesores" : "Mi disponibilidad"}
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Los clientes solo ven las franjas libres de estos horarios (hora de Ecuador). Las excepciones bloquean una fecha.
          </p>
        </header>

        {isAdmin && (
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <label className="block max-w-sm text-sm font-semibold text-slate-700">
              Asesor
              <select value={selectedAgent} onChange={(event) => chooseAgent(event.target.value)} className={inputClass}>
                <option value="">Elija un asesor…</option>
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>{agent.name}</option>
                ))}
              </select>
            </label>
          </section>
        )}

        {isAdmin && !selectedAgent ? (
          <p className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
            Elija un asesor para ver y editar su disponibilidad.
          </p>
        ) : (
          <>
            {notice && (
              <div role="status" className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">{notice}</div>
            )}
            {loadError && (
              <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{loadError}</div>
            )}

            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900">
                Franjas semanales{selectedAgentName ? ` de ${selectedAgentName}` : ""}
              </h2>
              {loading ? (
                <p className="mt-4 text-sm text-slate-500">Cargando…</p>
              ) : (
                <ul className="mt-4 divide-y divide-slate-100">
                  {rulesByDay.map(({ day, items }) => (
                    <li key={day} className="flex flex-wrap items-start gap-3 py-3">
                      <span className="w-28 shrink-0 font-semibold text-slate-800">{WEEKDAY_LABELS[day]}</span>
                      {items.length === 0 ? (
                        <span className="text-sm text-slate-400">Sin atención</span>
                      ) : (
                        <div className="flex flex-wrap gap-2">
                          {items.map((rule) => (
                            <span
                              key={rule.id}
                              className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm ${
                                editingRuleId === rule.id ? "border-blue-400 bg-blue-50" : "border-slate-200 bg-slate-50"
                              }`}
                            >
                              <span className="font-semibold text-slate-800">
                                {toHourMinute(rule.start_time)}–{toHourMinute(rule.end_time)}
                              </span>
                              <span className="text-xs text-slate-500">visitas de {rule.slot_duration_minutes} min</span>
                              <button type="button" onClick={() => startRuleEdit(rule)} className="text-xs font-semibold text-blue-700 hover:underline">
                                Editar
                              </button>
                              <button
                                type="button"
                                onClick={() => setPendingDelete({
                                  kind: "rule",
                                  id: rule.id,
                                  label: `la franja del ${rule.day_name} de ${toHourMinute(rule.start_time)} a ${toHourMinute(rule.end_time)}`,
                                })}
                                className="text-xs font-semibold text-red-700 hover:underline"
                              >
                                Eliminar
                              </button>
                            </span>
                          ))}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              )}

              <form onSubmit={submitRule} className="mt-5 grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-5">
                <label className="text-sm font-medium text-slate-700">
                  Día
                  <select value={ruleForm.day_of_week} onChange={(event) => setRuleForm({ ...ruleForm, day_of_week: event.target.value })} className={inputClass}>
                    {WEEKDAYS.map((day) => (
                      <option key={day} value={day}>{WEEKDAY_LABELS[day]}</option>
                    ))}
                  </select>
                  <FieldError message={ruleErrors.day_of_week} />
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Desde
                  <input type="time" required value={ruleForm.start_time} onChange={(event) => setRuleForm({ ...ruleForm, start_time: event.target.value })} className={inputClass} />
                  <FieldError message={ruleErrors.start_time} />
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Hasta
                  <input type="time" required value={ruleForm.end_time} onChange={(event) => setRuleForm({ ...ruleForm, end_time: event.target.value })} className={inputClass} />
                  <FieldError message={ruleErrors.end_time} />
                </label>
                <label className="text-sm font-medium text-slate-700">
                  Duración de la visita
                  <select value={ruleForm.slot_duration_minutes} onChange={(event) => setRuleForm({ ...ruleForm, slot_duration_minutes: event.target.value })} className={inputClass}>
                    {DURATIONS.map((minutes) => (
                      <option key={minutes} value={minutes}>{minutes} min</option>
                    ))}
                  </select>
                  <FieldError message={ruleErrors.slot_duration_minutes} />
                </label>
                <div className="flex items-end gap-2">
                  <button type="submit" disabled={saving} className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60">
                    {editingRuleId ? "Guardar cambios" : "Agregar franja"}
                  </button>
                  {editingRuleId && (
                    <button type="button" onClick={cancelRuleEdit} className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">
                      Cancelar
                    </button>
                  )}
                </div>
                {(ruleErrors.detail || ruleErrors.agent || ruleErrors.non_field_errors) && (
                  <p role="alert" className="text-sm text-red-700 sm:col-span-5">
                    {ruleErrors.detail || ruleErrors.agent || ruleErrors.non_field_errors}
                  </p>
                )}
              </form>
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h2 className="text-lg font-bold text-slate-900">Excepciones</h2>
              <p className="mt-1 text-sm text-slate-600">Fechas en las que no se atiende: el día completo o solo un rango de horas.</p>
              {!loading && (
                exceptions.length === 0 ? (
                  <p className="mt-4 text-sm text-slate-400">No hay excepciones registradas.</p>
                ) : (
                  <ul className="mt-4 divide-y divide-slate-100">
                    {exceptions.map((exception) => (
                      <li key={exception.id} className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
                        <span>
                          <span className="font-semibold capitalize text-slate-800">{formatDayLabel(exception.exception_date)}</span>
                          <span className="ml-2 text-slate-600">
                            {exception.is_full_day
                              ? "Día completo"
                              : `${toHourMinute(exception.start_time)}–${toHourMinute(exception.end_time)}`}
                          </span>
                          {exception.reason && <span className="ml-2 text-slate-500">· {exception.reason}</span>}
                        </span>
                        <button
                          type="button"
                          onClick={() => setPendingDelete({
                            kind: "exception",
                            id: exception.id,
                            label: `la excepción del ${formatDayLabel(exception.exception_date)}`,
                          })}
                          className="text-xs font-semibold text-red-700 hover:underline"
                        >
                          Eliminar
                        </button>
                      </li>
                    ))}
                  </ul>
                )
              )}

              <form onSubmit={submitException} className="mt-5 grid gap-4 border-t border-slate-100 pt-5 sm:grid-cols-5">
                <label className="text-sm font-medium text-slate-700">
                  Fecha
                  <input
                    type="date"
                    required
                    min={ecuadorToday()}
                    value={exceptionForm.exception_date}
                    onChange={(event) => setExceptionForm({ ...exceptionForm, exception_date: event.target.value })}
                    className={inputClass}
                  />
                  <FieldError message={exceptionErrors.exception_date} />
                </label>
                <label className="flex items-center gap-2 self-end pb-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={exceptionForm.full_day}
                    onChange={(event) => setExceptionForm({ ...exceptionForm, full_day: event.target.checked, start_time: "", end_time: "" })}
                    className="h-4 w-4 rounded border-slate-300"
                  />
                  Día completo
                </label>
                {!exceptionForm.full_day && (
                  <>
                    <label className="text-sm font-medium text-slate-700">
                      Desde
                      <input type="time" required value={exceptionForm.start_time} onChange={(event) => setExceptionForm({ ...exceptionForm, start_time: event.target.value })} className={inputClass} />
                      <FieldError message={exceptionErrors.start_time} />
                    </label>
                    <label className="text-sm font-medium text-slate-700">
                      Hasta
                      <input type="time" required value={exceptionForm.end_time} onChange={(event) => setExceptionForm({ ...exceptionForm, end_time: event.target.value })} className={inputClass} />
                      <FieldError message={exceptionErrors.end_time} />
                    </label>
                  </>
                )}
                <label className={`text-sm font-medium text-slate-700 ${exceptionForm.full_day ? "sm:col-span-2" : ""}`}>
                  Motivo (opcional)
                  <input
                    type="text"
                    maxLength={200}
                    value={exceptionForm.reason}
                    onChange={(event) => setExceptionForm({ ...exceptionForm, reason: event.target.value })}
                    className={inputClass}
                  />
                  <FieldError message={exceptionErrors.reason} />
                </label>
                <div className="flex items-end sm:col-span-5">
                  <button type="submit" disabled={saving} className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60">
                    Registrar excepción
                  </button>
                </div>
                {(exceptionErrors.detail || exceptionErrors.agent || exceptionErrors.non_field_errors) && (
                  <p role="alert" className="text-sm text-red-700 sm:col-span-5">
                    {exceptionErrors.detail || exceptionErrors.agent || exceptionErrors.non_field_errors}
                  </p>
                )}
              </form>
            </section>
          </>
        )}
      </div>

      <Dialog
        open={pendingDelete !== null}
        title="¿Eliminar?"
        tone="danger"
        confirmLabel="Eliminar"
        busy={saving}
        onConfirm={confirmDelete}
        onCancel={() => setPendingDelete(null)}
      >
        Se eliminará {pendingDelete?.label}. Las franjas libres que ven los clientes se actualizan de inmediato.
      </Dialog>
    </main>
  );
}
