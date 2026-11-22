import type { Property } from "../types/property";

export type ContactDraft = { full_name: string; phone: string; email: string };

export function contactPhoneError(raw: string): string | undefined {
  const value = raw.replace(/[\s\-.()]/g, "");
  if (!value) return "Indica tu celular.";
  if (/^(?:09\d{8}|\+5939\d{8})$/.test(value)) return undefined;
  return "Celular de Ecuador: 10 dígitos, empieza por 09. También aceptamos +5939XXXXXXXX.";
}

// No compartir consentimientos: interés y confirmación de visita tienen fines distintos.
export function contactFields(value: Partial<ContactDraft>): ContactDraft {
  return { full_name: value.full_name || "", phone: value.phone || "", email: value.email || "" };
}

export function principalFeatures(property: Pick<Property, "property_type" | "area_m2" | "bedrooms" | "bathrooms" | "parking_spaces">) {
  return [
    { label: "Área", amount: property.area_m2, value: `${property.area_m2} m²` },
    { label: "Habitaciones", amount: property.bedrooms, value: String(property.bedrooms) },
    { label: "Baños", amount: property.bathrooms, value: String(property.bathrooms) },
    { label: "Parqueaderos", amount: property.parking_spaces, value: String(property.parking_spaces) },
  ].filter((feature) => Number.isFinite(feature.amount) && feature.amount > 0 &&
    (property.property_type !== "terreno" || !["Habitaciones", "Baños"].includes(feature.label)));
}

export function similarProperties(property: Property, candidates: Property[], limit = 6): Property[] {
  const seen = new Set<number>();
  return candidates.filter((candidate) => {
    if (candidate.id === property.id || seen.has(candidate.id) || candidate.property_type !== property.property_type ||
      !["disponible", "reservador"].includes(candidate.status)) return false;
    seen.add(candidate.id);
    return true;
  }).sort((a, b) => Number(b.operation_type === property.operation_type) - Number(a.operation_type === property.operation_type) || b.id - a.id)
    .slice(0, Math.max(0, limit));
}

// The visitor explicitly supplies this email for the visit confirmation only.
export function visitConfirmation(value: string) {
  const email = value.trim();
  return { email, email_opt_in: email.length > 0 };
}

export function propertyCoordinates(latitude: string | null, longitude: string | null): [number, number] | null {
  if (latitude === null || longitude === null || !latitude.trim() || !longitude.trim()) return null;
  const lat = Number(latitude), lng = Number(longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) return null;
  return [lat, lng];
}
