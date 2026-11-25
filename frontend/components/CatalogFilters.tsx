"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import type { PropertyCatalogFilters, PriceDistribution } from "@/types/property";
import {
  amountPreview, catalogHref, catalogKeys, movePriceThumb, numericDraft,
  numericInitialValue, parkingFilterLabel, priceSliderBounds, toggleSelection, validateCatalogDraft, type CatalogKey,
} from "@/lib/catalogFilters";

type Panel = "price" | "rooms" | "type" | "more" | "mobile";
const panelKeys: Record<Panel, readonly CatalogKey[]> = {
  price: ["price_min", "price_max"], rooms: ["bedrooms", "bathrooms"],
  type: ["property_type"], more: ["area_min", "parking_spaces"], mobile: catalogKeys,
};
const titles: Record<Panel, string> = { price: "Rango de precio", rooms: "Habitaciones y baños", type: "Tipo de propiedad", more: "Más filtros", mobile: "Filtrar propiedades" };
const types = { casa: "Casa", departamento: "Departamento", local: "Local comercial", terreno: "Terreno" };
const control = "min-h-11 w-full min-w-0 rounded-lg border border-slate-300 bg-white px-3 py-2 text-base text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-600";
const button = "min-h-11 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:border-blue-500 hover:bg-blue-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:cursor-wait disabled:opacity-60";

function initialDraft(filters: PropertyCatalogFilters): PropertyCatalogFilters {
  return { ...filters, price_min: numericInitialValue(filters.price_min), price_max: numericInitialValue(filters.price_max), area_min: numericInitialValue(filters.area_min),
    bedrooms: Number(filters.bedrooms) > 0 ? filters.bedrooms : "",
    bathrooms: Number(filters.bathrooms) > 0 ? filters.bathrooms : "",
    parking_spaces: Number(filters.parking_spaces) > 0 ? filters.parking_spaces : "" };
}
function firstErrorPanel(errors: Record<string, string[]>): Panel | null {
  if (errors.location) return "mobile";
  return (["price", "rooms", "type", "more"] as Panel[]).find((panel) => panelKeys[panel].some((key) => errors[key]?.length)) || null;
}
function SearchIcon() {
  return <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5"><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 4 4" /></svg>;
}
function Chevron() {
  return <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.75" className="h-4 w-4 shrink-0"><path d="m5 7.5 5 5 5-5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export default function CatalogFilters({ filters, fieldErrors, distribution }: {
  filters: PropertyCatalogFilters; fieldErrors: Record<string, string[]>; distribution?: PriceDistribution;
}) {
  const router = useRouter();
  const [pending, startTransition] = useTransition();
  const [panel, setPanel] = useState<Panel | null>(() => firstErrorPanel(fieldErrors));
  const [draft, setDraft] = useState(() => initialDraft(filters));
  const [location, setLocation] = useState(filters.location || "");
  const [errors, setErrors] = useState(fieldErrors);
  const [navHeight, setNavHeight] = useState(61);
  const [position, setPosition] = useState<{ left: number; top: number } | null>(null);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);
  const locationRef = useRef<HTMLInputElement>(null);
  const priceTrackRef = useRef<HTMLDivElement>(null);
  const [activeThumb, setActiveThumb] = useState<"price_min" | "price_max">("price_min");

  useEffect(() => {
    const nav = document.querySelector("nav");
    if (!nav) return;
    const update = () => setNavHeight(nav.getBoundingClientRect().height);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(nav);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!panel || !dialogRef.current) return;
    const dialog = dialogRef.current;
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    dialog.showModal();
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      dialog.close();
      document.body.style.overflow = previousOverflow;
      const target = triggerRef.current || previousFocus;
      if (target?.isConnected) target.focus();
    };
  }, [panel]);

  function openPanel(next: Panel, trigger: HTMLButtonElement) {
    triggerRef.current = trigger;
    setDraft(initialDraft(filters));
    setErrors(fieldErrors);
    const rect = trigger.getBoundingClientRect();
    const top = rect.bottom + 8;
    const desktop = window.innerWidth >= 1024 && !["more", "mobile"].includes(next);
    setPosition(desktop && window.innerHeight - top >= 400
      ? { left: Math.max(16, Math.min(rect.left, window.innerWidth - 416)), top }
      : null);
    setPanel(next);
  }
  function navigate(changes: PropertyCatalogFilters) {
    setPanel(null);
    startTransition(() => router.push(catalogHref(filters, changes), { scroll: false }));
  }
  function update(key: CatalogKey, value: string) {
    setDraft((previous) => ({ ...previous, [key]: value }));
    setErrors((previous) => { const next = { ...previous }; delete next[key]; return next; });
  }
  function apply() {
    if (!panel) return;
    const nextErrors = validateCatalogDraft(draft, panelKeys[panel]);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) {
      requestAnimationFrame(() => dialogRef.current?.querySelector<HTMLElement>('[aria-invalid="true"]')?.focus());
      return;
    }
    navigate(Object.fromEntries(panelKeys[panel].map((key) => [key, draft[key] || ""])));
  }
  function search() {
    const nextErrors = validateCatalogDraft({ location }, ["location"]);
    if (nextErrors.location) { setErrors(nextErrors); locationRef.current?.focus(); return; }
    navigate({ location });
  }
  function error(key: string) {
    return errors[key]?.length ? <p id={`${key}-error`} role="alert" className="mt-1 text-sm text-red-700">{errors[key].join(" ")}</p> : null;
  }
  function amount(key: "price_min" | "price_max" | "area_min", label: string) {
    const unit = key === "area_min" ? "m²" : "USD";
    return <div className="min-w-0">
      <label htmlFor={key} className="mb-1 block text-sm font-medium text-slate-700">{label} ({unit})</label>
      <input id={key} type="text" inputMode="decimal" autoComplete="off" maxLength={13}
        pattern="(?:[0-9]+(?:[.][0-9]{0,2})?|[.][0-9]{1,2})" className={control}
        placeholder={key === "area_min" ? "Ej. 100" : key === "price_min" ? "Ej. 100000" : "Ej. 300000"} value={draft[key] || ""}
        aria-invalid={!!errors[key]} aria-describedby={`${key}-help${errors[key] ? ` ${key}-error` : ""}`}
        onChange={(event) => {
          const next = numericDraft(event.target.value);
          if (next === null) { setErrors((previous) => ({ ...previous, [key]: ["Usa solo números y hasta dos decimales."] })); return; }
          update(key, next);
        }} onBlur={() => { const value = draft[key] || ""; if (value === ".") update(key, ""); else if (value.endsWith(".")) update(key, value.slice(0, -1)); }} />
      <p id={`${key}-help`} className="sr-only">{amountPreview(draft[key] || "", unit)}</p>{error(key)}
    </div>;
  }
  function priceFields() {
    const bounds = priceSliderBounds(draft, distribution);
    const low = draft.price_min ? Number(draft.price_min) : bounds.min;
    const high = draft.price_max ? Number(draft.price_max) : bounds.max;
    const percent = (value: number) => bounds.max === bounds.min ? 50 : Math.max(0, Math.min(100, (value - bounds.min) / (bounds.max - bounds.min) * 100));
    const lower = percent(low), upper = percent(high);
    const peak = Math.max(1, ...(distribution?.bins.map((bin) => bin.count) || []));
    function move(key: "price_min" | "price_max", clientX: number) {
      const rect = priceTrackRef.current?.getBoundingClientRect();
      if (!rect?.width) return;
      const value = bounds.min + (clientX - rect.left) / rect.width * (bounds.max - bounds.min);
      update(key, movePriceThumb(draft, key, value, distribution));
    }
    return <fieldset className="space-y-4">
      <legend className="mb-3 font-semibold text-slate-900">Precio referencial en USD</legend>
      <p id="price-slider-help" className="sr-only">Controles de precio mínimo y máximo. Flechas: 100 USD; Inicio y Fin: extremos.</p>
      <figure>
        {distribution?.total ? <>
          <div role="img" aria-label={`Distribución de ${distribution.total} propiedades. ${distribution.bins.map((bin) => `${bin.min} a ${bin.max} USD: ${bin.count}`).join("; ")}`}
            className="relative mx-5 h-20 border-b border-slate-200">
            {distribution.bins.map((bin, index) => {
              const left = bounds.max === bounds.min ? 0 : percent(Number(bin.min));
              const right = bounds.max === bounds.min ? 100 : percent(Number(bin.max));
              const selected = Number(bin.max) >= low && Number(bin.min) <= high;
              return <span key={index} aria-hidden="true" title={`${amountPreview(bin.min, "USD")} – ${amountPreview(bin.max, "USD")}: ${bin.count} propiedades`}
                className={`absolute bottom-0 rounded-t-sm ${selected ? "bg-blue-300" : "bg-slate-200"}`}
                style={{ left: `${left}%`, width: `${Math.max(0.1, right - left)}%`, height: `${bin.count / peak * 100}%`, borderInlineEnd: "2px solid white" }} />;
            })}
          </div>
          <figcaption className="sr-only">{distribution.total} propiedades con los demás filtros, antes de aplicar el precio.</figcaption>
        </> : <p className="rounded-lg bg-slate-50 p-3 text-sm text-slate-500">No hay precios para esta búsqueda. Prueba otros filtros.</p>}
      </figure>
      <div className="px-5">
        <div ref={priceTrackRef} className="relative h-12" role="group" aria-label="Rango de precio">
          <div className="absolute top-5 h-1 w-full rounded-full bg-slate-200" />
          <div className="absolute top-5 h-1 rounded-full bg-blue-700" style={{ left: `${lower}%`, width: `${Math.max(0, upper - lower)}%` }} />
          {(["price_min", "price_max"] as const).map((key) => {
            const value = key === "price_min" ? low : high;
            return <button key={key} type="button" role="slider" aria-label={key === "price_min" ? "Precio mínimo" : "Precio máximo"}
              aria-valuemin={bounds.min} aria-valuemax={bounds.max} aria-valuenow={value} aria-valuetext={amountPreview(String(value), "USD")}
              aria-describedby="price-slider-help" disabled={bounds.empty || bounds.min === bounds.max}
              style={{ left: `calc(${percent(value)}% - 22px)`, zIndex: activeThumb === key ? 2 : 1 }}
              className="group absolute top-0 flex h-11 w-11 touch-none items-center justify-center rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:cursor-not-allowed"
              onFocus={() => setActiveThumb(key)}
              onPointerDown={(event) => { event.currentTarget.setPointerCapture(event.pointerId); event.currentTarget.focus(); setActiveThumb(key); }}
              onPointerMove={(event) => { if (event.currentTarget.hasPointerCapture(event.pointerId)) move(key, event.clientX); }}
              onPointerUp={(event) => { if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId); }}
              onKeyDown={(event) => {
                const jumps: Record<string, number> = { ArrowRight: 100, ArrowUp: 100, ArrowLeft: -100, ArrowDown: -100, PageUp: 1000, PageDown: -1000 };
                if (!(event.key in jumps) && event.key !== "Home" && event.key !== "End") return;
                event.preventDefault();
                const next = event.key === "Home" ? bounds.min : event.key === "End" ? bounds.max : value + jumps[event.key];
                update(key, movePriceThumb(draft, key, next, distribution, false));
              }}>
              {!bounds.empty && <span aria-hidden="true" data-price-tooltip={key}
                style={{ transform: `translateX(${percent(value) < 25 ? "0%" : percent(value) > 75 ? "-100%" : "-50%"})` }}
                className="pointer-events-none absolute bottom-full left-1/2 mb-1 whitespace-nowrap rounded-md bg-slate-900 px-2 py-1 text-xs font-semibold text-white opacity-0 shadow-sm group-hover:opacity-100 group-active:opacity-100 group-focus-visible:opacity-100">
                {amountPreview(String(value), "USD")}
              </span>}
              <span aria-hidden="true" className="h-5 w-5 rounded-full border-2 border-blue-700 bg-white shadow-sm" />
            </button>;
          })}
        </div>
        {!bounds.empty && <div className="flex justify-between gap-2 text-xs text-slate-500"><span>{amountPreview(String(bounds.min), "USD")}</span><span>{amountPreview(String(bounds.max), "USD")}</span></div>}
      </div>
      <div className="grid grid-cols-2 gap-3">{amount("price_min", "Mínimo")}{amount("price_max", "Máximo")}</div>
    </fieldset>;
  }
  function roomsFields() {
    return <div className="space-y-6">{(["bedrooms", "bathrooms"] as const).map((key) => {
      const current = draft[key] || "";
      const options = ["1", "2", "3", "4"];
      if (Number(current) > 0 && /^\d+$/.test(current) && !options.includes(current)) options.push(current);
      return <fieldset key={key}>
        <legend className="mb-3 font-semibold text-slate-900">{key === "bedrooms" ? "Número de habitaciones" : "Número de baños"}</legend>
        <div className="grid grid-cols-4 gap-2">{options.map((value, index) => <button key={value} type="button" aria-pressed={current === value}
          onClick={() => update(key, toggleSelection(current, value))} className={`${button} w-full min-w-0 break-all !px-2 ${index >= 4 ? "col-span-4" : ""} ${current === value ? "!border-blue-700 !bg-blue-50 !text-blue-800" : ""}`}>
          {value}+
        </button>)}</div>{error(key)}
      </fieldset>;
    })}</div>;
  }
  function typeFields() {
    return <fieldset>
      <legend className="mb-3 font-semibold text-slate-900">Tipo de propiedad</legend>
      <div className="grid grid-cols-2 gap-2">{[["", "Todos"], ...Object.entries(types)].map(([value, label]) => <button key={value} type="button"
        aria-pressed={(draft.property_type || "") === value} onClick={() => update("property_type", value)}
        className={`${button} w-full min-w-0 min-h-14 !px-2 ${value === "" ? "col-span-2" : ""} ${(draft.property_type || "") === value ? "!border-blue-700 !bg-blue-50 !text-blue-800" : ""}`}>{label}</button>)}</div>{error("property_type")}
    </fieldset>;
  }
  function moreFields() {
    const current = draft.parking_spaces || "";
    const options = ["1", "2", "3"];
    if (Number(current) > 0 && /^\d+$/.test(current) && !options.includes(current)) options.push(current);
    return <div className="space-y-5">
      {amount("area_min", "Superficie mínima")}
      <fieldset>
        <legend className="mb-3 font-semibold text-slate-900">Parqueaderos</legend>
        <div className="grid grid-cols-3 gap-2">{options.map((value, index) => <button key={value} type="button"
          aria-pressed={current === value} onClick={() => update("parking_spaces", toggleSelection(current, value))}
          className={`${button} w-full min-w-0 break-all !px-2 ${index >= 3 ? "col-span-3" : ""} ${current === value ? "!border-blue-700 !bg-blue-50 !text-blue-800" : ""}`}>
          {value}+
        </button>)}</div>
        {error("parking_spaces")}
      </fieldset>
    </div>;
  }
  const active = [
    ...(filters.location ? [{ label: filters.location, keys: ["location"] as CatalogKey[] }] : []),
    ...(filters.price_min || filters.price_max ? [{ label: `Precio: ${filters.price_min ? amountPreview(filters.price_min, "USD") : "sin mínimo"} – ${filters.price_max ? amountPreview(filters.price_max, "USD") : "sin máximo"}`, keys: ["price_min", "price_max"] as CatalogKey[] }] : []),
    ...(Number(filters.bedrooms) > 0 ? [{ label: `${filters.bedrooms}+ hab.`, keys: ["bedrooms"] as CatalogKey[] }] : []),
    ...(Number(filters.bathrooms) > 0 ? [{ label: `${filters.bathrooms}+ baños`, keys: ["bathrooms"] as CatalogKey[] }] : []),
    ...(filters.property_type ? [{ label: types[filters.property_type as keyof typeof types] || "Tipo inválido", keys: ["property_type"] as CatalogKey[] }] : []),
    ...(filters.area_min ? [{ label: `Desde ${amountPreview(filters.area_min, "m²")}`, keys: ["area_min"] as CatalogKey[] }] : []),
    ...(Number(filters.parking_spaces) > 0 ? [{ label: parkingFilterLabel(filters.parking_spaces!), keys: ["parking_spaces"] as CatalogKey[] }] : []),
  ];
  return <div style={{ top: navHeight }} className="sticky z-10 mb-6 rounded-xl border border-slate-200 bg-white/95 shadow-sm backdrop-blur" aria-busy={pending}>
    <div className="flex flex-wrap items-center gap-2 p-3">
      <form className="flex min-w-0 flex-1 basis-40 items-center gap-1 rounded-lg border border-slate-300 bg-white focus-within:ring-2 focus-within:ring-blue-600" onSubmit={(event) => { event.preventDefault(); search(); }}>
        <label htmlFor="catalog-location" className="sr-only">Ciudad, barrio o sector</label>
        <input ref={locationRef} id="catalog-location" type="search" maxLength={500} value={location} onChange={(event) => setLocation(event.target.value)}
          placeholder="Ciudad, barrio o sector..." className="min-h-11 w-full min-w-0 rounded-lg bg-transparent px-3 py-2 text-base text-slate-900 outline-none" />
        <button type="submit" disabled={pending} aria-label="Buscar ubicación" className="mr-1 flex min-h-11 min-w-11 items-center justify-center rounded-lg text-blue-700 hover:bg-blue-50 focus-visible:outline-2"><SearchIcon /></button>
      </form>
      <div className="hidden flex-wrap gap-2 lg:flex">
        <button disabled className={`${button} !cursor-not-allowed !opacity-50`}>Operación · Próximamente</button>
        {(["price", "rooms", "type", "more"] as Panel[]).map((item) => <button key={item} type="button" disabled={pending}
          aria-haspopup="dialog" aria-expanded={panel === item} onClick={(event) => openPanel(item, event.currentTarget)} className={`${button} inline-flex shrink-0 items-center gap-3`}>
          <span>{item === "price" ? "Precio" : item === "rooms" ? "Habitaciones y baños" : item === "type" ? "Tipo de propiedad" : "Más filtros"}</span><Chevron />
        </button>)}
      </div>
      <button type="button" disabled={pending} aria-haspopup="dialog" aria-expanded={panel === "mobile"} onClick={(event) => openPanel("mobile", event.currentTarget)} className={`${button} lg:hidden`}>Filtros{active.length ? ` (${active.length})` : ""}</button>
    </div>
    {(active.length > 0 || pending) && <div className="flex flex-wrap items-center gap-2 border-t border-slate-100 px-3 py-2">
      {active.map((chip) => <button key={chip.keys.join()} type="button" disabled={pending} aria-label={`Quitar filtro: ${chip.label}`}
        onClick={() => navigate(Object.fromEntries(chip.keys.map((key) => [key, ""])))}
        className="flex min-h-9 max-w-full items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-sm text-blue-800 hover:bg-blue-100 focus-visible:outline-2">
        <span className="truncate">{chip.label}</span><span aria-hidden="true">×</span>
      </button>)}
      {active.length > 0 && <button type="button" disabled={pending} onClick={() => navigate(Object.fromEntries(catalogKeys.map((key) => [key, ""])))} className="min-h-9 px-2 text-sm font-semibold text-slate-600 underline">Limpiar filtros</button>}
      {pending && <span role="status" className="text-sm font-medium text-blue-700">Actualizando resultados…</span>}
    </div>}
    <dialog ref={dialogRef} aria-labelledby="catalog-dialog-title"
      style={position ? { left: position.left, top: position.top, transform: "none", maxHeight: `calc(100dvh - ${position.top + 16}px)` } : { left: "50%", top: "50%", transform: "translate(-50%, -50%)" }}
      className="fixed m-0 max-h-[85dvh] w-[calc(100%_-_2rem)] max-w-[400px] overflow-y-auto rounded-xl border border-slate-200 bg-white p-0 text-slate-900 shadow-2xl backdrop:bg-slate-900/20"
      onCancel={(event) => { event.preventDefault(); setPanel(null); }}
      onClick={(event) => { if (event.target !== event.currentTarget) return; const rect = event.currentTarget.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) setPanel(null); }}>
      {panel && <form onSubmit={(event) => { event.preventDefault(); apply(); }}>
        <div className="sticky top-0 z-10 flex items-center justify-between gap-3 border-b border-slate-100 bg-white p-4">
          <h2 id="catalog-dialog-title" className="text-lg font-bold">{titles[panel]}</h2>
          <button type="button" onClick={() => setPanel(null)} aria-label="Cerrar filtros sin aplicar" className={`${button} px-3`}>×</button>
        </div>
        <div className="space-y-6 p-4">
          {panel === "mobile" && <div><label htmlFor="dialog-location" className="mb-1 block text-sm font-medium">Ciudad, barrio o sector</label>
            <input id="dialog-location" type="search" maxLength={500} value={draft.location || ""} onChange={(event) => update("location", event.target.value)} className={control} aria-invalid={!!errors.location} aria-describedby={errors.location ? "location-error" : undefined} />{error("location")}
          </div>}
          {(panel === "price" || panel === "mobile") && priceFields()}
          {(panel === "rooms" || panel === "mobile") && roomsFields()}
          {(panel === "type" || panel === "mobile") && typeFields()}
          {(panel === "more" || panel === "mobile") && moreFields()}
        </div>
        <div className="sticky bottom-0 border-t border-slate-100 bg-white p-4">
          <button type="submit" disabled={pending} className="min-h-11 w-full rounded-lg bg-blue-700 px-5 py-2 font-semibold text-white hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Filtrar</button>
        </div>
      </form>}
    </dialog>
  </div>;
}
