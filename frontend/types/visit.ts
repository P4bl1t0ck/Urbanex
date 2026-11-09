// Contrato con backend/apps/visits (lote 2: HU-22, HU-18 y HU-24). Serializers en
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
};

export type AgendaResponse = {
  agent: number;
  from: string;
  to: string;
  timezone: string;
  visits: AgendaVisit[];
};
