"use client";

// P-08 (HU-20): se consulta desde el navegador para que el límite por IP del servidor cuente al
// cliente y no al servidor de Next. Un enlace inexistente o vencido responde 404 (mismo mensaje).
// Muestra al asesor de la visita (nombre, apellido y teléfono; decisión de Pablo, 2026-11-09) y,
// si es otro, al asesor que lleva su seguimiento (DS-39).

// HU-21 (DS-52): botón "Cancelar visita" con confirmación, hasta 1 hora antes del inicio.

import Link from "next/link";
import { useEffect, useState } from "react";
import Dialog from "@/components/Dialog";
import { ApiError } from "@/lib/api";
import { cancelPublicVisit, getPublicVisit } from "@/lib/visits";
import { ecuadorDateOf, formatDayLabel, formatTime } from "@/lib/visitsCalendar";
import type { PublicAgent, PublicVisit } from "@/types/visit";

type State =
  | { kind: "loading" }
  | { kind: "ok"; visit: PublicVisit }
  | { kind: "not-found" }
  | { kind: "error"; message: string };

function AgentCard({ title, agent }: { title: string; agent: PublicAgent }) {
  const name = `${agent.first_name} ${agent.last_name}`.trim() || "Asesor de Urbanex";
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <p className="mt-1 font-semibold text-slate-900">{name}</p>
      {agent.phone ? (
        <a href={`tel:${agent.phone}`} className="mt-1 inline-block text-sm text-blue-700 hover:underline">
          {agent.phone}
        </a>
      ) : (
        <p className="mt-1 text-sm text-slate-500">Teléfono no registrado</p>
      )}
    </div>
  );
}

function cancelErrorMessage(err: unknown) {
  if (err instanceof ApiError) {
    if (err.status === 409) return "Esta visita ya no está programada.";
    if (err.status === 404) return "Este enlace no es válido o la visita ya comenzó.";
    if (err.status === 429) return "Hiciste muchas consultas seguidas. Espera un minuto y vuelve a intentar.";
    if (err.status === 400) return err.message || "Ya no se puede cancelar por el enlace. Comunícate con tu asesor.";
  }
  return "No se pudo cancelar tu visita. Intenta nuevamente.";
}

export default function PublicVisitView({ token }: { token: string }) {
  const [state, setState] = useState<State>({ kind: "loading" });
  const [confirming, setConfirming] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState("");
  const [cancelled, setCancelled] = useState(false);

  async function confirmCancel() {
    setCancelling(true);
    setCancelError("");
    try {
      const visit = await cancelPublicVisit(token);
      setState({ kind: "ok", visit });
      setCancelled(true);
    } catch (err) {
      setCancelError(cancelErrorMessage(err));
    } finally {
      setCancelling(false);
      setConfirming(false);
    }
  }

  useEffect(() => {
    let isActive = true;
    getPublicVisit(token)
      .then((visit) => {
        if (isActive) setState({ kind: "ok", visit });
      })
      .catch((err) => {
        if (!isActive) return;
        if (err instanceof ApiError && err.status === 404) {
          setState({ kind: "not-found" });
        } else if (err instanceof ApiError && err.status === 429) {
          setState({ kind: "error", message: "Hiciste muchas consultas seguidas. Espera un minuto y vuelve a intentar." });
        } else {
          setState({ kind: "error", message: "No se pudo cargar tu visita. Intenta nuevamente." });
        }
      });
    return () => {
      isActive = false;
    };
  }, [token]);

  return (
    <main className="mx-auto min-h-screen max-w-2xl px-4 py-10">
      <h1 className="text-2xl font-bold text-slate-900">Tu visita</h1>

      {state.kind === "loading" && <p className="mt-6 text-sm text-slate-500">Cargando…</p>}

      {state.kind === "not-found" && (
        <div className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="font-semibold text-slate-900">Este enlace no es válido o la visita ya comenzó.</p>
          <p className="mt-2 text-sm text-slate-600">
            Si necesitas ayuda con tu visita, comunícate con tu asesor.
          </p>
          <Link href="/properties" className="mt-4 inline-block text-sm font-semibold text-blue-700 hover:underline">
            Ver el catálogo
          </Link>
        </div>
      )}

      {state.kind === "error" && (
        <p role="alert" className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          {state.message}
        </p>
      )}

      {state.kind === "ok" && (
        <section className="mt-6 space-y-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Propiedad</p>
            <Link
              href={`/properties/${state.visit.property.id}`}
              className="mt-1 block text-lg font-semibold text-blue-800 hover:underline"
            >
              {state.visit.property.title}
            </Link>
            <p className="text-sm text-slate-600">{state.visit.property.location}</p>
          </div>

          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Fecha y hora</p>
              <p className="mt-1 font-semibold capitalize text-slate-900">
                {formatDayLabel(ecuadorDateOf(state.visit.scheduled_start))}
              </p>
              <p className="text-sm text-slate-700">
                {formatTime(state.visit.scheduled_start)} a {formatTime(state.visit.scheduled_end)} (hora de Ecuador)
              </p>
            </div>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-800">
              {state.visit.status_display}
            </span>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <AgentCard title="Asesor de la visita" agent={state.visit.visit_agent} />
            {state.visit.followup_agent && (
              <AgentCard title="Asesor de tu seguimiento" agent={state.visit.followup_agent} />
            )}
          </div>

          {cancelled && (
            <p role="status" className="rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">
              Tu visita quedó cancelada. Tu asesor ya fue avisado.
            </p>
          )}
          {cancelError && (
            <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">{cancelError}</p>
          )}

          {state.visit.can_cancel ? (
            <div className="space-y-2">
              <button
                type="button"
                onClick={() => setConfirming(true)}
                className="w-full rounded-lg border border-red-300 px-4 py-2 text-sm font-semibold text-red-700 hover:bg-red-50 sm:w-auto"
              >
                Cancelar visita
              </button>
              <p className="text-xs text-slate-500">
                Puedes cancelarla hasta el {formatDayLabel(ecuadorDateOf(state.visit.cancel_until))} a las{" "}
                {formatTime(state.visit.cancel_until)} (1 hora antes). Para cambiar la hora, comunícate con tu asesor.
              </p>
            </div>
          ) : state.visit.status === "PROGRAMADA" ? (
            <p className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
              Falta menos de 1 hora: para cancelar o cambiar tu visita, comunícate con tu asesor.
            </p>
          ) : null}
        </section>
      )}

      <Dialog
        open={confirming}
        title="¿Cancelar tu visita?"
        confirmLabel="Sí, cancelar"
        cancelLabel="Volver"
        tone="danger"
        busy={cancelling}
        onConfirm={confirmCancel}
        onCancel={() => setConfirming(false)}
      >
        <p>La hora quedará libre y no se puede deshacer. Si quieres otra hora, puedes agendarla de nuevo en la ficha de la propiedad.</p>
      </Dialog>
    </main>
  );
}
