// Contrato de /api/opportunities/ (HU-27, HU-34). Debe coincidir con OpportunitySerializer,
// OpportunityOpenSerializer, EligiblePropertySerializer y AgentOptionSerializer en
// backend/apps/opportunities/serializers.py.

export type OpportunityStatus =
  | "CONTACTO_INICIAL"
  | "LISTA_INTERESADOS"
  | "VISITA_PROGRAMADA"
  | "EN_NEGOCIACION"
  | "RESERVADA"
  | "EVALUACION_DOCUMENTAL"
  | "PENDIENTE_CIERRE"
  | "PENDIENTE_COMISION"
  | "CIERRE"
  | "PERDIDA";

export const OPPORTUNITY_STATUS_LABELS: Record<OpportunityStatus, string> = {
  CONTACTO_INICIAL: "Contacto inicial",
  LISTA_INTERESADOS: "Lista de interesados",
  VISITA_PROGRAMADA: "Visita programada",
  EN_NEGOCIACION: "En negociación",
  RESERVADA: "Reservada",
  EVALUACION_DOCUMENTAL: "Evaluación documental",
  PENDIENTE_CIERRE: "Pendiente de cierre",
  PENDIENTE_COMISION: "Pendiente de comisión",
  CIERRE: "Cierre",
  PERDIDA: "Perdida",
};

export type OriginChannel =
  | "CATALOGO_WEB"
  | "WHATSAPP"
  | "MESSENGER"
  | "CAMPANA"
  | "INTERES_RESERVADA"
  | "MANUAL";

export type ContactSummary = {
  id: number;
  full_name: string;
  phone: string; // Normalizado: +5939XXXXXXXX (DS-28)
  email: string;
};

export type Opportunity = {
  id: number;
  status: OpportunityStatus;
  status_display: string;
  origin_channel: OriginChannel;
  origin_channel_display: string;
  contact: ContactSummary;
  property: { id: number; title: string; sector: string; property_type: string };
  assigned_agent: { id: number; name: string };
  last_activity_at: string; // ISO 8601 (UTC)
  created_at: string; // ISO 8601 (UTC)
};

// Respuesta paginada de GET /api/opportunities/ (PageNumberPagination, 20 por página).
export type OpportunityPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Opportunity[];
};

export type OpportunityFilters = {
  assigned_agent?: string;
  property?: string;
  status?: OpportunityStatus | "";
  created_from?: string; // AAAA-MM-DD, hora de Ecuador
  created_to?: string;
};

export type OpportunityOpenPayload = {
  full_name: string;
  phone: string;
  email?: string;
  property: number;
  privacy_accepted: boolean;
  assigned_agent?: number | null; // Solo el admin (DS-28)
};

export type OpportunityOpenResponse = {
  opportunity: Opportunity;
  contact_reused: boolean;
};

// 409 de POST /api/opportunities/: ya hay una oportunidad activa para el contacto y el inmueble.
export type OpportunityConflictBody = {
  detail: string;
  existing_opportunity_id: number | null;
};

// Selector de I-07: solo datos públicos del catálogo (DS-28, DT-39, SEC-03).
export type EligibleProperty = {
  id: number;
  title: string;
  sector: string;
  property_type: string;
  property_type_display: string;
  price: string; // DecimalField llega como string
  photo: string | null;
};

export type AgentOption = {
  id: number;
  name: string;
};
