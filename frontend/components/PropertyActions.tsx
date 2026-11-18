"use client";

import { useEffect, useRef, useState } from "react";
import FreeSlotsPicker from "@/components/FreeSlotsPicker";
import InterestForm from "@/components/InterestForm";
import WhatsAppContactButton from "@/components/WhatsAppContactButton";
import { contactFields, type ContactDraft } from "@/lib/propertyDetail";
import type { Property } from "@/types/property";

type Intent = "contact" | "visit";

export default function PropertyActions({ property }: {
  property: Pick<Property, "id" | "title" | "price" | "operation_type" | "status" | "agent_name">;
}) {
  const [intent, setIntent] = useState<Intent | null>(null);
  const [draft, setDraft] = useState<ContactDraft>(() => contactFields({}));
  const [busy, setBusy] = useState(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const contactButton = useRef<HTMLButtonElement>(null);
  const visitButton = useRef<HTMLButtonElement>(null);
  const busyRef = useRef(false);
  const inlineActions = useRef<HTMLDivElement>(null);
  const trigger = useRef<HTMLButtonElement | null>(null);
  const [pastActions, setPastActions] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);

  useEffect(() => {
    const element = inlineActions.current;
    if (!element) return;
    const observer = new IntersectionObserver(([entry]) => {
      setPastActions(!entry.isIntersecting && entry.boundingClientRect.bottom <= 0);
    });
    observer.observe(element);
    // Native modal dialogs from both the gallery and these actions suppress the bar.
    const updateDialogs = () => setDialogOpen(Boolean(document.querySelector("dialog[open]")));
    const dialogs = new MutationObserver(updateDialogs);
    dialogs.observe(document.body, { subtree: true, attributes: true, attributeFilter: ["open"] });
    updateDialogs();
    return () => { observer.disconnect(); dialogs.disconnect(); };
  }, []);

  function openAction(action: Intent, button: HTMLButtonElement) {
    trigger.current = button;
    setIntent(action);
  }
  const available = property.status === "disponible";

  useEffect(() => { busyRef.current = busy; }, [busy]);
  useEffect(() => {
    if (!intent || !available) return;
    const dialog = dialogRef.current;
    const overflow = document.body.style.overflow;
    dialog?.showModal();
    document.body.style.overflow = "hidden";
    return () => {
      dialog?.close();
      document.body.style.overflow = overflow;
      requestAnimationFrame(() => {
        const original = trigger.current;
        if (original?.isConnected) original.focus();
        else {
          const barButton = document.querySelector<HTMLButtonElement>(`footer [data-action="${intent}"]`);
          (barButton ?? (intent === "contact" ? contactButton : visitButton).current)?.focus();
        }
      });
    };
  }, [intent, available]);

  function close() {
    if (!busyRef.current) dialogRef.current?.close();
  }

  return (
    <>
      <div ref={inlineActions} className="mt-5">
        {available ? <div className="grid grid-cols-2 gap-3">
          <button ref={contactButton} data-action="contact" type="button" onClick={(event) => openAction("contact", event.currentTarget)}
            className="min-h-11 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Contactar agente</button>
          <button ref={visitButton} data-action="visit" type="button" onClick={(event) => openAction("visit", event.currentTarget)}
            className="min-h-11 rounded-lg border border-blue-700 bg-white px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Agendar visita</button>
        </div> : <p className="text-sm text-slate-600">Propiedad reservada. Contacto y visitas no disponibles.</p>}
      </div>
      {intent === null && pastActions && !dialogOpen && (
        <footer aria-label="Precio y acciones del inmueble"
          className="[@media(max-height:450px)]:hidden fixed inset-x-0 bottom-0 z-40 border-t border-slate-200 bg-white/95 px-4 pt-3 shadow-[0_-4px_20px_rgba(15,23,42,0.06)] backdrop-blur sm:px-6"
          style={{ paddingBottom: "calc(0.75rem + env(safe-area-inset-bottom))" }}>
          <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-baseline gap-x-3">
              <p className="text-xs font-medium text-slate-500">{property.operation_type === "arriendo" ? "Alquiler mensual" : "Precio de venta"}</p>
              <p className="text-xl font-bold text-slate-900">
                {Number(property.price).toLocaleString("es-EC", { style: "currency", currency: "USD" })}
                {property.operation_type === "arriendo" && <span className="ml-1 text-sm font-medium text-slate-500">/ mes</span>}
              </p>
            </div>
            {available ? (
              <div className="grid grid-cols-2 gap-3 sm:flex">
                <button data-action="contact" type="button" onClick={(event) => openAction("contact", event.currentTarget)}
                  className="min-h-11 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Contactar agente</button>
                <button data-action="visit" type="button" onClick={(event) => openAction("visit", event.currentTarget)}
                  className="min-h-11 rounded-lg border border-blue-700 bg-white px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Agendar visita</button>
              </div>
            ) : (
              <p className="text-sm text-slate-600">Propiedad reservada. Contacto y visitas no disponibles.</p>
            )}
          </div>
        </footer>
      )}

      <dialog ref={dialogRef} aria-labelledby="property-action-title" onClose={() => setIntent(null)}
        onCancel={(event) => { if (busyRef.current) event.preventDefault(); }}
        onClick={(event) => { if (event.target === event.currentTarget) close(); }}
        className="m-auto max-h-[94dvh] w-[calc(100%-1rem)] max-w-2xl overflow-hidden rounded-2xl bg-white p-0 text-slate-900 shadow-2xl backdrop:bg-slate-900/40">
        <header className="flex items-center justify-between gap-4 border-b border-slate-200 px-4 py-3 sm:px-6">
          <h2 id="property-action-title" className="text-lg font-bold">{intent === "visit" ? "Agendar visita" : "Contactar agente"}</h2>
          <button type="button" onClick={close} disabled={busy}
            className="min-h-11 rounded-lg px-3 text-sm font-semibold text-slate-600 hover:bg-slate-100 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-blue-700">Cerrar</button>
        </header>
        <div className="max-h-[calc(94dvh-72px)] overflow-y-auto overscroll-contain px-4 pt-4 sm:px-6"
          style={{ paddingBottom: "calc(1rem + env(safe-area-inset-bottom))" }}>
          <p className="text-sm font-semibold text-slate-800">{property.title}</p>
          {property.agent_name && <p className="mt-1 text-sm text-slate-500">Asesor responsable: {property.agent_name}</p>}
          {available && intent === "contact" && (
            <>
              <WhatsAppContactButton propertyId={property.id} title={property.title} />
              <p className="mt-6 border-t border-slate-200 pt-5 text-sm font-semibold text-slate-700">O déjanos tus datos</p>
              <InterestForm propertyId={property.id} initialContact={draft} onContactChange={setDraft} onBusyChange={setBusy} />
            </>
          )}
          {available && intent === "visit" && (
            <FreeSlotsPicker propertyId={property.id} initialContact={draft} onContactChange={setDraft} onBusyChange={setBusy} />
          )}
        </div>
      </dialog>
    </>
  );
}
