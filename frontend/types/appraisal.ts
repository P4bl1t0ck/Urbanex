// Contrato de /api/appraisals/ (HU-04, HU-06, HU-08). Debe coincidir con AppraisalSerializer,
// AppraisalCreateSerializer, AppraisalCalibrateSerializer y la acción candidates/ en
// backend/apps/appraisals/.

import type { PropertyStatus } from "./property";

export type AppraisalStatus = "BORRADOR" | "APROBADO";

export type ConfidenceLevel = "ALTO" | "MEDIO" | "BAJO";

export type Appraisal = {
  id: string; // UUID
  folio: string; // AV-AAAAMMDD-XXXXXX (formato por confirmar, DT-42)
  property: number;
  agent: number;
  agent_name: string;
  status: AppraisalStatus;
  status_display: string;
  // Valor exacto del motor (DS-21); null en los registros manuales (DS-02).
  suggested_value: string | null; // DecimalField llega como string
  // El mismo valor redondeado a cientos: es el que se muestra (ajuste de Pablo, DS-21).
  suggested_value_display: string | null;
  confidence_level: ConfidenceLevel;
  confidence_level_display: string;
  is_manual_fallback: boolean;
  engine_parameters_version: number | null; // Versión de theta usada (HU-08)
  // [] en los avalúos anteriores al motor; objeto con la traza desde DS-21.
  comparables_snapshot: AppraisalSnapshot | [];
  ai_draft_justification: string; // Lo llenará HU-07
  calibrated_value: string | null;
  final_justification: string;
  // Solo se calculan al aprobar y si existe suggested_value.
  difference_amount: string | null;
  difference_percentage: string | null;
  created_at: string;
  approved_at: string | null;
};

// comparables_snapshot (apps/appraisals/engine/calculator.py). Los números llegan como texto.
export type SnapshotFactor = { key: string; value: string; detail: string };

export type SnapshotComparable = {
  id: number;
  property_type: string;
  status: string;
  price: string;
  area_m2: string;
  unit_price: string;
  // Solo cuando el motor calculó (no en la referencia manual de C-02).
  factors?: SnapshotFactor[];
  total_factor?: string;
  adjusted_unit_price?: string;
  weight?: string;
  deviation?: string;
  discarded?: boolean;
};

export type AppraisalSnapshot = {
  engine: string;
  parameters_version: number | null;
  comparables: SnapshotComparable[];
  manual_reason?: string;
  weighted_unit_price?: string;
  cv?: string;
};

// GET /api/appraisals/candidates/?property=<id> (HU-04, pantalla I-11)
export type ComparableCandidate = {
  id: number;
  title: string;
  property_type: string;
  status: PropertyStatus;
  location: string;
  price: string;
  area_m2: number;
  unit_price: string;
  distance_km: number;
};

export type CandidatesResponse = {
  property: { id: number; title: string; property_type: string; price: string; area_m2: number; has_coordinates: boolean };
  can_calculate: boolean;
  blocker: string | null;
  parameters_version: number | null;
  min_comparables: number;
  max_comparables: number;
  candidates: ComparableCandidate[];
  suggested_ids: number[];
};

// POST /api/appraisals/: sin comparables = registro manual (DS-02); con 3 a 5 calcula el motor.
export type AppraisalCreatePayload = {
  property: number;
  comparables?: number[];
};

// PATCH /api/appraisals/<id>/ (solo en BORRADOR)
export type AppraisalCalibratePayload = {
  calibrated_value?: string;
  final_justification?: string;
};

// 400 de POST /api/auth/properties/<id>/publish/ (get_missing_publication_requirements)
export type MissingRequirementCode = "image" | "brokerage_contract" | "appraisal";

export type MissingRequirement = {
  code: MissingRequirementCode;
  message: string;
};

export type PublishErrorResponse = {
  detail: string;
  missing_requirements?: MissingRequirement[];
};

// GET /api/auth/properties/<id>/publication-requirements/ (DS-15): misma regla que el 400.
export type PublicationRequirementsResponse = {
  status: PropertyStatus;
  can_publish: boolean;
  missing_requirements: MissingRequirement[];
};
