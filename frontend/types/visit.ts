// Contrato con backend/apps/visits (lote 2: HU-22, HU-18 y HU-24; lote 3: HU-19, HU-20 y HU-25). Serializers en
// backend/apps/visits/serializers.py y respuestas de backend/apps/visits/views.py.

// 0 = lunes ... 6 = domingo (Weekday en models.py).
export type Weekday = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export const WEEKDAY_LABELS: Record<Weekday, string> = {
  0: "Lunes",
  1: "Martes",
  2: "Miércoles",
  3: "Jueves",
  4: "Viernes",
  5: "Sábado",
  6: "Domingo",
};

// HU-22: franja semanal. Horas "HH:MM:SS" (hora de Ecuador).
export type AvailabilityRule = {
  id: number;
  agent: number;
  agent_name: string;
  day_of_week: Weekday;
  day_name: string;
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
};

export type AvailabilityRulePayload = {
  agent?: number;
  day_of_week: Weekday;
  start_time: string;
  end_time: string;
  slot_duration_minutes: number;
};

// HU-22: sin horas = día completo.
export type AvailabilityException = {
  id: number;
  agent: number;
  agent_name: string;
  exception_date: string;
  start_time: string | null;
  end_time: string | null;
  is_full_day: boolean;
  reason: string;
};

export type AvailabilityExceptionPayload = {
  agent?: number;
  exception_date: string;
  start_time: string | null;
  end_time: string | null;
  reason: string;
};

// HU-18: respuesta pública mínima (solo franjas libres). start/end con -05:00.
export type FreeSlot = { start: string; end: string };

export type FreeSlotsResponse = {
  property: number;
  timezone: string;
  slots: FreeSlot[];
};

// HU-24: agenda del asesor.
export type VisitStatus = "PROGRAMADA" | "REALIZADA" | "NO_ASISTIDA" | "CANCELADA";

export const VISIT_STATUS_LABELS: Record<VisitStatus, string> = {
  PROGRAMADA: "Programada",
  REALIZADA: "Realizada",
  NO_ASISTIDA: "No asistida",
  CANCELADA: "Cancelada",
};

// "" = por defecto (todas menos canceladas); "all" = todas.
export type AgendaStatusFilter = "" | "all" | VisitStatus;

export type AgendaVisit = {
  id: number;
  scheduled_start: string;
  scheduled_end: string;
  status: VisitStatus;
  status_display: string;
  property: { id: number; title: string; location: string };
  client: { full_name: string; phone: string; email: string };
  opportunity: number;
  // Lote 3 (DS-39)
  needs_whatsapp_confirmation: boolean; // HU-20: no hubo confirmación por correo
  followup_agent_name: string | null; // Asesor de la oportunidad, si no es el de la visita
  can_record_outcome: boolean; // HU-25: Programada y ya empezó
  outcome_notes: string;
  outcome_recorded_at: string | null;
  outcome_recorded_by_name: string | null;
  can_cancel: boolean; // HU-21 y HU-23 (DS-52): Programada y antes de su inicio
};

// HU-21 (I-08): el asesor o el admin cancelan con motivo obligatorio.
export type VisitCancelPayload = { reason: string };

// HU-25: resultados que registra el asesor.
export type VisitOutcome = "REALIZADA" | "NO_ASISTIDA" | "CANCELADA";

export type VisitOutcomePayload = { status: VisitOutcome; outcome_notes: string };

// HU-19 (P-07): solicitud del cliente sin cuenta.
export type VisitRequestPayload = {
  start: string;
  full_name: string;
  phone: string;
  email: string;
  email_opt_in: boolean;
  privacy_accepted: boolean;
};

export type VisitRequestResponse = {
  detail: string;
  scheduled_start: string;
  scheduled_end: string;
  confirmation: "email" | "whatsapp";
};

// HU-20 (P-08): datos públicos por el enlace único.
export type PublicAgent = { first_name: string; last_name: string; phone: string };

export type PublicVisit = {
  scheduled_start: string;
  scheduled_end: string;
  status: VisitStatus;
  status_display: string;
  property: { id: number; title: string; location: string };
  visit_agent: PublicAgent;
  followup_agent: PublicAgent | null;
  can_cancel: boolean; // HU-21 (DS-52): hasta 1 hora antes del inicio
  cancel_until: string; // ISO con -05:00
};

export type AgendaResponse = {
  agent: number;
  from: string;
  to: string;
  timezone: string;
  visits: AgendaVisit[];
};
