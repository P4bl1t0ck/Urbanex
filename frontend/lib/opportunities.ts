// Llamadas a /api/opportunities/ (HU-27, HU-34). Usa authFetch de lib/api.ts sin modificarlo.

import { authFetch } from "@/lib/api";
import type {
  AgentOption,
  EligibleProperty,
  OpportunityFilters,
  OpportunityOpenPayload,
  OpportunityOpenResponse,
  OpportunityPage,
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

export function getEligibleProperties() {
  return authFetch<EligibleProperty[]>(`${BASE}eligible-properties/`);
}

// Solo el admin: el servidor responde 403 a un asesor.
export function getAgents() {
  return authFetch<AgentOption[]>(`${BASE}agents/`);
}
