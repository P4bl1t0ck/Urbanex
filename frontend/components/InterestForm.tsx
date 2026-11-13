"use client";

// P-07 (HU-16, RF-03, DS-50): formulario público de interés. Pide nombre, celular de Ecuador
// (DS-28), correo opcional con casilla para recibir novedades, mensaje opcional (máximo 1000
// caracteres, campo que crece con el texto) y la aceptación obligatoria de la política de
// privacidad (LOPDP). La respuesta del servidor es siempre la misma: no revela si el contacto
// ya existía. Si la propiedad deja de estar Disponible o no tiene asesor activo, responde 404.

import { useState } from "react";
import AutoGrowTextarea from "@/components/AutoGrowTextarea";
import { ApiError } from "@/lib/api";
import { registerInterest } from "@/lib/opportunities";
import { MAX_INTEREST_MESSAGE } from "@/lib/opportunityPipeline";
import type { WebInterestPayload } from "@/types/opportunity";

type FieldErrors = Partial<Record<keyof WebInterestPayload | "general", string>>;

const EMPTY: WebInterestPayload = {
  full_name: "",
  phone: "",
  email: "",
  email_opt_in: false,
  message: "",
  privacy_accepted: false,
};

function firstMessage(value: unknown): string | undefined {
  if (typeof value === "string") return value;
  if (Array.isArray(value) && typeof value[0] === "string") return value[0];
  return undefined;
}

function errorsFrom(err: unknown): FieldErrors {
  if (!(err instanceof ApiError)) return { general: "No se pudo enviar tu interés. Intenta nuevamente." };
  if (err.status === 429) {
    return { general: "Enviaste varias solicitudes seguidas. Espera un momento y vuelve a intentar." };
  }
  if (err.status === 404) return { general: "Esta propiedad ya no recibe solicitudes por este medio." };
  const body = (err.body && typeof err.body === "object" ? err.body : {}) as Record<string, unknown>;
  const errors: FieldErrors = {};
  for (const key of ["full_name", "phone", "email", "message", "privacy_accepted"] as const) {
    const message = firstMessage(body[key]);
    if (message) errors[key] = message;
  }
  if (Object.keys(errors).length === 0) errors.general = err.message;
  return errors;
}

export default function InterestForm({ propertyId }: { propertyId: number }) {
  const [form, setForm] = useState<WebInterestPayload>(EMPTY);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [sending, setSending] = useState(false);
  const [done, setDone] = useState("");

  function update<K extends keyof WebInterestPayload>(key: K, value: WebInterestPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const missing: FieldErrors = {};
    if (!form.full_name.trim()) missing.full_name = "Indica tu nombre.";
    if (!form.phone.trim()) missing.phone = "Indica tu celular.";
    if (form.email_opt_in && !form.email.trim()) {
      missing.email = "Para recibir novedades por correo, indica tu correo.";
    }
    if (!form.privacy_accepted) missing.privacy_accepted = "Debes aceptar la política de privacidad (LOPDP).";
    setErrors(missing);
    if (Object.keys(missing).length > 0) return;

    setSending(true);
    try {
      const result = await registerInterest(propertyId, form);
      setDone(result.detail);
      setForm(EMPTY);
    } catch (err) {
      setErrors(errorsFrom(err));
    } finally {
      setSending(false);
    }
  }

  const fieldClass =
    "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none";

  if (done) {
    return (
      <section className="mt-8 rounded-xl border border-green-200 bg-green-50 p-5" aria-live="polite">
        <h2 className="text-lg font-bold text-green-900">¡Gracias!</h2>
        <p className="mt-1 text-sm text-green-900">{done}</p>
        <button
          type="button"
          onClick={() => setDone("")}
          className="mt-3 text-sm font-semibold text-green-800 underline hover:text-green-950"
        >
          Enviar otro mensaje
        </button>
      </section>
    );
  }

  return (
    <form
      onSubmit={submit}
      noValidate
      className="mt-8 rounded-xl border border-slate-200 bg-slate-50 p-5"
      aria-labelledby="interest-form-title"
    >
      <h2 id="interest-form-title" className="text-xl font-bold text-slate-900">
        ¿Te interesa esta propiedad?
      </h2>
      <p className="mt-1 text-sm text-slate-600">Déjanos tus datos y el asesor se comunicará contigo.</p>

      {errors.general && (
        <p role="alert" className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">
          {errors.general}
        </p>
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
        <label className="block text-sm font-medium text-slate-800 sm:col-span-2">
          Mensaje (opcional)
          <AutoGrowTextarea
            value={form.message}
            onValueChange={(value) => update("message", value)}
            maxLength={MAX_INTEREST_MESSAGE}
            invalid={Boolean(errors.message)}
            placeholder="Por ejemplo: ¿aceptan crédito hipotecario?"
          />
          {errors.message && <span className="block text-xs text-red-700">{errors.message}</span>}
        </label>
      </div>

      <label className="mt-2 flex items-start gap-2 text-sm text-slate-800">
        <input
          type="checkbox"
          checked={form.email_opt_in}
          onChange={(e) => update("email_opt_in", e.target.checked)}
          className="mt-0.5"
        />
        <span>Quiero recibir novedades de propiedades en mi correo.</span>
      </label>
      <label className="mt-3 flex items-start gap-2 text-sm text-slate-800">
        <input
          type="checkbox"
          checked={form.privacy_accepted}
          onChange={(e) => update("privacy_accepted", e.target.checked)}
          aria-invalid={Boolean(errors.privacy_accepted)}
          className="mt-0.5"
        />
        <span>Acepto la política de privacidad (LOPDP) y el tratamiento de mis datos para que el asesor me contacte.</span>
      </label>
      {errors.privacy_accepted && <p className="mt-1 text-xs text-red-700">{errors.privacy_accepted}</p>}

      <button
        type="submit"
        disabled={sending}
        className="mt-5 w-full rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60 sm:w-auto"
      >
        {sending ? "Enviando…" : "Enviar mi interés"}
      </button>
    </form>
  );
}
