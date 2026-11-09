// Llamadas a /api/visits/ (HU-22, HU-18, HU-24). Usa authFetch y apiFetch de lib/api.ts sin
// modificarlos. El selector de asesor del admin reutiliza getAgents() de lib/opportunities.ts.

import { apiFetch, authFetch } from "@/lib/api";
import type {
  AgendaResponse,
  AgendaStatusFilter,
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
