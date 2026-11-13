// Llamadas a /api/visits/ (HU-22, HU-18, HU-24). Usa authFetch y apiFetch de lib/api.ts sin
// modificarlos. El selector de asesor del admin reutiliza getAgents() de lib/opportunities.ts.

import { apiFetch, authFetch } from "@/lib/api";
import type {
  AgendaResponse,
  AgendaStatusFilter,
  AgendaVisit,
  PublicVisit,
  VisitCancelPayload,
  VisitOutcomePayload,
  VisitRequestPayload,
  VisitRequestResponse,
  AvailabilityException,
  AvailabilityExceptionPayload,
  AvailabilityRule,
  AvailabilityRulePayload,
  FreeSlotsResponse,
} from "@/types/visit";

const BASE = "/api/visits/";

function withQuery(path: string, params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") query.set(key, String(value));
  }
  const text = query.toString();
  return text ? `${path}?${text}` : path;
}

// HU-22 (I-09). El admin filtra por asesor; al asesor el servidor le devuelve solo lo suyo.
export function listAvailability(agent?: number) {
  return authFetch<AvailabilityRule[]>(withQuery(`${BASE}availability/`, { agent }));
}

export function createAvailability(payload: AvailabilityRulePayload) {
  return authFetch<AvailabilityRule>(`${BASE}availability/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateAvailability(id: number, payload: Partial<AvailabilityRulePayload>) {
  return authFetch<AvailabilityRule>(`${BASE}availability/${id}/`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteAvailability(id: number) {
  return authFetch<null>(`${BASE}availability/${id}/`, { method: "DELETE" });
}

export function listExceptions(agent?: number) {
  return authFetch<AvailabilityException[]>(withQuery(`${BASE}exceptions/`, { agent }));
}

export function createException(payload: AvailabilityExceptionPayload) {
  return authFetch<AvailabilityException>(`${BASE}exceptions/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function deleteException(id: number) {
  return authFetch<null>(`${BASE}exceptions/${id}/`, { method: "DELETE" });
}

// HU-18 (P-07): público, sin token. Sin cache para reflejar las visitas en tiempo real.
export function getFreeSlots(propertyId: number, from?: string, to?: string) {
  return apiFetch<FreeSlotsResponse>(
    withQuery(`${BASE}properties/${propertyId}/free-slots/`, { from, to }),
    { cache: "no-store" },
  );
}

// HU-24 (I-08). El admin debe indicar el asesor (el servidor responde 400 si falta).
export function getAgenda(params: { from: string; to: string; agent?: number; status?: AgendaStatusFilter }) {
  return authFetch<AgendaResponse>(withQuery(`${BASE}agenda/`, params));
}

// HU-19 (P-07): público, sin token. 400 datos o franja ya ocupada, 409 visita ya programada,
// 429 demasiadas solicitudes.
export function requestVisit(propertyId: number, payload: VisitRequestPayload) {
  return apiFetch<VisitRequestResponse>(`${BASE}properties/${propertyId}/request/`, {
    method: "POST",
    body: JSON.stringify(payload),
    cache: "no-store",
  });
}

// HU-20 (P-08): público por enlace único; 404 si no existe o ya empezó la visita.
export function getPublicVisit(token: string) {
  return apiFetch<PublicVisit>(`${BASE}public/${encodeURIComponent(token)}/`, { cache: "no-store" });
}

// HU-21 (P-08, DS-52): público por enlace; hasta 1 hora antes. 400 fuera de plazo, 409 ya cancelada.
export function cancelPublicVisit(token: string) {
  return apiFetch<PublicVisit>(`${BASE}public/${encodeURIComponent(token)}/cancel/`, {
    method: "POST",
    cache: "no-store",
  });
}

// HU-21 (I-08, DS-52): el asesor de la visita o el admin, hasta la hora de inicio, con motivo.
export function cancelVisit(visitId: number, payload: VisitCancelPayload) {
  return authFetch<AgendaVisit>(`${BASE}${visitId}/cancel/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// HU-25 (I-08): una sola vez y después de la hora de inicio.
export function recordVisitOutcome(visitId: number, payload: VisitOutcomePayload) {
  return authFetch<AgendaVisit>(`${BASE}${visitId}/outcome/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
