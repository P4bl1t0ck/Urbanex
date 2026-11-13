// Llamadas a /api/opportunities/ (HU-27, HU-34; lote 4: HU-15, HU-16, HU-29, HU-30). Usa
// apiFetch y authFetch de lib/api.ts sin modificarlos.

import { apiFetch, authFetch } from "@/lib/api";
import type {
  AgentOption,
  EligibleProperty,
  Interaction,
  InteractionCreatePayload,
  MarkLostPayload,
  OpportunityDetail,
  OpportunityFilters,
  OpportunityOpenPayload,
  OpportunityOpenResponse,
  OpportunityPage,
  StatusChangePayload,
  WebInterestPayload,
  WebInterestResponse,
  WhatsAppContactResponse,
} from "@/types/opportunity";

const BASE = "/api/opportunities/";

export function listOpportunities(filters: OpportunityFilters, page = 1) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, value);
  }
  if (page > 1) params.set("page", String(page));
  const query = params.toString();
  return authFetch<OpportunityPage>(query ? `${BASE}?${query}` : BASE);
}

export function openOpportunity(payload: OpportunityOpenPayload) {
  return authFetch<OpportunityOpenResponse>(BASE, { method: "POST", body: JSON.stringify(payload) });
}

// mine: HU-23 (DS-52), el asesor solo ve las propiedades que atiende (el admin, todas).
export function getEligibleProperties(mine = false) {
  return authFetch<EligibleProperty[]>(`${BASE}eligible-properties/${mine ? "?mine=1" : ""}`);
}

// Solo el admin: el servidor responde 403 a un asesor.
export function getAgents() {
  return authFetch<AgentOption[]>(`${BASE}agents/`);
}

// HU-15 (P-07): público, sin token. 404 si la propiedad no está Disponible; 429 por exceso.
export function getWhatsAppContact(propertyId: number) {
  return apiFetch<WhatsAppContactResponse>(`${BASE}public/properties/${propertyId}/whatsapp/`, {
    cache: "no-store",
  });
}

// HU-16 (P-07): público, sin token. 400 datos, 404 no Disponible o sin asesor, 429 por exceso.
export function registerInterest(propertyId: number, payload: WebInterestPayload) {
  return apiFetch<WebInterestResponse>(`${BASE}public/properties/${propertyId}/interest/`, {
    method: "POST",
    body: JSON.stringify(payload),
    cache: "no-store",
  });
}

// I-06A. 404 si la oportunidad no es del asesor (o no existe).
export function getOpportunity(id: number | string) {
  return authFetch<OpportunityDetail>(`${BASE}${id}/`);
}

// HU-29: un solo paso; devuelve el detalle actualizado.
export function advanceOpportunity(id: number, payload: StatusChangePayload) {
  return authFetch<OpportunityDetail>(`${BASE}${id}/status/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// HU-30: NOTA o CONTRAOFERTA.
// HU-31 (DS-52): marca la oportunidad como Perdida; devuelve el detalle actualizado.
export function markOpportunityLost(id: number, payload: MarkLostPayload) {
  return authFetch<OpportunityDetail>(`${BASE}${id}/lose/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function createInteraction(id: number, payload: InteractionCreatePayload) {
  return authFetch<Interaction>(`${BASE}${id}/interactions/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
