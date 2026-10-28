// Contrato de /api/appraisals/ (HU-08). Debe coincidir con AppraisalSerializer y
// AppraisalCalibrateSerializer en backend/apps/appraisals/serializers.py.

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
  // Hasta D-04 siempre es null: no hay motor de cálculo (DS-02).
  suggested_value: string | null; // DecimalField llega como string
  confidence_level: ConfidenceLevel;
  confidence_level_display: string;
  is_manual_fallback: boolean;
  comparables_snapshot: unknown[]; // Lo llenará HU-04
  ai_draft_justification: string; // Lo llenará HU-07
  calibrated_value: string | null;
  final_justification: string;
  // Solo se calculan al aprobar y si existe suggested_value.
  difference_amount: string | null;
  difference_percentage: string | null;
  created_at: string;
  approved_at: string | null;
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
