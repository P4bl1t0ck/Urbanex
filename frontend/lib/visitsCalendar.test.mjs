// Lote 2 (I-09, P-07, I-08): fechas y horas del agendamiento en hora de Ecuador. Ejecutar
// desde frontend/: npm test   (equivale a: node --test "lib/**/*.test.mjs")
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  addDays,
  daysBetween,
  ecuadorDateOf,
  ecuadorToday,
  formatTime,
  groupByEcuadorDay,
  toHourMinute,
  weekdayOf,
  weekRange,
  weekStart,
} from "./visitsCalendar.ts";

test("hoy en Ecuador: a las 03:00 UTC todavía es el día anterior", () => {
  assert.equal(ecuadorToday(new Date("2026-11-10T03:00:00Z")), "2026-11-09");
  assert.equal(ecuadorToday(new Date("2026-11-10T05:00:00Z")), "2026-11-10");
});

test("la fecha de una hora con -05:00 no cambia aunque en UTC ya sea el día siguiente", () => {
  assert.equal(ecuadorDateOf("2026-11-15T23:30:00-05:00"), "2026-11-15");
  assert.equal(ecuadorDateOf("2026-11-16T04:30:00Z"), "2026-11-15");
});

test("las horas se muestran en hora de Ecuador en formato de 24 h", () => {
  assert.equal(formatTime("2026-11-09T09:00:00-05:00"), "09:00");
  assert.equal(formatTime("2026-11-09T14:00:00Z"), "09:00");
  assert.equal(formatTime("2026-11-09T17:30:00-05:00"), "17:30");
});

test("0 = lunes ... 6 = domingo, como el backend", () => {
  assert.equal(weekdayOf("2026-11-09"), 0); // lunes
  assert.equal(weekdayOf("2026-11-15"), 6); // domingo
});

test("la semana va de lunes a domingo", () => {
  assert.equal(weekStart("2026-11-09"), "2026-11-09");
  assert.equal(weekStart("2026-11-15"), "2026-11-09");
  assert.deepEqual(weekRange("2026-11-12"), { from: "2026-11-09", to: "2026-11-15" });
  // Cruza de mes y de año.
  assert.deepEqual(weekRange("2026-12-31"), { from: "2026-12-28", to: "2027-01-03" });
});

test("sumar días y listar un rango, incluidos los extremos", () => {
  assert.equal(addDays("2026-11-30", 1), "2026-12-01");
  assert.equal(addDays("2026-11-09", -7), "2026-11-02");
  assert.deepEqual(daysBetween("2026-11-09", "2026-11-11"), ["2026-11-09", "2026-11-10", "2026-11-11"]);
});

test("HH:MM:SS de la API pasa a HH:MM", () => {
  assert.equal(toHourMinute("09:30:00"), "09:30");
  assert.equal(toHourMinute(null), "");
});

test("agrupa por día de Ecuador y conserva los días vacíos", () => {
  const items = [
    { id: 1, start: "2026-11-09T09:00:00-05:00" },
    { id: 2, start: "2026-11-11T23:00:00-05:00" }, // 04:00 UTC del día 12
    { id: 3, start: "2026-11-09T10:00:00-05:00" },
    { id: 4, start: "2026-11-20T09:00:00-05:00" }, // Fuera del rango: se descarta
  ];
  const groups = groupByEcuadorDay(items, (item) => item.start, "2026-11-09", "2026-11-11");
  assert.deepEqual(
    groups.map((group) => [group.day, group.items.map((item) => item.id)]),
    [["2026-11-09", [1, 3]], ["2026-11-10", []], ["2026-11-11", [2]]],
  );
});
