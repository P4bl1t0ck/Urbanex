"use client";

// Pantalla I-07 (HU-27): apertura manual de contacto y oportunidad para interesados que llegan
// por canales no integrados (llamadas, referidos). Reglas del servidor (DS-28): celular de
// Ecuador, aceptación de la política de privacidad, solo propiedades disponibles y una sola
// oportunidad activa por contacto e inmueble. La apertura queda en un historial que no se
// puede eliminar, por eso se confirma en un modal.

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import Dialog from "@/components/Dialog";
import { ApiError } from "@/lib/api";
import { getAgents, getEligibleProperties, openOpportunity } from "@/lib/opportunities";
import type {
  AgentOption,
  ContactSummary,
  EligibleProperty,
  OpportunityConflictBody,
  OpportunityOpenPayload,
} from "@/types/opportunity";

type Form = {
  full_name: string;
  phone: string;
  email: string;
  property: number | null;
  assigned_agent: string;
  privacy_accepted: boolean;
};

const EMPTY_FORM: Form = {
  full_name: "",
  phone: "",
  email: "",
  property: null,
  assigned_agent: "",
  privacy_accepted: false,
};

type Options = { properties: EligibleProperty[]; agents: AgentOption[]; isAdmin: boolean };

function formatMoney(value: string) {
  return Number(value).toLocaleString("es-EC", { style: "currency", currency: "USD" });
}

function fieldErrors(body: unknown): Record<string, string> {
  if (!body || typeof body !== "object" || Array.isArray(body)) return {};
  const result: Record<string, string> = {};
  for (const [key, value] of Object.entries(body as Record<string, unknown>)) {
    result[key] = Array.isArray(value) ? String(value[0]) : String(value);
  }
  return result;
}

export default function OpenOpportunityPage() {
  const router = useRouter();
  const [options, setOptions] = useState<Options | null>(null);
  const [loadError, setLoadError] = useState("");
  const [form, setForm] = useState<Form>(EMPTY_FORM);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [conflict, setConflict] = useState<OpportunityConflictBody | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [reused, setReused] = useState<{ opportunityId: number; contact: ContactSummary } | null>(null);

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
    if (!sessionStorage.getItem("access")) {
      router.replace("/login");
      return;
    }
    // El rol solo decide si se muestra el selector de asesor; el servidor lo valida (DS-28).
    const isAdmin = sessionStorage.getItem("userRole") === "admin";
    let isActive = true;

    async function load() {
      try {
        const [properties, agents] = await Promise.all([
          getEligibleProperties(),
          isAdmin ? getAgents() : Promise.resolve([] as AgentOption[]),
        ]);
        if (isActive) setOptions({ properties, agents, isAdmin });
      } catch (err) {
        if (!isActive || handleAuthError(err)) return;
        setLoadError(err instanceof Error ? err.message : "No se pudieron cargar las propiedades.");
      }
    }

    void load();
    return () => {
      isActive = false;
    };
  }, [router, handleAuthError]);

  function update<K extends keyof Form>(key: K, value: Form[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
    setConflict(null);
  }

  // Validación previa solo para guiar al asesor; la regla real la aplica el servidor.
  function requestConfirmation(event: FormEvent) {
    event.preventDefault();
    const missing: Record<string, string> = {};
    if (!form.full_name.trim()) missing.full_name = "Indique el nombre del interesado.";
    if (!form.phone.trim()) missing.phone = "Indique el celular del interesado.";
    if (form.property === null) missing.property = "Elija una propiedad disponible.";
    if (options?.isAdmin && !form.assigned_agent) missing.assigned_agent = "Elija el asesor responsable.";
    if (!form.privacy_accepted) {
      missing.privacy_accepted = "Confirme que el interesado aceptó la política de privacidad (LOPDP).";
    }
    setErrors(missing);
    setConflict(null);
    if (Object.keys(missing).length === 0) setConfirming(true);
  }

  async function submit() {
    if (form.property === null) return;
    setBusy(true);
    const payload: OpportunityOpenPayload = {
      full_name: form.full_name.trim(),
      phone: form.phone.trim(),
      email: form.email.trim(),
      property: form.property,
      privacy_accepted: form.privacy_accepted,
    };
    if (options?.isAdmin) payload.assigned_agent = Number(form.assigned_agent);
    try {
      const response = await openOpportunity(payload);
      const id = response.opportunity.id;
      if (response.contact_reused) {
        setConfirming(false);
        setBusy(false);
        setReused({ opportunityId: id, contact: response.opportunity.contact });
        return;
      }
      router.push(`/dashboard/opportunities?opened=${id}`);
    } catch (err) {
      setConfirming(false);
      setBusy(false);
      if (handleAuthError(err)) return;
      if (err instanceof ApiError && err.status === 409) {
        setConflict(err.body as OpportunityConflictBody);
        return;
      }
      if (err instanceof ApiError && err.status === 400) {
        setErrors(fieldErrors(err.body));
        return;
      }
      setErrors({ detail: err instanceof Error ? err.message : "Ocurrió un error inesperado." });
    }
  }

  const inputClass =
    "mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-600 focus:outline-none";
  const selected = options?.properties.find((p) => p.id === form.property);

  if (!options && !loadError) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <p className="mx-auto max-w-5xl animate-pulse text-slate-600">Cargando propiedades disponibles...</p>
      </main>
    );
  }

  if (loadError || !options) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <div className="mx-auto max-w-5xl space-y-4">
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {loadError || "No se pudieron cargar las propiedades."}
          </div>
          <Link href="/dashboard/opportunities" className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver a las oportunidades
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <header>
          <Link href="/dashboard/opportunities" className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver a las oportunidades
          </Link>
          <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">Seguimiento de oportunidades</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Abrir contacto y oportunidad</h1>
          <p className="mt-2 text-sm text-slate-600">
            Para interesados que llegan por llamada, referido u otro canal no integrado. La oportunidad nace en
            Contacto inicial{options.isAdmin ? " y queda a cargo del asesor que elijas" : " y queda a tu cargo"}.
          </p>
        </header>

        {conflict && (
          <div role="alert" className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-amber-900">
            {conflict.detail}
            {conflict.existing_opportunity_id && <> (oportunidad #{conflict.existing_opportunity_id}).</>}{" "}
            <Link
              href={`/dashboard/opportunities?property=${form.property ?? ""}`}
              className="font-semibold underline"
            >
              Ver oportunidades
            </Link>
          </div>
        )}
        {errors.detail && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {errors.detail}
          </div>
        )}

        <form onSubmit={requestConfirmation} noValidate className="space-y-6">
          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Interesado</h2>
            <div className="mt-4 grid gap-4 sm:grid-cols-3">
              <label className="text-sm font-medium text-slate-700">
                Nombre completo
                <input
                  className={inputClass}
                  value={form.full_name}
                  maxLength={150}
                  onChange={(e) => update("full_name", e.target.value)}
                  aria-invalid={Boolean(errors.full_name)}
                />
                {errors.full_name && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.full_name}</span>}
              </label>
              <label className="text-sm font-medium text-slate-700">
                Celular
                <input
                  className={inputClass}
                  value={form.phone}
                  inputMode="tel"
                  placeholder="09XXXXXXXX"
                  onChange={(e) => update("phone", e.target.value)}
                  aria-invalid={Boolean(errors.phone)}
                />
                <span className="mt-1 block text-xs text-slate-500">Celular de Ecuador: 09XXXXXXXX o +5939XXXXXXXX.</span>
                {errors.phone && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.phone}</span>}
              </label>
              <label className="text-sm font-medium text-slate-700">
                Correo (opcional)
                <input
                  type="email"
                  className={inputClass}
                  value={form.email}
                  onChange={(e) => update("email", e.target.value)}
                  aria-invalid={Boolean(errors.email)}
                />
                {errors.email && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.email}</span>}
              </label>
            </div>
            <p className="mt-3 text-xs text-slate-500">
              Si el celular ya está registrado, se usa el contacto existente con sus datos guardados.
            </p>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Propiedad de interés</h2>
            <p className="mt-1 text-xs text-slate-500">Solo propiedades disponibles en el catálogo.</p>
            {errors.property && <p role="alert" className="mt-2 text-sm text-red-700">{errors.property}</p>}
            {options.properties.length === 0 ? (
              <p className="mt-4 text-sm text-slate-600">No hay propiedades disponibles en este momento.</p>
            ) : (
              <div role="radiogroup" aria-label="Propiedad de interés" className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {options.properties.map((property) => {
                  const isSelected = property.id === form.property;
                  return (
                    <label
                      key={property.id}
                      className={`cursor-pointer overflow-hidden rounded-xl border bg-white transition ${
                        isSelected ? "border-blue-600 ring-2 ring-blue-600" : "border-slate-200 hover:border-slate-300"
                      }`}
                    >
                      <input
                        type="radio"
                        name="property"
                        className="sr-only"
                        checked={isSelected}
                        onChange={() => update("property", property.id)}
                      />
                      <div className="relative h-32 bg-slate-100">
                        {property.photo ? (
                          <Image src={property.photo} alt={property.title} fill unoptimized className="object-cover" sizes="(max-width: 640px) 100vw, 33vw" />
                        ) : (
                          <div className="flex h-full items-center justify-center text-xs text-slate-500">Sin foto</div>
                        )}
                      </div>
                      <div className="p-3">
                        <p className="line-clamp-1 font-semibold text-slate-900">{property.title}</p>
                        <p className="line-clamp-1 text-xs text-slate-600">
                          {property.sector} · {property.property_type_display}
                        </p>
                        <p className="mt-1 text-sm font-bold text-blue-800">{formatMoney(property.price)}</p>
                      </div>
                    </label>
                  );
                })}
              </div>
            )}
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            {options.isAdmin && (
              <label className="mb-4 block max-w-sm text-sm font-medium text-slate-700">
                Asesor responsable
                <select
                  className={inputClass}
                  value={form.assigned_agent}
                  onChange={(e) => update("assigned_agent", e.target.value)}
                  aria-invalid={Boolean(errors.assigned_agent)}
                >
                  <option value="">Elige un asesor activo</option>
                  {options.agents.map((agent) => (
                    <option key={agent.id} value={agent.id}>{agent.name}</option>
                  ))}
                </select>
                {errors.assigned_agent && <span role="alert" className="mt-1 block text-xs text-red-700">{errors.assigned_agent}</span>}
              </label>
            )}
            <label className="flex items-start gap-3 text-sm text-slate-700">
              <input
                type="checkbox"
                className="mt-0.5 h-4 w-4 accent-blue-700"
                checked={form.privacy_accepted}
                onChange={(e) => update("privacy_accepted", e.target.checked)}
                aria-invalid={Boolean(errors.privacy_accepted)}
              />
              <span>
                El interesado aceptó la política de privacidad (LOPDP). Se guardará la fecha y la hora de la aceptación.
              </span>
            </label>
            {errors.privacy_accepted && <p role="alert" className="mt-1 text-xs text-red-700">{errors.privacy_accepted}</p>}

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={busy}
                className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Abrir oportunidad
              </button>
              <Link href="/dashboard/opportunities" className="rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100">
                Cancelar
              </Link>
            </div>
          </section>
        </form>
      </div>

      <Dialog
        open={confirming}
        title="¿Abrir la oportunidad?"
        confirmLabel="Abrir oportunidad"
        busy={busy}
        onConfirm={() => void submit()}
        onCancel={() => setConfirming(false)}
      >
        <p>
          Se abrirá una oportunidad en Contacto inicial para <strong>{form.full_name.trim()}</strong> sobre{" "}
          <strong>{selected?.title}</strong>. La apertura queda registrada en el historial y no se puede eliminar.
        </p>
      </Dialog>

      <Dialog
        open={reused !== null}
        title="Se usó un contacto existente"
        confirmLabel="Ver oportunidades"
        tone="warning"
        onConfirm={() => reused && router.push(`/dashboard/opportunities?opened=${reused.opportunityId}`)}
      >
        {reused && (
          <p>
            El celular ya estaba registrado. La oportunidad #{reused.opportunityId} se abrió con el contacto guardado, cuyos
            datos no se modificaron: <strong>{reused.contact.full_name}</strong>, {reused.contact.phone}
            {reused.contact.email ? `, ${reused.contact.email}` : ""}.
          </p>
        )}
      </Dialog>
    </main>
  );
}
