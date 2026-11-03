// HU-12 / URB-17: pruebas de los metadatos de la ficha. Ejecutar desde frontend/:
//   npm test   (equivale a: node --test "lib/**/*.test.mjs")
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  buildPropertyMetadata,
  UNAVAILABLE_PROPERTY_METADATA,
} from "./propertyMetadata.ts";

function makeProperty(overrides = {}) {
  return {
    id: 33,
    agent: 1,
    agent_name: "Asesor Demo",
    title: "Casa en Cumbayá",
    description: "Casa amplia con jardín.",
    property_type: "casa",
    status: "disponible",
    price: "185000.00",
    area_m2: 220,
    bedrooms: 3,
    bathrooms: 2,
    parking_spaces: 2,
    location: "Cumbayá, Quito",
    latitude: null,
    longitude: null,
    images: [
      {
        id: 1,
        property: 33,
        image: "http://127.0.0.1:8000/media/properties/casa.jpg",
        caption: null,
        uploaded_at: "2026-10-27T10:00:00Z",
      },
    ],
    unavailability_reason: null,
    created_at: "2026-10-27T10:00:00Z",
    updated_at: "2026-10-27T10:00:00Z",
    ...overrides,
  };
}

test("ficha disponible: título, descripción, Open Graph y Twitter con la imagen principal", () => {
  const metadata = buildPropertyMetadata(makeProperty());
  const image = "http://127.0.0.1:8000/media/properties/casa.jpg";

  assert.equal(metadata.title, "Casa en Cumbayá | Urbanex");
  assert.match(metadata.description, /^Casa en Cumbayá, Quito · .*185\.000,00.* \(precio referencial\)\. Casa amplia con jardín\.$/);
  assert.equal(metadata.alternates.canonical, "/properties/33");
  assert.equal(metadata.openGraph.url, "/properties/33");
  assert.equal(metadata.openGraph.title, metadata.title);
  assert.equal(metadata.openGraph.description, metadata.description);
  assert.deepEqual(metadata.openGraph.images, [{ url: image, alt: "Casa en Cumbayá" }]);
  assert.equal(metadata.twitter.card, "summary_large_image");
  assert.deepEqual(metadata.twitter.images, [image]);
  assert.equal(metadata.robots, undefined);
});

test("ficha reservada: también es pública y lleva metadatos", () => {
  const metadata = buildPropertyMetadata(makeProperty({ status: "reservador" }));
  assert.equal(metadata.title, "Casa en Cumbayá | Urbanex");
  assert.ok(metadata.openGraph);
});

test("ficha sin fotos: sin imagen y tarjeta de Twitter 'summary'", () => {
  const metadata = buildPropertyMetadata(makeProperty({ images: [] }));
  assert.equal(metadata.openGraph.images, undefined);
  assert.equal(metadata.twitter.card, "summary");
  assert.equal(metadata.twitter.images, undefined);
});

test("descripción larga: se recorta a 200 caracteres como máximo, con puntos suspensivos", () => {
  const metadata = buildPropertyMetadata(makeProperty({ description: "Muy luminosa. ".repeat(40) }));
  assert.ok(metadata.description.length <= 200);
  assert.ok(metadata.description.endsWith("…"));
});

test("descripción vacía o con saltos de línea: queda solo el resumen, en una línea", () => {
  const empty = buildPropertyMetadata(makeProperty({ description: "   " }));
  assert.match(empty.description, /\(precio referencial\)\.$/);

  const multiline = buildPropertyMetadata(makeProperty({ description: "Línea uno\n\nLínea dos" }));
  assert.ok(multiline.description.endsWith("Línea uno Línea dos"));
});

for (const status of ["captacion", "vendido", "arrendado", "no_disponible"]) {
  test(`ficha en estado '${status}': sin datos de la propiedad y noindex`, () => {
    const metadata = buildPropertyMetadata(makeProperty({ status }));
    assert.deepEqual(metadata, UNAVAILABLE_PROPERTY_METADATA);
    assert.equal(metadata.title, "Propiedad no disponible | Urbanex");
    assert.equal(metadata.description, undefined);
    assert.equal(metadata.openGraph, undefined);
    assert.equal(metadata.twitter, undefined);
    assert.deepEqual(metadata.robots, { index: false, follow: false });
  });
}
