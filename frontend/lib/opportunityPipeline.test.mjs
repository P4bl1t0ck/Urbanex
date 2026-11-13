// Lote 4 (P-07 e I-06A): lógica pura de HU-15, HU-29 y HU-30. Ejecutar desde frontend/:
// npm test   (equivale a: node --test "lib/**/*.test.mjs")
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  buildTimeline,
  buildWhatsAppLink,
  isPositiveAmount,
  pipelineSteps,
} from "./opportunityPipeline.ts";

test("pipelineSteps marca las etapas hechas, la actual y las siguientes", () => {
  const { inPipeline, steps } = pipelineSteps("EN_NEGOCIACION");
  assert.equal(inPipeline, true);
  assert.deepEqual(steps.map((step) => step.state), ["done", "done", "current", "upcoming"]);
});

test("pipelineSteps no marca etapas si el estado está fuera de la secuencia", () => {
  for (const status of ["CIERRE", "LISTA_INTERESADOS", "PERDIDA"]) {
    const { inPipeline, steps } = pipelineSteps(status);
    assert.equal(inPipeline, false);
    assert.ok(steps.every((step) => step.state === "upcoming"));
  }
});

test("buildWhatsAppLink usa solo dígitos y prellena título y código", () => {
  const link = buildWhatsAppLink("593997654321", "Casa en Cumbayá", 12);
  assert.ok(link.startsWith("https://wa.me/593997654321?text="));
  const text = decodeURIComponent(link.split("?text=")[1]);
  assert.equal(text, 'Hola, me interesa la propiedad "Casa en Cumbayá" (código #12) que vi en Urbanex.');
  assert.ok(buildWhatsAppLink("+593 99 765 4321", "X", 1).startsWith("https://wa.me/593997654321?"));
});

test("isPositiveAmount acepta montos mayores que 0 con hasta 2 decimales", () => {
  for (const ok of ["1", "142500", "142500.5", "142500.50", " 99.99 "]) {
    assert.equal(isPositiveAmount(ok), true, ok);
  }
  for (const bad of ["", "0", "0.00", "-5", "1.234", "abc", "1e5", "12,50"]) {
    assert.equal(isPositiveAmount(bad), false, bad);
  }
});

test("buildTimeline mezcla estados e interacciones, de la más reciente a la más antigua", () => {
  const history = [
    { id: 1, created_at: "2026-11-09T10:00:00Z" },
    { id: 2, created_at: "2026-11-09T12:00:00Z" },
  ];
  const interactions = [
    { id: 7, created_at: "2026-11-09T11:00:00Z" },
    { id: 8, created_at: "2026-11-09T12:00:00Z" },
  ];
  const keys = buildTimeline(history, interactions).map((item) => item.key);
  assert.deepEqual(keys, ["s-2", "i-8", "i-7", "s-1"]);
});

test("buildTimeline suma los documentos de la propiedad en orden cronológico (HU-33)", () => {
  const history = [{ id: 1, created_at: "2026-11-09T10:00:00Z" }];
  const interactions = [{ id: 7, created_at: "2026-11-09T12:00:00Z" }];
  const documents = [
    { id: "a", created_at: "2026-11-09T09:00:00Z" },
    { id: "b", created_at: "2026-11-09T12:00:00Z" },
  ];
  const keys = buildTimeline(history, interactions, documents).map((item) => item.key);
  // Con la misma hora, la interacción va antes que el documento.
  assert.deepEqual(keys, ["i-7", "d-b", "s-1", "d-a"]);
});
