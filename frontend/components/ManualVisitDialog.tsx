"use client";

// HU-23 (I-08, DS-52): visitas coordinadas por WhatsApp.
// - ManualVisitDialog: el asesor registra la visita (propiedad que atiende, franja libre con 30 min
//   de antelación, datos del cliente y LOPDP confirmada por el asesor). El contacto se reutiliza
//   por celular (DS-28); el servidor vuelve a comprobar la franja (sin doble reserva).
// - RescheduleVisitDialog: mueve una visita Programada a otra franja libre del mismo asesor.
// Si el cliente no dio correo, el historial de la oportunidad indica que se le avisa por WhatsApp.

import { useEffect, useState } from "react";
import Dialog from "@/components/Dialog";
import { ApiError } from "@/lib/api";
import { getEligibleProperties } from "@/lib/opportunities";
import { createCoordinatedVisit, getCoordinatedSlots, getRescheduleSlots, rescheduleVisit } from "@/lib/visits";
import { ecuadorDateOf, formatDayLabel, formatTime } from "@/lib/visitsCalendar";
import type { EligibleProperty } from "@/types/opportunity";
import type { AgendaVisit, FreeSlot } from "@/types/visit";

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-600 focus:outline-none";

function slotLabel(slot: FreeSlot) {
  return `${formatDayLabel(ecuadorDateOf(slot.start))} · ${formatTime(slot.start)}–${formatTime(slot.end)}`;
}

function errorText(err: unknown, fallback: string) {
  if (err instanceof ApiError && err.body && typeof err.body === "object" && !Array.isArray(err.body)) {
    const values = Object.values(err.body as Record<string, unknown>);
    const first = values[0];
    if (Array.isArray(first) && typeof first[0] === "string") return first[0];
    if (typeof first === "string") return first;
  }
  return err instanceof Error ? err.message : fallback;
}

type SlotsState = { key: string; slots: FreeSlot[]; error: string };

function SlotSelect({
  value,
  onChange,
  state,
  loading,
}: {
  value: string;
  onChange: (value: string) => void;
  state: SlotsState | null;
  loading: boolean;
}) {
  return (
    <label className="block text-sm font-semibold text-slate-700">
      Fecha y hora (próximos 14 días)
      <select value={value} onChange={(event) => onChange(event.target.value)} disabled={loading} className={inputClass}>
        <option value="">{loading ? "Cargando horarios…" : "Elige una franja libre…"}</option>
        {state?.slots.map((slot) => (
          <option key={slot.start} value={slot.start}>{slotLabel(slot)}</option>
        ))}
      </select>
      {state?.error && <span className="block text-xs text-red-700">{state.error}</span>}
      {!loading && state && !state.error && state.slots.length === 0 && (
        <span className="block text-xs text-slate-500">No hay franjas libres. Revisa la disponibilidad del asesor.</span>
      )}
    </label>
  );
}

type Draft = {
  property: string;
  start: string;
  full_name: string;
  phone: string;
  email: string;
  email_opt_in: boolean;
  privacy_accepted: boolean;
};

const EMPTY_DRAFT: Draft = {
  property: "",
  start: "",
  full_name: "",
  phone: "",
  email: "",
  email_opt_in: false,
  privacy_accepted: false,
};

export function ManualVisitDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: (visit: AgendaVisit) => void;
}) {
  const [properties, setProperties] = useState<EligibleProperty[] | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);
  const [slots, setSlots] = useState<SlotsState | null>(null);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open || properties) return;
    let isActive = true;
    getEligibleProperties(true)
      .then((rows) => {
        if (isActive) setProperties(rows);
      })
      .catch((err) => {
        if (isActive) setError(errorText(err, "No se pudieron cargar las propiedades."));
      });
    return () => {
      isActive = false;
    };
  }, [open, properties]);

  useEffect(() => {
    if (!open || !draft.property) return;
    let isActive = true;
    const key = draft.property;
    getCoordinatedSlots(Number(draft.property))
      .then((response) => {
        if (isActive) setSlots({ key, slots: response.slots, error: "" });
      })
      .catch((err) => {
        if (isActive) setSlots({ key, slots: [], error: errorText(err, "No se pudieron cargar los horarios.") });
      });
    return () => {
      isActive = false;
    };
  }, [open, draft.property]);

  const slotsLoading = Boolean(draft.property) && slots?.key !== draft.property;

  function close() {
    setDraft(EMPTY_DRAFT);
    setSlots(null);
    setError("");
    onClose();
  }

  async function submit() {
    if (!draft.property || !draft.start || !draft.full_name.trim() || !draft.phone.trim()) {
      setError("Elige la propiedad y la franja, y escribe el nombre y el celular del cliente.");
      return;
    }
    if (!draft.privacy_accepted) {
      setError("Confirma que el cliente aceptó la política de privacidad (LOPDP).");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const visit = await createCoordinatedVisit({ ...draft, property: Number(draft.property) });
      onCreated(visit);
      close();
    } catch (err) {
      setError(errorText(err, "No se pudo registrar la visita."));
      if (err instanceof ApiError && err.status === 400) setSlots(null); // La franja pudo ocuparse
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog
      open={open}
      title="Registrar visita coordinada"
      confirmLabel={saving ? "Guardando…" : "Registrar visita"}
      busy={saving}
      onConfirm={submit}
      onCancel={close}
    >
      <div className="space-y-3">
        <p className="text-xs text-slate-500">Para visitas acordadas por WhatsApp. Mínimo 30 minutos de antelación.</p>
        <label className="block text-sm font-semibold text-slate-700">
          Propiedad
          <select
            value={draft.property}
            onChange={(event) => {
              setDraft({ ...draft, property: event.target.value, start: "" });
              setSlots(null);
            }}
            className={inputClass}
          >
            <option value="">{properties ? "Elige la propiedad…" : "Cargando…"}</option>
            {properties?.map((property) => (
              <option key={property.id} value={property.id}>{property.title} · {property.sector}</option>
            ))}
          </select>
        </label>
        {draft.property && (
          <SlotSelect
            value={draft.start}
            onChange={(start) => setDraft({ ...draft, start })}
            state={slots?.key === draft.property ? slots : null}
            loading={slotsLoading}
          />
        )}
        <label className="block text-sm font-semibold text-slate-700">
          Nombre del cliente
          <input value={draft.full_name} maxLength={150} onChange={(e) => setDraft({ ...draft, full_name: e.target.value })} className={inputClass} />
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          Celular (Ecuador)
          <input
            value={draft.phone}
            inputMode="tel"
            placeholder="09XXXXXXXX"
            onChange={(e) => setDraft({ ...draft, phone: e.target.value })}
            className={inputClass}
          />
          <span className="block text-xs font-normal text-slate-500">Si el celular ya existe, se usa ese contacto sin cambiar sus datos.</span>
        </label>
        <label className="block text-sm font-semibold text-slate-700">
          Correo (opcional)
          <input type="email" value={draft.email} onChange={(e) => setDraft({ ...draft, email: e.target.value })} className={inputClass} />
        </label>
        <label className="flex items-start gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={draft.email_opt_in}
            onChange={(e) => setDraft({ ...draft, email_opt_in: e.target.checked })}
            className="mt-1"
          />
          Enviar la confirmación con el enlace de la visita a ese correo
        </label>
        <label className="flex items-start gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={draft.privacy_accepted}
            onChange={(e) => setDraft({ ...draft, privacy_accepted: e.target.checked })}
            className="mt-1"
          />
          El cliente aceptó la política de privacidad (LOPDP)
        </label>
        {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-2 text-sm text-red-800">{error}</p>}
      </div>
    </Dialog>
  );
}

export function RescheduleVisitDialog({
  visit,
  onClose,
  onRescheduled,
}: {
  visit: AgendaVisit | null;
  onClose: () => void;
  onRescheduled: (visit: AgendaVisit) => void;
}) {
  const [slots, setSlots] = useState<SlotsState | null>(null);
  const [start, setStart] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const key = visit ? String(visit.id) : "";

  useEffect(() => {
    if (!visit) return;
    let isActive = true;
    const requestKey = String(visit.id);
    getRescheduleSlots(visit.id)
      .then((response) => {
        if (isActive) setSlots({ key: requestKey, slots: response.slots, error: "" });
      })
      .catch((err) => {
        if (isActive) setSlots({ key: requestKey, slots: [], error: errorText(err, "No se pudieron cargar los horarios.") });
      });
    return () => {
      isActive = false;
    };
  }, [visit]);

  function close() {
    setSlots(null);
    setStart("");
    setError("");
    onClose();
  }

  async function submit() {
    if (!visit) return;
    if (!start) {
      setError("Elige la nueva franja.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      onRescheduled(await rescheduleVisit(visit.id, start));
      close();
    } catch (err) {
      setError(errorText(err, "No se pudo reprogramar la visita."));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog
      open={visit !== null}
      title="Reprogramar visita"
      confirmLabel={saving ? "Guardando…" : "Reprogramar"}
      busy={saving}
      onConfirm={submit}
      onCancel={close}
    >
      {visit && (
        <div className="space-y-3">
          <p>
            {visit.property.title} · {visit.client.full_name} · ahora:{" "}
            {formatDayLabel(ecuadorDateOf(visit.scheduled_start))} {formatTime(visit.scheduled_start)}
          </p>
          <SlotSelect value={start} onChange={setStart} state={slots?.key === key ? slots : null} loading={slots?.key !== key} />
          <p className="text-xs text-slate-500">
            {visit.needs_whatsapp_confirmation
              ? "El cliente no dio correo: avísale del cambio por WhatsApp (queda anotado en el historial)."
              : "Se avisará al cliente por correo con el mismo enlace de su visita."}
          </p>
          {error && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 p-2 text-sm text-red-800">{error}</p>}
        </div>
      )}
    </Dialog>
  );
}
