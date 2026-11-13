"use client";

// Pantalla I-06A (lote 4, DS-50): detalle de la oportunidad para el asesor asignado o el admin.
// - HU-29: barra de progreso Contacto inicial -> Visita programada -> En negociación ->
//   Pendiente de cierre. Se avanza un paso a la vez, con confirmación (no hay retroceso
//   manual). El botón se deshabilita con el mismo motivo que daría la API si falta la visita;
//   el paso a Pendiente de cierre pide el precio final acordado (> 0).
// - HU-30: línea de tiempo inmutable (cambios de estado + interacciones) y formulario de NOTA o
//   CONTRAOFERTA. En Cierre no se registran interacciones nuevas.
// Otro asesor recibe 404 del servidor: aquí se muestra como "no encontrada".

import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import AutoGrowTextarea from "@/components/AutoGrowTextarea";
import Dialog from "@/components/Dialog";
import { ApiError } from "@/lib/api";
import { getAuthSessionSnapshot, subscribeToAuthSession } from "@/lib/auth-session";
import { advanceOpportunity, createInteraction, getOpportunity } from "@/lib/opportunities";
import {
  MAX_INTERACTION_NOTES,
  buildTimeline,
  isPositiveAmount,
  pipelineSteps,
} from "@/lib/opportunityPipeline";
import type { InteractionCreatePayload, OpportunityDetail } from "@/types/opportunity";

function formatDateTime(value: string) {
  return new Date(value).toLocaleString("es-EC", {
    timeZone: "America/Guayaquil",
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatMoney(value: string) {
  return Number(value).toLocaleString("es-EC", { style: "currency", currency: "USD" });
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

type Loaded = { key: number; data: OpportunityDetail | null; error: string; notFound: boolean };

type InteractionDraft = {
  interaction_type: "NOTA" | "CONTRAOFERTA";
  notes: string;
  offered_price: string;
  visit: string;
};

const EMPTY_DRAFT: InteractionDraft = { interaction_type: "NOTA", notes: "", offered_price: "", visit: "" };

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-600 focus:outline-none";

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const sessionSnapshot = useSyncExternalStore(subscribeToAuthSession, getAuthSessionSnapshot, () => "");
  const session = sessionSnapshot ? (JSON.parse(sessionSnapshot) as { access: string | null }) : null;
  const validId = /^\d+$/.test(id ?? "");

  const [reload, setReload] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [notice, setNotice] = useState("");

  const [finalPrice, setFinalPrice] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [advancing, setAdvancing] = useState(false);
  const [advanceError, setAdvanceError] = useState("");

  const [draft, setDraft] = useState<InteractionDraft>(EMPTY_DRAFT);
  const [draftErrors, setDraftErrors] = useState<Record<string, string>>({});
  const [savingInteraction, setSavingInteraction] = useState(false);

  const canLoad = Boolean(session?.access) && validId;
  const loading = canLoad && loaded?.key !== reload;
  const data = !loading ? loaded?.data ?? null : null;

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
    if (!canLoad) return;
    let isActive = true;
    const key = reload;
    getOpportunity(id)
      .then((detail) => {
        if (isActive) setLoaded({ key, data: detail, error: "", notFound: false });
      })
      .catch((err) => {
        if (!isActive || handleAuthError(err)) return;
        const notFound = err instanceof ApiError && err.status === 404;
        setLoaded({
          key,
          data: null,
          notFound,
          error: notFound ? "" : err instanceof Error ? err.message : "No se pudo cargar la oportunidad.",
        });
      });
    return () => {
      isActive = false;
    };
  }, [canLoad, id, reload, handleAuthError]);

  const needsPrice = data?.next_status === "PENDIENTE_CIERRE";
  const advanceDisabled =
    !data?.next_status || Boolean(data.advance_blocked_reason) || (needsPrice && !isPositiveAmount(finalPrice));

  async function confirmAdvance() {
    if (!data?.next_status) return;
    setAdvancing(true);
    setAdvanceError("");
    try {
      const updated = await advanceOpportunity(data.id, {
        status: data.next_status,
        agreed_final_price: needsPrice ? finalPrice.trim() : null,
      });
      setLoaded({ key: reload, data: updated, error: "", notFound: false });
      setNotice(`La oportunidad pasó a "${updated.status_display}".`);
      setFinalPrice("");
    } catch (err) {
      if (handleAuthError(err)) return;
      setAdvanceError(err instanceof Error ? err.message : "No se pudo cambiar el estado.");
      setReload((value) => value + 1); // Puede haber cambiado mientras tanto
    } finally {
      setAdvancing(false);
      setConfirming(false);
    }
  }

  async function submitInteraction(event: React.FormEvent) {
    event.preventDefault();
    if (!data) return;
    const missing: Record<string, string> = {};
    if (!draft.notes.trim()) missing.notes = "Escribe las observaciones.";
    if (draft.interaction_type === "CONTRAOFERTA" && !isPositiveAmount(draft.offered_price)) {
      missing.offered_price = "Indica el precio ofrecido (mayor que 0, hasta 2 decimales).";
    }
    setDraftErrors(missing);
    if (Object.keys(missing).length > 0) return;

    const payload: InteractionCreatePayload = {
      interaction_type: draft.interaction_type,
      notes: draft.notes,
      offered_price: draft.interaction_type === "CONTRAOFERTA" ? draft.offered_price.trim() : null,
      visit: draft.visit ? Number(draft.visit) : null,
    };
    setSavingInteraction(true);
    try {
      await createInteraction(data.id, payload);
      setDraft(EMPTY_DRAFT);
      setNotice("Interacción registrada.");
      setReload((value) => value + 1);
    } catch (err) {
      if (handleAuthError(err)) return;
      const byField = fieldErrors(err);
      setDraftErrors(
        Object.keys(byField).length ? byField : { detail: err instanceof Error ? err.message : "No se pudo registrar." },
      );
    } finally {
      setSavingInteraction(false);
    }
  }

  const backLink = (
    <Link href="/dashboard/opportunities" className="text-sm font-semibold text-blue-700 hover:underline">
      ← Volver a la cartera
    </Link>
  );

  if (!validId || loaded?.notFound) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl space-y-4">
          {backLink}
          <h1 className="text-2xl font-bold text-slate-900">Oportunidad no encontrada</h1>
          <p className="text-slate-600">No existe o no pertenece a tu cartera.</p>
        </div>
      </main>
    );
  }

  const progress = data ? pipelineSteps(data.status) : null;
  const timeline = data ? buildTimeline(data.status_history, data.interactions, data.documents) : [];
  const visitLabel = (visitId: number | null) => {
    const visit = data?.visits.find((row) => row.id === visitId);
    return visit ? `Visita del ${formatDateTime(visit.scheduled_start)}` : "";
  };

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header>
          {backLink}
          <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">Detalle de la oportunidad</p>
          <h1 className="mt-1 break-words text-3xl font-bold tracking-tight text-slate-900">
            {data ? `#${data.id} · ${data.contact.full_name}` : "Cargando…"}
          </h1>
        </header>

        {loaded?.error && !loading && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{loaded.error}</div>
        )}
        {notice && (
          <div role="status" className="rounded-lg border border-green-200 bg-green-50 p-4 text-green-800">{notice}</div>
        )}

        {loading && <p className="animate-pulse text-sm text-slate-600">Cargando oportunidad...</p>}

        {data && progress && (
          <>
            <section className="grid gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2 lg:grid-cols-4">
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase text-slate-500">Contacto</p>
                <p className="break-words font-medium text-slate-900">{data.contact.full_name}</p>
                <p className="text-sm text-slate-600">{data.contact.phone}</p>
                {data.contact.email && <p className="break-all text-sm text-slate-600">{data.contact.email}</p>}
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase text-slate-500">Propiedad</p>
                <Link href={`/properties/${data.property.id}`} className="break-words font-medium text-blue-700 hover:underline">
                  {data.property.title}
                </Link>
                <p className="text-sm text-slate-600">{data.property.sector}</p>
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase text-slate-500">Asesor y canal</p>
                <p className="font-medium text-slate-900">{data.assigned_agent.name}</p>
                <p className="text-sm text-slate-600">{data.origin_channel_display}</p>
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold uppercase text-slate-500">Apertura y actividad</p>
                <p className="text-sm text-slate-700">Abierta: {formatDateTime(data.created_at)}</p>
                <p className="text-sm text-slate-700">Última actividad: {formatDateTime(data.last_activity_at)}</p>
              </div>
            </section>

            {/* HU-29: barra de progreso y avance de un paso */}
            <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm" aria-labelledby="pipeline-title">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 id="pipeline-title" className="text-lg font-bold text-slate-900">Estado de la oportunidad</h2>
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-800">{data.status_display}</span>
              </div>

              <ol className="mt-5 flex flex-col gap-3 sm:flex-row sm:gap-2">
                {progress.steps.map((step, index) => (
                  <li key={step.status} className="flex flex-1 items-center gap-2 sm:flex-col sm:text-center">
                    <span
                      aria-hidden="true"
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                        step.state === "done"
                          ? "bg-green-600 text-white"
                          : step.state === "current"
                            ? "bg-blue-700 text-white ring-4 ring-blue-100"
                            : "bg-slate-200 text-slate-500"
                      }`}
                    >
                      {step.state === "done" ? "✓" : index + 1}
                    </span>
                    <span
                      className={`text-sm ${step.state === "current" ? "font-bold text-blue-800" : step.state === "done" ? "text-green-800" : "text-slate-500"}`}
                    >
                      {step.label}
                      <span className="sr-only">
                        {step.state === "done" ? " (completada)" : step.state === "current" ? " (actual)" : " (pendiente)"}
                      </span>
                    </span>
                  </li>
                ))}
              </ol>

              {!progress.inPipeline && (
                <p className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
                  &quot;{data.status_display}&quot; está fuera de la secuencia de este corte; no se avanza desde aquí.
                </p>
              )}
              {data.agreed_final_price && (
                <p className="mt-4 text-sm text-slate-700">
                  Precio final acordado: <span className="font-semibold">{formatMoney(data.agreed_final_price)}</span>
                </p>
              )}

              {data.next_status ? (
                <div className="mt-5 rounded-lg border border-blue-100 bg-blue-50/50 p-4">
                  <p className="text-sm font-semibold text-slate-900">Siguiente paso: {data.next_status_display}</p>
                  {needsPrice && (
                    <label className="mt-3 block max-w-xs text-sm font-medium text-slate-800">
                      Precio final acordado (USD)
                      <input
                        type="text"
                        inputMode="decimal"
                        placeholder="Ej.: 142500.00"
                        value={finalPrice}
                        onChange={(e) => setFinalPrice(e.target.value)}
                        aria-invalid={Boolean(finalPrice) && !isPositiveAmount(finalPrice)}
                        className={inputClass}
                      />
                      <span className="mt-1 block text-xs text-slate-500">Mayor que 0, hasta 2 decimales. No cambia el precio público.</span>
                    </label>
                  )}
                  {data.advance_blocked_reason && (
                    <p className="mt-3 text-sm text-amber-900">
                      {data.advance_blocked_reason}{" "}
                      <Link href="/dashboard/agenda" className="font-semibold underline">Ver agenda</Link>
                    </p>
                  )}
                  {advanceError && <p role="alert" className="mt-3 text-sm text-red-700">{advanceError}</p>}
                  <button
                    type="button"
                    disabled={advanceDisabled || advancing}
                    onClick={() => setConfirming(true)}
                    className="mt-4 w-full rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
                  >
                    Avanzar a {data.next_status_display}
                  </button>
                </div>
              ) : data.status === "PENDIENTE_CIERRE" ? (
                <p className="mt-5 text-sm text-slate-700">
                  Pendiente de cierre es el último paso del asesor: el cierre lo confirma el administrador (RF-07, fuera de este corte).
                </p>
              ) : null}
            </section>

            {/* HU-30: línea de tiempo y registro de interacciones */}
            <section className="grid gap-6 lg:grid-cols-5">
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-3" aria-labelledby="timeline-title">
                <h2 id="timeline-title" className="text-lg font-bold text-slate-900">Historial</h2>
                <p className="text-xs text-slate-500">Inmutable: los registros no se editan ni se borran.</p>
                {timeline.length === 0 ? (
                  <p className="mt-4 text-sm text-slate-600">Todavía no hay registros.</p>
                ) : (
                  <ol className="mt-4 space-y-3">
                    {timeline.map((item) => (
                      <li key={item.key} className="min-w-0 rounded-lg border border-slate-100 bg-slate-50 p-3">
                        <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
                          {item.kind === "status" ? (
                            <span className="rounded-full bg-blue-100 px-2 py-0.5 font-semibold text-blue-800">Cambio de estado</span>
                          ) : item.kind === "document" ? (
                            <span className="rounded-full bg-violet-100 px-2 py-0.5 font-semibold text-violet-800">Documento</span>
                          ) : (
                            <span
                              className={`rounded-full px-2 py-0.5 font-semibold ${
                                item.entry.interaction_type === "CONTRAOFERTA"
                                  ? "bg-amber-100 text-amber-900"
                                  : item.entry.interaction_type === "SISTEMA"
                                    ? "bg-slate-200 text-slate-700"
                                    : "bg-green-100 text-green-800"
                              }`}
                            >
                              {item.entry.interaction_type_display}
                            </span>
                          )}
                          <span>{formatDateTime(item.createdAt)}</span>
                        </div>
                        {item.kind === "status" ? (
                          <>
                            <p className="mt-2 text-sm text-slate-800">
                              {item.entry.previous_status_display ? `${item.entry.previous_status_display} → ` : "Apertura en "}
                              <span className="font-semibold">{item.entry.new_status_display}</span>
                            </p>
                            <p className="text-xs text-slate-500">
                              {item.entry.changed_by?.name ?? "Sistema"}{item.entry.reason ? ` · ${item.entry.reason}` : ""}
                            </p>
                          </>
                        ) : item.kind === "document" ? (
                          <>
                            <p className="mt-2 text-sm text-slate-800">
                              {item.entry.doc_type_display} · versión {item.entry.version}
                              {!item.entry.is_current_version && " (reemplazada)"}
                            </p>
                            <p className="text-xs text-slate-500">
                              Validación: {item.entry.validation_status_display} · Subido por {item.entry.uploaded_by?.name ?? "—"}
                            </p>
                          </>
                        ) : (
                          <>
                            <p className="mt-2 whitespace-pre-line break-words text-sm text-slate-800">{item.entry.notes}</p>
                            {item.entry.offered_price && (
                              <p className="mt-1 text-sm font-semibold text-amber-900">Precio ofrecido: {formatMoney(item.entry.offered_price)}</p>
                            )}
                            <p className="mt-1 text-xs text-slate-500">
                              {item.entry.author?.name ?? "Sistema"}
                              {item.entry.visit ? ` · ${visitLabel(item.entry.visit)}` : ""}
                            </p>
                          </>
                        )}
                      </li>
                    ))}
                  </ol>
                )}
              </div>

              <div className="space-y-6 lg:col-span-2">
                <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h2 className="text-lg font-bold text-slate-900">Registrar interacción</h2>
                  {!data.accepts_interactions ? (
                    <p className="mt-3 text-sm text-slate-600">La oportunidad está cerrada: no se registran interacciones nuevas.</p>
                  ) : (
                    <form onSubmit={submitInteraction} noValidate className="mt-3 space-y-4">
                      {draftErrors.detail && <p role="alert" className="text-sm text-red-700">{draftErrors.detail}</p>}
                      <fieldset>
                        <legend className="text-sm font-medium text-slate-800">Tipo</legend>
                        <div className="mt-1 flex flex-wrap gap-4 text-sm text-slate-800">
                          {(["NOTA", "CONTRAOFERTA"] as const).map((type) => (
                            <label key={type} className="flex items-center gap-2">
                              <input
                                type="radio"
                                name="interaction_type"
                                checked={draft.interaction_type === type}
                                onChange={() => setDraft({ ...draft, interaction_type: type })}
                              />
                              {type === "NOTA" ? "Nota" : "Contraoferta"}
                            </label>
                          ))}
                        </div>
                        {draftErrors.interaction_type && <span className="block text-xs text-red-700">{draftErrors.interaction_type}</span>}
                      </fieldset>
                      <label className="block text-sm font-medium text-slate-800">
                        Observaciones
                        <AutoGrowTextarea
                          value={draft.notes}
                          onValueChange={(value) => setDraft({ ...draft, notes: value })}
                          maxLength={MAX_INTERACTION_NOTES}
                          invalid={Boolean(draftErrors.notes)}
                          placeholder="Qué se habló, acuerdos, próximos pasos…"
                        />
                        {draftErrors.notes && <span className="block text-xs text-red-700">{draftErrors.notes}</span>}
                      </label>
                      {draft.interaction_type === "CONTRAOFERTA" && (
                        <label className="block text-sm font-medium text-slate-800">
                          Precio ofrecido (USD)
                          <input
                            type="text"
                            inputMode="decimal"
                            placeholder="Ej.: 140000"
                            value={draft.offered_price}
                            onChange={(e) => setDraft({ ...draft, offered_price: e.target.value })}
                            aria-invalid={Boolean(draftErrors.offered_price)}
                            className={inputClass}
                          />
                          <span className="mt-1 block text-xs text-slate-500">No cambia el precio público de la propiedad.</span>
                          {draftErrors.offered_price && <span className="block text-xs text-red-700">{draftErrors.offered_price}</span>}
                        </label>
                      )}
                      {data.visits.length > 0 && (
                        <label className="block text-sm font-medium text-slate-800">
                          Visita relacionada (opcional)
                          <select
                            value={draft.visit}
                            onChange={(e) => setDraft({ ...draft, visit: e.target.value })}
                            className={inputClass}
                          >
                            <option value="">Ninguna</option>
                            {data.visits.map((visit) => (
                              <option key={visit.id} value={visit.id}>
                                {formatDateTime(visit.scheduled_start)} · {visit.status_display}
                              </option>
                            ))}
                          </select>
                          {draftErrors.visit && <span className="block text-xs text-red-700">{draftErrors.visit}</span>}
                        </label>
                      )}
                      <button
                        type="submit"
                        disabled={savingInteraction}
                        className="w-full rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
                      >
                        {savingInteraction ? "Guardando…" : "Registrar"}
                      </button>
                    </form>
                  )}
                </div>

                <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h2 className="text-lg font-bold text-slate-900">Visitas</h2>
                  {data.visits.length === 0 ? (
                    <p className="mt-2 text-sm text-slate-600">Sin visitas registradas.</p>
                  ) : (
                    <ul className="mt-2 space-y-2 text-sm">
                      {data.visits.map((visit) => (
                        <li key={visit.id} className="flex flex-wrap justify-between gap-2 text-slate-700">
                          <span>{formatDateTime(visit.scheduled_start)}</span>
                          <span className="font-semibold">{visit.status_display}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </section>
          </>
        )}
      </div>

      <Dialog
        open={confirming}
        title={`¿Avanzar a "${data?.next_status_display ?? ""}"?`}
        confirmLabel="Avanzar"
        tone="warning"
        busy={advancing}
        onConfirm={confirmAdvance}
        onCancel={() => setConfirming(false)}
      >
        <p>El cambio queda en el historial con tu usuario, fecha y hora, y no se puede deshacer manualmente.</p>
        {needsPrice && isPositiveAmount(finalPrice) && (
          <p className="mt-2">Precio final acordado: <span className="font-semibold">{formatMoney(finalPrice.trim())}</span></p>
        )}
      </Dialog>
    </main>
  );
}
