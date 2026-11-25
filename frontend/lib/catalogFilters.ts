// Entrada decimal sin signo ni notación científica; vacío significa sin filtro.
import type { PropertyCatalogFilters, PriceDistribution } from "../types/property";

export const catalogKeys = ["location", "price_min", "price_max", "bedrooms", "bathrooms", "property_type", "area_min", "parking_spaces"] as const;
export type CatalogKey = typeof catalogKeys[number];

export function toggleSelection(current: string | undefined, selected: string): string {
  return current === selected ? "" : selected;
}

export function parkingFilterLabel(value: string): string {
  if (!value || Number(value) === 0) return "";
  if (!/^\d+$/.test(value)) return "Parqueaderos inválidos";
  return `${value}+ parqueaderos`;
}

export function numericDraft(raw: string): string | null {
  const value = raw.trim().replace(",", ".");
  return /^\d{0,10}(?:\.\d{0,2})?$/.test(value) ? value : null;
}

export function numericInitialValue(raw = ""): string {
  const value = numericDraft(raw);
  return value !== null && /\d/.test(value) ? value : "";
}

export function amountPreview(raw: string, unit: "USD" | "m²"): string {
  if (!raw || !/\d/.test(raw) || numericDraft(raw) === null) return "Sin límite";
  const formatted = new Intl.NumberFormat("es-EC", { maximumFractionDigits: 2 }).format(Number(numericDraft(raw)));
  return `${formatted} ${unit}`;
}

// Solo se aplican los campos del panel confirmado; los demás conservan su valor.
export function catalogHref(applied: PropertyCatalogFilters, changes: PropertyCatalogFilters = {}): string {
  const merged = { ...applied, ...changes };
  const params = new URLSearchParams();
  for (const key of catalogKeys) {
    const value = merged[key]?.trim();
    if (["bedrooms", "bathrooms", "parking_spaces"].includes(key) && value && Number(value) === 0) continue;
    if (value) params.set(key, value);
  }
  if (merged.sort && merged.sort !== "recent") params.set("sort", merged.sort);
  return `/properties${params.size ? `?${params}` : ""}`;
}

export function validateCatalogDraft(draft: PropertyCatalogFilters, keys: readonly CatalogKey[]): Record<string, string[]> {
  const errors: Record<string, string[]> = {};
  for (const key of keys) {
    const value = draft[key]?.trim() || "";
    if (!value) continue;
    if (["price_min", "price_max", "area_min"].includes(key) &&
        (numericDraft(value) === null || !/\d/.test(value))) {
      errors[key] = ["Usa un número positivo o cero, con hasta dos decimales."];
    }
    if (["bedrooms", "bathrooms", "parking_spaces"].includes(key) && (!/^\d+$/.test(value) || Number(value) > 2147483647)) {
      errors[key] = ["Selecciona un mínimo válido."];
    }
    if (key === "property_type" && !["casa", "departamento", "local", "terreno"].includes(value)) {
      errors[key] = ["Selecciona un tipo válido."];
    }
    if (key === "location" && value.length > 500) errors[key] = ["Usa hasta 500 caracteres."];
  }
  if (keys.includes("price_min") && keys.includes("price_max") && draft.price_min && draft.price_max &&
      !errors.price_min && !errors.price_max && Number(numericDraft(draft.price_min)) > Number(numericDraft(draft.price_max))) {
    errors.price_max = ["El precio máximo debe ser mayor o igual al mínimo."];
  }
  return errors;
}

export function priceSliderBounds(draft: PropertyCatalogFilters, distribution?: PriceDistribution): { min: number; max: number; empty: boolean } {
  const values = [distribution?.min, distribution?.max, draft.price_min, draft.price_max]
    .filter((value): value is string => value !== null && value !== undefined && value !== "")
    .map(numericInitialValue).filter((value) => value !== "").map(Number);
  return values.length ? { min: Math.min(...values), max: Math.max(...values), empty: false }
    : { min: 0, max: 0, empty: true };
}

export function movePriceThumb(draft: PropertyCatalogFilters, key: "price_min" | "price_max", value: number,
  distribution?: PriceDistribution, snap = true): string {
  const bounds = priceSliderBounds(draft, distribution);
  const lower = draft.price_min ? Number(numericInitialValue(draft.price_min)) : bounds.min;
  const upper = draft.price_max ? Number(numericInitialValue(draft.price_max)) : bounds.max;
  let safe = Math.max(bounds.min, Math.min(bounds.max, value));
  // Centavos enteros: saltos de 100 USD desde el mínimo real, sin perder el extremo máximo.
  if (snap && safe > bounds.min && safe < bounds.max) {
    const base = Math.round(bounds.min * 100);
    safe = (base + Math.round((Math.round(safe * 100) - base) / 10000) * 10000) / 100;
  }
  safe = Math.max(bounds.min, Math.min(bounds.max, safe));
  return String(key === "price_min" ? Math.min(safe, upper) : Math.max(safe, lower));
}
