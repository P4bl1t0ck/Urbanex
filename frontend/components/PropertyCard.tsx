import Image from "next/image";
import Link from "next/link";
import { Property } from "@/types/property";

export default function PropertyCard({ property }: { property: Property }) {
  const mainImage = property.images?.[0]?.image;

  return (
    <article className="min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="relative aspect-[4/3] bg-slate-100">
        {mainImage ? (
          <Image
            src={mainImage}
            alt={property.title}
            fill
            unoptimized
            className="object-cover"
            sizes="(max-width: 620px) 100vw, (max-width: 920px) 50vw, (max-width: 1220px) 33vw, (max-width: 1520px) 25vw, 20vw"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Imagen no disponible
          </div>
        )}
        <span className="absolute left-3 top-3 rounded-full bg-white/95 px-3 py-1 text-xs font-semibold capitalize text-slate-700 shadow-sm">
          {property.status === "reservador" ? "Reservado" :
            property.status?.replaceAll("_", " ") || "Sin estado"}
        </span>
      </div>
      <div className="p-4">
        <p className="text-2xl font-extrabold tracking-tight text-slate-900">
            {Number(property.price).toLocaleString("es-EC", {
              style: "currency",
              currency: "USD",
            })}
        </p>
        <p className="mt-2 truncate text-sm text-slate-700" title={`${property.bedrooms} habitaciones · ${property.bathrooms} baños · ${property.area_m2} m²`}>
          {property.bedrooms} Hab <span aria-hidden="true">·</span> {property.bathrooms} Ba <span aria-hidden="true">·</span> {property.area_m2} m²
        </p>
        <h2 className="mt-3 truncate text-sm font-semibold text-slate-900" title={property.title}>
          <Link
            href={`/properties/${property.id}`}
            className="flex min-h-11 items-center rounded-sm py-1 hover:text-blue-700 hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700"
          >
            {property.title}
          </Link>
        </h2>
        <p className="mt-1 truncate text-sm text-slate-500" title={property.location}>{property.location}</p>
      </div>
    </article>
  );
}
