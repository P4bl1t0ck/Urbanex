import Image from "next/image";
import Link from "next/link";
import { Property } from "@/types/property";

export default function PropertyCard({ property }: { property: Property }) {
  const mainImage = property.images?.[0]?.image;
  // Development stays in this tab; production restores the approved new-tab behavior.
  const opensNewTab = process.env.NODE_ENV === "production";

  return (
    <article className="min-w-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <Link href={`/properties/${property.id}`} target={opensNewTab ? "_blank" : undefined} rel={opensNewTab ? "noopener noreferrer" : undefined}
        aria-label={`Ver ficha de ${property.title}${opensNewTab ? " (se abre en una pestaña nueva)" : ""}`}
        className="block h-full focus-visible:outline-2 focus-visible:outline-offset-[-4px] focus-visible:outline-blue-700">
      <div className="relative aspect-[16/10] bg-slate-100">
        {mainImage ? (
          <Image
            src={mainImage}
            alt={property.title}
            fill
            unoptimized
            className="object-cover"
            sizes="(max-width: 700px) 100vw, (max-width: 1040px) 50vw, (max-width: 1380px) 33vw, 25vw"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-sm text-slate-500">
            Imagen no disponible
          </div>
        )}
        <span className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full bg-white/95 px-3 py-1.5 text-xs font-semibold capitalize text-slate-700 shadow-sm">
          <span aria-hidden="true" className={`h-2 w-2 rounded-full ${property.status === "disponible" ? "bg-emerald-500" : "bg-amber-500"}`} />
          {property.status === "reservador" ? "Reservado" :
            property.status?.replaceAll("_", " ") || "Sin estado"}
        </span>
      </div>
      <div className="p-3 sm:p-4">
        <p className="text-2xl font-extrabold tracking-tight text-slate-900">
            {Number(property.price).toLocaleString("es-EC", {
              style: "currency",
              currency: "USD",
            })}
            {property.operation_type === "arriendo" && <span className="ml-1 text-sm font-medium text-slate-500">/ mes</span>}
        </p>
        <p className="mt-1 text-sm text-slate-700">
          {property.property_type !== "terreno" && <>{property.bedrooms} Hab <span aria-hidden="true">·</span> {property.bathrooms} Ba <span aria-hidden="true">·</span> </>}{property.area_m2} m²
        </p>
        <h2 className="mt-2 line-clamp-2 break-words text-sm font-semibold leading-5 text-slate-900" title={property.title}>
          {property.title}
        </h2>
        <p className="mt-1 line-clamp-2 break-words text-sm leading-5 text-slate-500" title={property.location}>{property.location}</p>
      </div>
      </Link>
    </article>
  );
}
