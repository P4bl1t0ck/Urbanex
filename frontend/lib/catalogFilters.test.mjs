import { test } from "node:test";
import assert from "node:assert/strict";
import { numericDraft, numericInitialValue, amountPreview, catalogHref, validateCatalogDraft, priceSliderBounds, movePriceThumb, parkingFilterLabel, toggleSelection } from "./catalogFilters.ts";

const prices = { min: "85000.00", max: "285000.00", total: 26, bins: [] };

test("decimal: conserva vacío, cero y límites inclusivos sin activar valores de ejemplo", () => {
  for (const value of ["", "0", "100000", "9999999999.99", ".", ".5", "12."]) {
    assert.equal(numericDraft(value), value);
  }
  assert.equal(numericInitialValue(), "");
  assert.equal(numericInitialValue("."), "");
});
test("decimal: teclado con coma se normaliza sin cambiar magnitud", () => {
  assert.equal(numericDraft(" 150000,50 "), "150000.50");
  assert.equal(numericDraft(",5"), ".5");
});
test("decimal: rechaza letras, exponentes, negativos, pegados mixtos y exceso de precisión", () => {
  for (const value of ["texto", "1e3", "-1", "+2", "12abc", "1.234", "1,234.56", "10000000000", "NaN", "Infinity"]) {
    assert.equal(numericDraft(value), null, value);
    assert.equal(numericInitialValue(value), "", value);
  }
});
test("vista previa: distingue sin límite de cero y conserva unidades", () => {
  assert.equal(amountPreview("", "USD"), "Sin límite");
  assert.equal(amountPreview(".", "USD"), "Sin límite");
  assert.equal(amountPreview("0", "USD"), "0 USD");
  assert.match(amountPreview("285000", "USD"), /USD$/);
  assert.match(amountPreview("95.5", "m²"), /m²$/);
  assert.equal(amountPreview("texto", "USD"), "Sin límite");
});

test("aplicar un panel conserva otros filtros, codifica ubicación y reinicia página", () => {
  const href = catalogHref({ location: "Cumbayá & Quito", bedrooms: "3", page: "2" }, { price_min: "150000" });
  const query = new URL(href, "http://localhost").searchParams;
  assert.equal(query.get("location"), "Cumbayá & Quito");
  assert.equal(query.get("bedrooms"), "3");
  assert.equal(query.get("price_min"), "150000");
  assert.equal(query.has("page"), false);
});

test("borrador y cancelación no mutan filtros aplicados; quitar un grupo conserva el resto", () => {
  const applied = Object.freeze({ location: "Quito", price_min: "100", price_max: "200", bathrooms: "2", page: "3" });
  const draft = { ...applied, price_min: "150" };
  assert.equal(applied.price_min, "100");
  assert.equal(draft.price_min, "150");
  const query = new URL(catalogHref(applied, { price_min: "", price_max: "" }), "http://localhost").searchParams;
  assert.equal(query.has("price_min"), false);
  assert.equal(query.has("price_max"), false);
  assert.equal(query.get("bathrooms"), "2");
  assert.equal(query.get("location"), "Quito");
  assert.equal(applied.page, "3");
  assert.equal(catalogHref({}, {}), "/properties");
});

test("precio: rechaza rango invertido y acepta límites iguales, cero y campos vacíos", () => {
  assert.ok(validateCatalogDraft({ price_min: "200", price_max: "100" }, ["price_min", "price_max"]).price_max);
  for (const values of [{}, { price_min: "0", price_max: "0" }, { price_min: "100.50", price_max: "100.50" }]) {
    assert.deepEqual(validateCatalogDraft(values, ["price_min", "price_max"]), {});
  }
  assert.ok(validateCatalogDraft({ price_min: "." }, ["price_min"]).price_min);
});

test("validación del panel señala campos malformados sin bloquear otro panel", () => {
  const values = { price_min: "texto", bedrooms: "-1", bathrooms: "2147483648", property_type: "suite", area_min: "1e3", location: "x".repeat(501) };
  const errors = validateCatalogDraft(values, ["price_min", "bedrooms", "bathrooms", "property_type", "area_min", "location"]);
  assert.deepEqual(Object.keys(errors).sort(), Object.keys(values).sort());
  assert.deepEqual(validateCatalogDraft({ ...values, location: "Quito" }, ["location"]), {});
});

test("slider: comienza en precios reales y no agrega filtros implícitos", () => {
  assert.deepEqual(priceSliderBounds({}, prices), { min: 85000, max: 285000, empty: false });
  assert.equal(priceSliderBounds({ price_max: "7500000.25" }, prices).max, 7500000.25);
  assert.equal(priceSliderBounds({ price_min: "100" }, prices).min, 100);
  assert.equal(catalogHref({ location: "Quito" }), "/properties?location=Quito");
});

test("slider: no cruza los controles y salta de 100 en 100", () => {
  assert.equal(movePriceThumb({ price_max: "150000" }, "price_min", 200000, prices), "150000");
  assert.equal(movePriceThumb({ price_min: "100000" }, "price_max", 90000, prices), "100000");
  assert.equal(movePriceThumb({}, "price_min", 85060, prices), "85100");
  assert.equal(movePriceThumb({}, "price_min", -1, prices), "85000");
});

test("precio escrito por encima de la escala inicial conserva importe exacto al aplicar", () => {
  const draft = { price_min: "7500000.25", price_max: "9999999999.99" };
  assert.deepEqual(validateCatalogDraft(draft, ["price_min", "price_max"]), {});
  const query = new URL(catalogHref({}, draft), "http://localhost").searchParams;
  assert.equal(query.get("price_min"), draft.price_min);
  assert.equal(query.get("price_max"), draft.price_max);
  assert.equal(priceSliderBounds(draft, prices).max, 9999999999.99);
});

test("slider: conserva extremos no alineados y pasos desde un mínimo decimal", () => {
  const distribution = { ...prices, min: "85050.25", max: "285077.77" };
  assert.equal(movePriceThumb({}, "price_min", 85120, distribution), "85150.25");
  assert.equal(movePriceThumb({}, "price_max", 285077.77, distribution), "285077.77");
  assert.equal(movePriceThumb({ price_min: "100000.50" }, "price_min", 100100.50, distribution, false), "100100.5");
});

test("slider: inventario vacío y precio único no inventan un rango", () => {
  assert.deepEqual(priceSliderBounds({}, { min: null, max: null, total: 0, bins: [] }), { min: 0, max: 0, empty: true });
  assert.deepEqual(priceSliderBounds({}, { ...prices, min: "100.25", max: "100.25" }), { min: 100.25, max: 100.25, empty: false });
});

test("parqueaderos: selección válida viaja en URL y sobrevive a otros paneles", () => {
  assert.deepEqual(validateCatalogDraft({ parking_spaces: "2" }, ["parking_spaces"]), {});
  for (const value of ["-1", "1.5", "texto", "2147483648"]) {
    assert.ok(validateCatalogDraft({ parking_spaces: value }, ["parking_spaces"]).parking_spaces);
  }
  assert.equal(new URL(catalogHref({ parking_spaces: "2", page: "2" }, { price_min: "100000" }), "http://localhost").searchParams.get("parking_spaces"), "2");
  assert.equal(catalogHref({ parking_spaces: "2" }, { parking_spaces: "" }), "/properties");
});

test("parqueaderos: cero heredado se normaliza como ausencia de mínimo", () => {
  assert.deepEqual(validateCatalogDraft({ parking_spaces: "0" }, ["parking_spaces"]), {});
  const url = new URL(catalogHref({ location: "Quito", page: "2" }, { parking_spaces: "0" }), "http://localhost");
  assert.equal(url.searchParams.has("parking_spaces"), false);
  assert.equal(url.searchParams.has("page"), false);
  assert.equal(catalogHref({ location: "Quito", parking_spaces: "0" }, { parking_spaces: "" }), "/properties?location=Quito");
});

test("parqueaderos: etiquetas positivas son mínimos y cero no genera etiqueta", () => {
  assert.equal(parkingFilterLabel(""), "");
  assert.equal(parkingFilterLabel("0"), "");
  assert.equal(parkingFilterLabel("1"), "1+ parqueaderos");
  assert.equal(parkingFilterLabel("2"), "2+ parqueaderos");
  assert.equal(parkingFilterLabel("3"), "3+ parqueaderos");
  assert.equal(parkingFilterLabel("4"), "4+ parqueaderos");
  assert.equal(parkingFilterLabel("texto"), "Parqueaderos inválidos");
});

test("botones: ninguno seleccionado no restringe y repetir el activo lo desmarca", () => {
  assert.equal(toggleSelection(undefined, "1"), "1");
  assert.equal(toggleSelection("", "2"), "2");
  assert.equal(toggleSelection("2", "2"), "");
  assert.equal(toggleSelection("2", "3"), "3");
  assert.equal(catalogHref({ bedrooms: "2", bathrooms: "1" }, { bedrooms: toggleSelection("2", "2") }), "/properties?bathrooms=1");
});

test("ordenar conserva filtros y reinicia página; cambiar filtros conserva orden", () => {
  const sorted = new URL(catalogHref({ location: "Quito", parking_spaces: "2", page: "2" }, { sort: "price_desc" }), "http://localhost");
  assert.equal(sorted.searchParams.get("location"), "Quito");
  assert.equal(sorted.searchParams.get("parking_spaces"), "2");
  assert.equal(sorted.searchParams.get("sort"), "price_desc");
  assert.equal(sorted.searchParams.has("page"), false);
  const filtered = new URL(catalogHref({ sort: "price_asc", page: "3" }, { bedrooms: "2" }), "http://localhost");
  assert.equal(filtered.searchParams.get("sort"), "price_asc");
  assert.equal(filtered.searchParams.get("bedrooms"), "2");
  assert.equal(filtered.searchParams.has("page"), false);
});

test("limpiar filtros mantiene el orden elegido y recientes elimina sort", () => {
  assert.equal(catalogHref({ location: "Quito", parking_spaces: "1", sort: "price_desc" }, { location: "", parking_spaces: "" }), "/properties?sort=price_desc");
  assert.equal(catalogHref({ sort: "price_asc", location: "Quito" }, { sort: "recent" }), "/properties?location=Quito");
});
