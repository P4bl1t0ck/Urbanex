"use client";

// P-07 (HU-19, RF-04): formulario para solicitar la visita en la franja elegida en
// FreeSlotsPicker. El cliente no tiene cuenta. Pide nombre, celular de Ecuador (DS-28), la
// aceptación de la política de privacidad (LOPDP) y, opcionalmente, un correo con la casilla
// para recibir la confirmación (HU-20). La respuesta del servidor es la misma exista o no el
// contacto, y no trae datos del asesor ni el enlace de P-08: ese llega solo por correo (DS-39).

import { useState } from "react";
import { ApiError } from "@/lib/api";
import { requestVisit } from "@/lib/visits";
import { ecuadorDateOf, formatDayLabel, formatTime } from "@/lib/visitsCalendar";
import type { FreeSlot, VisitRequestPayload, VisitRequestResponse } from "@/types/visit";

type FieldErrors = Partial<Record<keyof VisitRequestPayload | "general", string>>;

const EMPTY = { full_name: "", phone: "", email: "", email_opt_in: false, privacy_accepted: false };

function firstMessage(value: unknown): string | undefined {
  if (typeof value === "string") return value;
  if (Array.isArray(value) && typeof value[0] === "string") return value[0];
  return undefined;
}

function errorsFrom(err: unknown): FieldErrors {
  if (!(err instanceof ApiError)) return { general: "No se pudo enviar la solicitud. Intenta nuevamente." };
  if (err.status === 429) {
    return { general: "Hiciste varias solicitudes seguidas. Espera un momento y vuelve a intentar." };
  }
  if (err.status === 404) return { general: "Esta propiedad ya no admite visitas." };
  const body = (err.body && typeof err.body === "object" ? err.body : {}) as Record<string, unknown>;
  const errors: FieldErrors = {};
  for (const key of ["full_name", "phone", "email", "privacy_accepted", "start"] as const) {
    const message = firstMessage(body[key]);
    if (message) errors[key] = message;
  }
  if (Object.keys(errors).length === 0) errors.general = err.message;
  return errors;
}

export default function VisitRequestForm({
  propertyId,
  slot,
  onCancel,
  onDone,
}: {
  propertyId: number;
  slot: FreeSlot;
  onCancel: () => void;
  onDone: (result: VisitRequestResponse | null) => void;
}) {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [sending, setSending] = useState(false);

  function update<K extends keyof typeof EMPTY>(key: K, value: (typeof EMPTY)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const missing: FieldErrors = {};
    if (!form.full_name.trim()) missing.full_name = "Indica tu nombre.";
    if (!form.phone.trim()) missing.phone = "Indica tu celular.";
    if (form.email_opt_in && !form.email.trim()) {
      missing.email = "Para recibir la confirmación por correo, indica tu correo.";
    }
    if (!form.privacy_accepted) missing.privacy_accepted = "Debes aceptar la política de privacidad (LOPDP).";
    setErrors(missing);
    if (Object.keys(missing).length > 0) return;

    setSending(true);
    try {
      const result = await requestVisit(propertyId, { ...form, start: slot.start });
      onDone(result);
    } catch (err) {
      const found = errorsFrom(err);
      if (err instanceof ApiError && err.status === 409) {
        found.general = err.message;
      }
      setErrors(found);
      // La franja ya no está libre: se refrescan los horarios para elegir otra.
      if (found.start) onDone(null);
    } finally {
      setSending(false);
    }
  }

  const fieldClass = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none";

  return (
    <form onSubmit={submit} noValidate className="mt-6 rounded-xl border border-blue-200 bg-blue-50/40 p-5" aria-labelledby="visit-request-title">
      <h3 id="visit-request-title" className="text-lg font-bold text-slate-900">Solicitar visita</h3>
      <p className="mt-1 text-sm text-slate-700">
        <span className="font-semibold capitalize">{formatDayLabel(ecuadorDateOf(slot.start))}</span>
        {" a las "}
        <span className="font-semibold">{formatTime(slot.start)}</span> (hora de Ecuador)
      </p>

      {errors.general && (
        <p role="alert" className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{errors.general}</p>
      )}
      {errors.start && (
        <p role="alert" className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{errors.start}</p>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-slate-800">
          Nombre completo
          <input
            type="text"
            autoComplete="name"
            maxLength={150}
            value={form.full_name}
            onChange={(e) => update("full_name", e.target.value)}
            aria-invalid={Boolean(errors.full_name)}
            className={fieldClass}
          />
          {errors.full_name && <span className="mt-1 block text-xs text-red-700">{errors.full_name}</span>}
        </label>
        <label className="block text-sm font-medium text-slate-800">
          Celular
          <input
            type="tel"
            autoComplete="tel"
            placeholder="09XXXXXXXX"
            value={form.phone}
            onChange={(e) => update("phone", e.target.value)}
            aria-invalid={Boolean(errors.phone)}
            className={fieldClass}
          />
          {errors.phone && <span className="mt-1 block text-xs text-red-700">{errors.phone}</span>}
        </label>
        <label className="block text-sm font-medium text-slate-800 sm:col-span-2">
          Correo (opcional)
          <input
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            aria-invalid={Boolean(errors.email)}
            className={fieldClass}
          />
          {errors.email && <span className="mt-1 block text-xs text-red-700">{errors.email}</span>}
        </label>
      </div>

      <label className="mt-4 flex items-start gap-2 text-sm text-slate-800">
        <input
          type="checkbox"
          checked={form.email_opt_in}
          onChange={(e) => update("email_opt_in", e.target.checked)}
          className="mt-0.5"
        />
        <span>Quiero recibir la confirmación de la visita en mi correo. Si no la marcas, el asesor te confirmará por WhatsApp.</span>
      </label>
      <label className="mt-3 flex items-start gap-2 text-sm text-slate-800">
        <input
          type="checkbox"
          checked={form.privacy_accepted}
          onChange={(e) => update("privacy_accepted", e.target.checked)}
          aria-invalid={Boolean(errors.privacy_accepted)}
          className="mt-0.5"
        />
        <span>Acepto la política de privacidad (LOPDP) y el tratamiento de mis datos para coordinar la visita.</span>
      </label>
      {errors.privacy_accepted && <p className="mt-1 text-xs text-red-700">{errors.privacy_accepted}</p>}

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          type="submit"
          disabled={sending}
          className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
        >
          {sending ? "Enviando…" : "Confirmar solicitud"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={sending}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-60"
        >
          Elegir otro horario
        </button>
      </div>
    </form>
  );
}
