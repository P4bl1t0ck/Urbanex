import { test } from "node:test";
import assert from "node:assert/strict";
import { propertyCoordinates, visitConfirmation, contactFields, principalFeatures, similarProperties } from "./propertyDetail.ts";

const property = { id: 1, property_type: "casa", operation_type: "venta", status: "disponible",
  area_m2: 120, bedrooms: 3, bathrooms: 0, parking_spaces: 0 };

test("principales: solo valores positivos y aplicables", () => {
  assert.deepEqual(principalFeatures(property).map((feature) => feature.label), ["Área", "Habitaciones"]);
  assert.deepEqual(principalFeatures({ ...property, property_type: "terreno", bathrooms: 2 }).map((feature) => feature.label), ["Área"]);
  assert.deepEqual(principalFeatures({ ...property, area_m2: 0, bedrooms: 0 }), []);
});

test("similares: mismo tipo, públicos, sin actual ni duplicados y misma operación primero", () => {
  const candidates = [property, { ...property, id: 2, operation_type: "arriendo" },
    { ...property, id: 3 }, { ...property, id: 4, property_type: "terreno" },
    { ...property, id: 5, status: "captacion" }, { ...property, id: 3 },
    { ...property, id: 6, status: "reservador" }];
  assert.deepEqual(similarProperties(property, candidates).map((item) => item.id), [6, 3, 2]);
  assert.deepEqual(similarProperties(property, candidates, 1).map((item) => item.id), [6]);
  assert.deepEqual(similarProperties(property, [property]), []);
});

test("datos compartidos: no heredan consentimiento, opt-in, mensaje ni horario", () => {
  assert.deepEqual(contactFields({ full_name: "Ejemplo", phone: "0900000000", email: "demo@example.test",
    privacy_accepted: true, email_opt_in: true, message: "Consulta", start: "2030-01-01" }),
  { full_name: "Ejemplo", phone: "0900000000", email: "demo@example.test" });
  assert.deepEqual(contactFields({}), { full_name: "", phone: "", email: "" });
});

test("visit confirmation: explicit email enables delivery, empty or whitespace disables it", () => {
  assert.deepEqual(visitConfirmation(" demo@example.test "), { email: "demo@example.test", email_opt_in: true });
  assert.deepEqual(visitConfirmation(""), { email: "", email_opt_in: false });
  assert.deepEqual(visitConfirmation("   "), { email: "", email_opt_in: false });
});

test("map coordinates: accepts zero, rejects missing, non-finite and out-of-range values", () => {
  assert.deepEqual(propertyCoordinates("-0.18", "-78.46"), [-0.18, -78.46]);
  assert.deepEqual(propertyCoordinates("0", "0"), [0, 0]);
  for (const [lat, lng] of [[null,"0"],["", "0"],[" ","0"],["NaN","0"],["Infinity","0"],["91","0"],["0","-181"]]) {
    assert.equal(propertyCoordinates(lat,lng), null);
  }
});
