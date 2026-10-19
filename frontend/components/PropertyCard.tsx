import Image from "next/image";
import Link from "next/link";
import { Property } from "@/types/property";

export default function PropertyCard({ property }: { property: Property }) {
  const mainImage = property.images?.[0]?.image;

  return (
    <article className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
      <div className="relative h-56 bg-slate-100">
        {mainImage ? (
          <Image
            src={mainImage}
            alt={property.title}
            fill
            unoptimized
            className="object-cover"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Imagen no disponible
          </div>
        )}
        <span className="absolute left-4 top-4 rounded-full bg-white/95 px-3 py-1 text-xs font-semibold capitalize text-slate-700 shadow-sm">
          {property.status?.replaceAll("_", " ") || "Sin estado"}
        </span>
      </div>
      <div className="p-5">
        <h2 className="line-clamp-1 text-lg font-bold text-slate-900">
          {property.title}
        </h2>
        <p className="mt-1 line-clamp-1 text-sm text-slate-600">
          {property.location}
        </p>
        <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-sm text-slate-600">
          <span>{property.bedrooms} habitaciones</span>
          <span>{property.bathrooms} baños</span>
          <span>{property.area_m2} m²</span>
        </div>
        <div className="mt-5 flex items-center justify-between gap-3 border-t border-slate-100 pt-4">
          <span className="text-lg font-bold text-blue-800">
            {Number(property.price).toLocaleString("es-EC", {
              style: "currency",
              currency: "USD",
            })}
          </span>
          <Link
            href={`/properties/${property.id}`}
            className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-800"
          >
            Ver detalles
          </Link>
        </div>
      </div>
    </article>
  );
}