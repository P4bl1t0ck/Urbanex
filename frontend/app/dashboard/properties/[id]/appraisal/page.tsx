"use client";

// Pantalla I-12 (HU-08): calibrar y aprobar el avalúo de una propiedad.
// Ciclo en el servidor: POST (borrador) -> PATCH (calibración) -> POST approve/ (inmutable).
// Sin motor de cálculo (D-04): todo avalúo es un registro manual (DS-02), así que esta
// pantalla nunca muestra ni calcula un valor sugerido.

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ApiError, authFetch } from "@/lib/api";
import type { Appraisal, AppraisalCalibratePayload } from "@/types/appraisal";
import type { Property } from "@/types/property";

type FieldErrors = Partial<Record<"calibrated_value" | "final_justification" | "general", string>>;

const STATUS_LABELS: Record<string, string> = {
  captacion: "En captación",
  disponible: "Disponible",
  reservador: "Reservado",
  vendido: "Vendido",
  arrendado: "Arrendado",
  no_disponible: "No disponible",
};

// DecimalField(max_digits=12, decimal_places=2): hasta 10 enteros y 2 decimales.
const DECIMAL_PATTERN = /^\d{1,10}(\.\d{1,2})?$/;

const inputClass =
  "w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100";

function formatMoney(value: string | null) {
  if (value == null) return "—";
  return Number(value).toLocaleString("es-EC", { style: "currency", currency: "USD" });
}

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Date(value).toLocaleString("es-EC", { dateStyle: "medium", timeStyle: "short" });
}

function Field({ label, hint, error, children }: { label: string; hint?: string; error?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase text-slate-700">{label}</span>
      {children}
      {error ? (
        <span className="mt-1 block text-xs font-medium text-red-700">{error}</span>
      ) : (
        hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>
      )}
    </label>
  );
}

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-lg font-semibold text-slate-900">{title}</h2>
      {children}
    </section>
  );
}

// Convierte el 400 de DRF ({campo: ["mensaje"]} o ["mensaje"]) en un mensaje por campo.
function toFieldErrors(error: unknown): FieldErrors {
  if (error instanceof ApiError && error.body && typeof error.body === "object" && !Array.isArray(error.body)) {
    const body = error.body as Record<string, unknown>;
    const pick = (key: string) => {
      const value = body[key];
      return Array.isArray(value) ? String(value[0]) : typeof value === "string" ? value : undefined;
    };
    const fieldErrors: FieldErrors = {
      calibrated_value: pick("calibrated_value"),
      final_justification: pick("final_justification"),
    };
    const general = pick("property") ?? pick("non_field_errors") ?? pick("detail");
    if (general || (!fieldErrors.calibrated_value && !fieldErrors.final_justification)) {
      fieldErrors.general = general ?? error.message;
    }
    return fieldErrors;
  }
  return { general: error instanceof Error ? error.message : "Ocurrió un error inesperado." };
}

export default function AppraisalPage() {
  const { id: propertyId } = useParams<{ id: string }>();
  const router = useRouter();

  const [property, setProperty] = useState<Property | null>(null);
  const [appraisals, setAppraisals] = useState<Appraisal[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const [calibratedValue, setCalibratedValue] = useState("");
  const [justification, setJustification] = useState("");
  const [errors, setErrors] = useState<FieldErrors>({});
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState<"start" | "save" | "approve" | null>(null);

  // El servidor ordena por -created_at: el primero es el más reciente.
  const draft = appraisals.find((a) => a.status === "BORRADOR") ?? null;
  const latestApproved = appraisals.find((a) => a.status === "APROBADO") ?? null;
  const history = appraisals.filter((a) => a.status === "APROBADO");

  function fillForm(appraisal: Appraisal | null) {
    setCalibratedValue(appraisal?.calibrated_value ?? "");
    setJustification(appraisal?.final_justification ?? "");
    setErrors({});
  }

  function handleAuthError(error: unknown) {
    if (error instanceof ApiError && error.status === 401) {
      router.replace("/login");
      return true;
    }
    return false;
  }

  useEffect(() => {
    if (!sessionStorage.getItem("access")) {
      router.replace("/login");
      return;
    }

    let isActive = true;

    async function load() {
      try {
        const [propertyData, appraisalData] = await Promise.all([
          authFetch<Property>(`/api/auth/properties/${propertyId}/`),
          authFetch<Appraisal[]>(`/api/appraisals/?property=${propertyId}`),
        ]);
        if (!isActive) return;
        setProperty(propertyData);
        setAppraisals(appraisalData);
        fillForm(appraisalData.find((a) => a.status === "BORRADOR") ?? null);
      } catch (error) {
        if (!isActive || handleAuthError(error)) return;
        setLoadError(
          error instanceof ApiError && error.status === 404
            ? "La propiedad no existe o no tienes acceso a ella."
            : error instanceof Error
              ? error.message
              : "No se pudo cargar el avalúo.",
        );
      } finally {
        if (isActive) setLoading(false);
      }
    }

    void load();
    return () => {
      isActive = false;
    };
    // handleAuthError solo usa router, que ya es dependencia.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [propertyId, router]);

  // Reemplaza (o agrega al inicio) un avalúo en la lista local tras una respuesta del servidor.
  function upsertAppraisal(updated: Appraisal) {
    setAppraisals((prev) =>
      prev.some((a) => a.id === updated.id)
        ? prev.map((a) => (a.id === updated.id ? updated : a))
        : [updated, ...prev],
    );
  }

  async function handleStart() {
    setBusy("start");
    setNotice("");
    setErrors({});
    try {
      const created = await authFetch<Appraisal>("/api/appraisals/", {
        method: "POST",
        body: JSON.stringify({ property: Number(propertyId) }),
      });
      upsertAppraisal(created);
      fillForm(created);
      setNotice(`Avalúo ${created.folio} iniciado como borrador.`);
    } catch (error) {
      if (!handleAuthError(error)) setErrors(toFieldErrors(error));
    } finally {
      setBusy(null);
    }
  }

  function validateLocally(): FieldErrors {
    const local: FieldErrors = {};
    const value = calibratedValue.trim();
    if (value && (!DECIMAL_PATTERN.test(value) || Number(value) <= 0)) {
      local.calibrated_value = "Ingresa un valor mayor a 0, con máximo 2 decimales y sin separadores de miles.";
    }
    if (!value && !justification.trim()) {
      local.general = "Ingresa el valor calibrado o la justificación antes de guardar.";
    }
    return local;
  }

  async function handleSave() {
    if (!draft) return;
    const local = validateLocally();
    setErrors(local);
    setNotice("");
    if (Object.keys(local).length > 0) return;

    // El serializer no acepta una justificación vacía: solo se envía lo que tiene contenido.
    const payload: AppraisalCalibratePayload = {};
    if (calibratedValue.trim()) payload.calibrated_value = calibratedValue.trim();
    if (justification.trim()) payload.final_justification = justification.trim();

    setBusy("save");
    try {
      const updated = await authFetch<Appraisal>(`/api/appraisals/${draft.id}/`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      upsertAppraisal(updated);
      fillForm(updated);
      setNotice("Borrador guardado.");
    } catch (error) {
      if (!handleAuthError(error)) setErrors(toFieldErrors(error));
    } finally {
      setBusy(null);
    }
  }

  async function handleApprove() {
    if (!draft) return;
    const confirmed = confirm(
      `¿Aprobar el avalúo ${draft.folio} por ${formatMoney(draft.calibrated_value)}?\n\n` +
        "Esta acción es irreversible: un avalúo aprobado no se puede modificar ni eliminar. " +
        "Para recalibrar tendrás que crear una reevaluación.",
    );
    if (!confirmed) return;

    setBusy("approve");
    setNotice("");
    setErrors({});
    try {
      const approved = await authFetch<Appraisal>(`/api/appraisals/${draft.id}/approve/`, { method: "POST" });
      upsertAppraisal(approved);
      fillForm(null);
      setNotice(`Avalúo ${approved.folio} aprobado.`);
    } catch (error) {
      if (!handleAuthError(error)) setErrors(toFieldErrors(error));
    } finally {
      setBusy(null);
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <p className="mx-auto max-w-4xl animate-pulse text-slate-600">Cargando avalúo...</p>
      </main>
    );
  }

  if (loadError || !property) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <div className="mx-auto max-w-4xl space-y-4">
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {loadError || "No se pudo cargar la propiedad."}
          </div>
          <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver a mis propiedades
          </Link>
        </div>
      </main>
    );
  }

  const isDirty =
    !!draft &&
    (calibratedValue.trim() !== (draft.calibrated_value ?? "") ||
      justification.trim() !== draft.final_justification);
  const canApprove = !!draft && !!draft.calibrated_value && !!draft.final_justification.trim() && !isDirty;
  const shown = draft ?? latestApproved;

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-4xl space-y-6">
        <header>
          <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">
            ← Volver a mis propiedades
          </Link>
          <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">Avalúo comercial</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">{property.title}</h1>
          <p className="mt-2 flex flex-wrap items-center gap-2 text-slate-600">
            <span>{property.location}</span>
            <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
              {STATUS_LABELS[property.status] ?? property.status}
            </span>
          </p>
        </header>

        {notice && (
          <div role="status" className="rounded-lg border border-green-200 bg-green-50 p-4 text-green-800">
            {notice}
          </div>
        )}
        {errors.general && (
          <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">
            {errors.general}
          </div>
        )}

        {/* Referencia para el asesor: no es un resultado del motor (D-04). */}
        <Card title="Referencia">
          <Field
            label="Precio actual de publicación"
            hint="Solo referencia. No es un valor sugerido: el motor de cálculo aún no está definido (D-04)."
          >
            <input
              type="text"
              value={formatMoney(property.price)}
              disabled
              readOnly
              className="w-full cursor-not-allowed rounded-lg border border-slate-200 bg-slate-100 p-2.5 text-sm text-slate-500"
            />
          </Field>
        </Card>

        {!shown ? (
          <Card title="Sin avalúos">
            <p className="text-sm text-slate-600">
              Esta propiedad todavía no tiene avalúos. Al iniciarlo se crea un borrador con folio propio que no se
              puede eliminar; podrás calibrarlo y, cuando esté listo, aprobarlo.
            </p>
            <button
              type="button"
              onClick={handleStart}
              disabled={busy !== null}
              className="mt-4 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busy === "start" ? "Iniciando..." : "Iniciar avalúo"}
            </button>
          </Card>
        ) : (
          <>
            <Card title={`Resultado del motor · ${shown.folio}`}>
              <dl className="grid gap-4 sm:grid-cols-3">
                <div>
                  <dt className="text-xs font-semibold uppercase text-slate-500">Valor sugerido</dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {shown.suggested_value != null ? formatMoney(shown.suggested_value) : "No disponible (D-04)"}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-slate-500">Nivel de confianza</dt>
                  <dd className="mt-1">
                    <span className="inline-flex rounded-full bg-amber-50 px-3 py-1 text-xs font-semibold text-amber-800">
                      {shown.confidence_level_display}
                    </span>
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-semibold uppercase text-slate-500">Origen</dt>
                  <dd className="mt-1 text-sm text-slate-700">
                    {shown.is_manual_fallback ? "Registro manual" : "Motor paramétrico"}
                  </dd>
                </div>
              </dl>
              <p className="mt-4 text-xs text-slate-500">
                {shown.comparables_snapshot.length === 0 && "Sin comparables seleccionados (HU-04). "}
                {!shown.ai_draft_justification && "Sin borrador de justificación de IA (HU-07). "}
                El valor final lo define el asesor.
              </p>
            </Card>

            {draft ? (
              <Card title="Calibración del asesor">
                <div className="space-y-4">
                  <Field
                    label="Valor calibrado (USD)"
                    hint="Valor comercial que propones. Ejemplo: 125000.00"
                    error={errors.calibrated_value}
                  >
                    <input
                      type="text"
                      inputMode="decimal"
                      value={calibratedValue}
                      onChange={(e) => setCalibratedValue(e.target.value)}
                      placeholder="0.00"
                      className={inputClass}
                    />
                  </Field>
                  <Field
                    label="Justificación final"
                    hint="Obligatoria para aprobar. Explica cómo llegaste al valor."
                    error={errors.final_justification}
                  >
                    <textarea
                      value={justification}
                      onChange={(e) => setJustification(e.target.value)}
                      rows={6}
                      className={inputClass}
                    />
                  </Field>
                </div>

                <div className="mt-6 flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={handleSave}
                    disabled={busy !== null || !isDirty}
                    className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {busy === "save" ? "Guardando..." : "Guardar borrador"}
                  </button>
                  <button
                    type="button"
                    onClick={handleApprove}
                    disabled={busy !== null || !canApprove}
                    className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {busy === "approve" ? "Aprobando..." : "Aprobar avalúo"}
                  </button>
                </div>
                {!canApprove && (
                  <p className="mt-3 text-xs text-slate-500">
                    {isDirty
                      ? "Guarda los cambios antes de aprobar."
                      : "Para aprobar, guarda un valor calibrado y una justificación."}
                  </p>
                )}
              </Card>
            ) : (
              latestApproved && (
                <Card title="Avalúo aprobado">
                  <dl className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <dt className="text-xs font-semibold uppercase text-slate-500">Valor calibrado</dt>
                      <dd className="mt-1 text-lg font-semibold text-slate-900">
                        {formatMoney(latestApproved.calibrated_value)}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs font-semibold uppercase text-slate-500">Diferencia con el motor</dt>
                      <dd className="mt-1 text-sm text-slate-700">
                        {latestApproved.difference_amount != null
                          ? `${formatMoney(latestApproved.difference_amount)} (${latestApproved.difference_percentage} %)`
                          : "No aplica (sin valor del motor)"}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs font-semibold uppercase text-slate-500">Aprobado</dt>
                      <dd className="mt-1 text-sm text-slate-700">{formatDate(latestApproved.approved_at)}</dd>
                    </div>
                    <div>
                      <dt className="text-xs font-semibold uppercase text-slate-500">Asesor</dt>
                      <dd className="mt-1 text-sm text-slate-700">{latestApproved.agent_name}</dd>
                    </div>
                    <div className="sm:col-span-2">
                      <dt className="text-xs font-semibold uppercase text-slate-500">Justificación</dt>
                      <dd className="mt-1 whitespace-pre-line text-sm text-slate-700">
                        {latestApproved.final_justification}
                      </dd>
                    </div>
                  </dl>
                  <p className="mt-4 text-xs text-slate-500">
                    Un avalúo aprobado no se puede modificar. Si el valor cambió, crea una reevaluación.
                  </p>
                  <button
                    type="button"
                    onClick={handleStart}
                    disabled={busy !== null}
                    className="mt-4 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {busy === "start" ? "Creando..." : "Crear reevaluación"}
                  </button>
                </Card>
              )
            )}
          </>
        )}

        {history.length > 0 && (
          <Card title="Historial de avalúos aprobados">
            <ul className="divide-y divide-slate-100">
              {history.map((a) => (
                <li key={a.id} className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm">
                  <span className="font-medium text-slate-800">{a.folio}</span>
                  <span className="text-slate-700">{formatMoney(a.calibrated_value)}</span>
                  <span className="text-slate-500">{formatDate(a.approved_at)}</span>
                  <span className="text-slate-500">{a.agent_name}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </div>
    </main>
  );
}
