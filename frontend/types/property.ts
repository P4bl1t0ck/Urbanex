// Contrato de /api/auth/properties/. Debe coincidir con PropertySerializer y
// PropertyImageSerializer en backend/apps/users/serializers.py.

export type PropertyType = "casa" | "departamento" | "local" | "terreno";

// "reservador" es el valor que hoy guarda Django (errata en Property.STATUS_CHOICES).
export type PropertyStatus =
  | "captacion"
  | "disponible"
  | "reservador"
  | "vendido"
  | "arrendado"
  | "no_disponible";

export type PropertyImage = {
  id: number;
  property: number;
  image: string; // URL absoluta generada por DRF
  caption: string | null;
  uploaded_at: string;
};

export type Property = {
  id: number;
  agent: number | null;
  agent_name: string;
  title: string;
  description: string;
  property_type: PropertyType;
  status: PropertyStatus;
  price: string; // DecimalField llega como string
  area_m2: number;
  bedrooms: number;
  bathrooms: number;
  parking_spaces: number;
  location: string;
  latitude: string | null; // DecimalField (6 decimales) llega como string
  longitude: string | null;
  images: PropertyImage[];
  unavailability_reason: string | null;
  created_at: string;
  updated_at: string;
};

export type PropertyCatalogFilters = Partial<Record<
  "property_type" | "price_min" | "price_max" | "bedrooms" | "bathrooms" |
  "area_min" | "parking_spaces" | "location" | "page" | "sort", string
>>;

export type PriceDistribution = {
  min: string | null;
  max: string | null;
  total: number;
  bins: { min: string; max: string; count: number }[];
};

export type PropertyCatalogPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Property[];
  price_distribution: PriceDistribution;
};
