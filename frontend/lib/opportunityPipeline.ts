// Lote 4 (DS-50): lógica pura de P-07 (HU-15) e I-06A (HU-29, HU-30), sin React ni red, para
// probarla con npm test. Solo `import type`: Node los borra al ejecutar las pruebas.

import type {
  Interaction,
  OpportunityDocument,
  OpportunityStatus,
  StatusHistoryEntry,
} from "../types/opportunity";

// HU-29: secuencia de este corte (hasta la entrega del 14-nov). Reservada y Evaluación
// documental quedan fuera hasta HU-35 y RF-10 (C-04); PERDIDA llega con HU-31.
export const PIPELINE_STEPS: { status: OpportunityStatus; label: string }[] = [
  { status: "CONTACTO_INICIAL", label: "Contacto inicial" },
  { status: "VISITA_PROGRAMADA", label: "Visita programada" },
  { status: "EN_NEGOCIACION", label: "En negociación" },
  { status: "PENDIENTE_CIERRE", label: "Pendiente de cierre" },
];

export type StepState = "done" | "current" | "upcoming";

// Estado de cada etapa de la barra. Si el estado actual no está en la secuencia (por ejemplo
// Cierre o Lista de interesados), inPipeline es false y ninguna etapa se marca.
export function pipelineSteps(status: OpportunityStatus) {
  const index = PIPELINE_STEPS.findIndex((step) => step.status === status);
  return {
    inPipeline: index >= 0,
    steps: PIPELINE_STEPS.map((step, position) => ({
      ...step,
      state: (index < 0 || position > index
        ? "upcoming"
        : position === index
          ? "current"
          : "done") as StepState,
    })),
  };
}

// HU-15: enlace wa.me con el mensaje prellenado (título y código de la propiedad).
export function buildWhatsAppLink(phone: string, title: string, propertyId: number) {
  const digits = phone.replace(/\D/g, "");
  const message = `Hola, me interesa la propiedad "${title}" (código #${propertyId}) que vi en Urbanex.`;
  return `https://wa.me/${digits}?text=${encodeURIComponent(message)}`;
}

// HU-16: largo máximo del mensaje del formulario (igual que el backend).
export const MAX_INTEREST_MESSAGE = 1000;
// HU-30: largo máximo de las observaciones (igual que InteractionCreateSerializer).
export const MAX_INTERACTION_NOTES = 2000;

// Monto en dólares con hasta 2 decimales y mayor que 0 (precio final o contraoferta). El
// backend vuelve a validarlo; esto solo evita enviar un valor que seguro será rechazado.
export function isPositiveAmount(text: string) {
  const value = text.trim();
  return /^\d{1,10}(\.\d{1,2})?$/.test(value) && Number(value) > 0;
}

export type TimelineItem =
  | { kind: "status"; key: string; createdAt: string; entry: StatusHistoryEntry }
  | { kind: "interaction"; key: string; createdAt: string; entry: Interaction }
  | { kind: "document"; key: string; createdAt: string; entry: OpportunityDocument };

// Con la misma hora: primero el cambio de estado, luego la interacción y al final el documento.
const KIND_ORDER: Record<TimelineItem["kind"], number> = { status: 0, interaction: 1, document: 2 };

// I-06A: historial de estados, interacciones y (HU-33, DS-52) documentos de la propiedad en una
// sola línea de tiempo, de la más reciente a la más antigua.
export function buildTimeline(
  history: StatusHistoryEntry[],
  interactions: Interaction[],
  documents: OpportunityDocument[] = [],
) {
  const items: TimelineItem[] = [
    ...history.map((entry) => ({
      kind: "status" as const, key: `s-${entry.id}`, createdAt: entry.created_at, entry,
    })),
    ...interactions.map((entry) => ({
      kind: "interaction" as const, key: `i-${entry.id}`, createdAt: entry.created_at, entry,
    })),
    ...documents.map((entry) => ({
      kind: "document" as const, key: `d-${entry.id}`, createdAt: entry.created_at, entry,
    })),
  ];
  return items.sort((a, b) => {
    const byTime = Date.parse(b.createdAt) - Date.parse(a.createdAt);
    if (byTime !== 0) return byTime;
    return KIND_ORDER[a.kind] - KIND_ORDER[b.kind];
  });
}
