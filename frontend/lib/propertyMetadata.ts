// HU-12 / URB-17: metadatos para compartir la ficha P-03 (título, descripción,
// imagen principal, Open Graph y Twitter). Solo usa `import type` para que
// `node --test` pueda ejecutarlo sin compilar (lib/propertyMetadata.test.mjs).
import type { Metadata } from "next";
import type { Property, PropertyStatus, PropertyType } from "@/types/property";

// Mismos estados que PUBLIC_STATUSES en backend/apps/users/views.py
// ("reservador" es la errata vigente, DT-16).
export const PUBLIC_STATUSES: readonly PropertyStatus[] = ["disponible", "reservador"];

const SITE_NAME = "Urbanex";
const DESCRIPTION_MAX_LENGTH = 200;

const TYPE_LABELS: Record<PropertyType, string> = {
  casa: "Casa",
  departamento: "Departamento",
  local: "Local",
  terreno: "Terreno",
};

// Ficha inexistente, no pública o error de la API: sin datos de la propiedad.
export const UNAVAILABLE_PROPERTY_METADATA: Metadata = {
  title: `Propiedad no disponible | ${SITE_NAME}`,
  robots: { index: false, follow: false },
};

export function isPublicProperty(property: Pick<Property, "status">): boolean {
  return PUBLIC_STATUSES.includes(property.status);
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return `${text.slice(0, maxLength - 1).trimEnd()}…`;
}

export function buildPropertyDescription(property: Property): string {
  const price = Number(property.price).toLocaleString("es-EC", {
    style: "currency",
    currency: "USD",
  });
  const type = TYPE_LABELS[property.property_type] ?? property.property_type;
  const summary = `${type} en ${property.location} · ${price} (precio referencial).`;
  const description = property.description.replace(/\s+/g, " ").trim();
  return truncate(description ? `${summary} ${description}` : summary, DESCRIPTION_MAX_LENGTH);
}

export function buildPropertyMetadata(property: Property): Metadata {
  if (!isPublicProperty(property)) return UNAVAILABLE_PROPERTY_METADATA;

  const title = `${property.title} | ${SITE_NAME}`;
  const description = buildPropertyDescription(property);
  const url = `/properties/${property.id}`;
  const mainImage = property.images?.[0]?.image;
  const images = mainImage ? [{ url: mainImage, alt: property.title }] : undefined;

  return {
    title,
    description,
    alternates: { canonical: url },
    openGraph: {
      type: "website",
      siteName: SITE_NAME,
      locale: "es_EC",
      url,
      title,
      description,
      images,
    },
    twitter: {
      card: mainImage ? "summary_large_image" : "summary",
      title,
      description,
      images: mainImage ? [mainImage] : undefined,
    },
  };
}
