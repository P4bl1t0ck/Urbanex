"use client";

import { useEffect, useRef, useState } from "react";
import type { PropertyImage, PropertyStatus } from "@/types/property";

export default function PropertyGallery({ images, title, status }: {
  images: PropertyImage[];
  title: string;
  status: PropertyStatus;
}) {
  const [failed, setFailed] = useState<string[]>([]);
  const [openedPhoto, setOpenedPhoto] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const touchStart = useRef<{ x: number; y: number } | null>(null);
  const didSwipe = useRef(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const photoRefs = useRef(new Map<number, HTMLElement>());
  const photos = images.filter((photo) => photo.image);
  const selectedIndex = Math.max(0, photos.findIndex((photo) => photo.id === selectedId));
  const mainPhoto = photos[selectedIndex];
  const move = (step: number) => {
    if (photos.length > 1) setSelectedId(photos[(selectedIndex + step + photos.length) % photos.length].id);
  };

  useEffect(() => {
    if (openedPhoto === null) return;
    const dialog = dialogRef.current;
    const overflow = document.body.style.overflow;
    dialog?.showModal();
    document.body.style.overflow = "hidden";
    const frame = requestAnimationFrame(() => {
      photoRefs.current.get(openedPhoto)?.scrollIntoView({ block: "center" });
    });
    return () => {
      cancelAnimationFrame(frame);
      dialog?.close();
      document.body.style.overflow = overflow;
    };
  }, [openedPhoto]);

  const unavailable = (photo: PropertyImage) => failed.includes(photo.image);
  const markFailed = (photo: PropertyImage) => setFailed((previous) =>
    previous.includes(photo.image) ? previous : [...previous, photo.image]);

  return (
    <section aria-label={`Fotografías de ${title}`} className="min-w-0">
      <div className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-slate-100" style={{ touchAction: "pan-y" }}
        onKeyDown={(event) => {
          if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
            event.preventDefault();
            move(event.key === "ArrowLeft" ? -1 : 1);
          }
        }}
        onTouchStart={(event) => {
          didSwipe.current = false;
          const touch = event.touches[0];
          touchStart.current = touch ? { x: touch.clientX, y: touch.clientY } : null;
        }}
        onTouchEnd={(event) => {
          const touch = event.changedTouches[0];
          const start = touchStart.current;
          touchStart.current = null;
          if (!touch || !start) return;
          const dx = touch.clientX - start.x;
          const dy = touch.clientY - start.y;
          if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
            didSwipe.current = true;
            move(dx < 0 ? 1 : -1);
          }
        }} onTouchCancel={() => { touchStart.current = null; }}>
        {mainPhoto && !unavailable(mainPhoto) ? (
          <button type="button" onClick={() => {
            if (didSwipe.current) { didSwipe.current = false; return; }
            setOpenedPhoto(mainPhoto.id);
          }}
            aria-label={`Ver galería de fotografías de ${title}`}
            className="absolute inset-0 cursor-zoom-in focus-visible:outline-2 focus-visible:outline-offset-[-4px] focus-visible:outline-blue-700">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={mainPhoto.image} alt={`${title}, fotografía ${selectedIndex + 1}`}
              decoding="async" className="block h-full w-full object-contain"
              onError={() => markFailed(mainPhoto)} />
          </button>
        ) : (
          <p className="flex min-h-48 items-center justify-center px-6 text-center text-slate-600">
            {mainPhoto ? "No se pudo cargar esta fotografía" : "Fotografías no disponibles"}
          </p>
        )}
        {photos.length > 1 && (
          <>
            <button type="button" onClick={() => move(-1)} aria-label="Fotografía anterior"
              className="absolute left-3 top-1/2 min-h-11 min-w-11 -translate-y-1/2 rounded-full bg-white/95 text-2xl text-slate-800 shadow focus-visible:outline-2 focus-visible:outline-blue-700">‹</button>
            <button type="button" onClick={() => move(1)} aria-label="Fotografía siguiente"
              className="absolute right-3 top-1/2 min-h-11 min-w-11 -translate-y-1/2 rounded-full bg-white/95 text-2xl text-slate-800 shadow focus-visible:outline-2 focus-visible:outline-blue-700">›</button>
          </>
        )}
        <span className="pointer-events-none absolute left-4 top-4 inline-flex items-center gap-2 rounded-full bg-white/95 px-3 py-2 text-sm font-semibold text-slate-800 shadow-sm">
          <span aria-hidden="true" className={`h-2.5 w-2.5 rounded-full ${status === "disponible" ? "bg-emerald-500" : "bg-amber-500"}`} />
          {status === "reservador" ? "Reservado" : "Disponible"}
        </span>
      </div>

      {photos.length > 1 && (
        <div className="mt-4 overflow-x-auto p-1" aria-label="Seleccionar fotografía principal">
          <div className="mx-auto flex w-max min-w-full items-center justify-center gap-3">
          {photos.map((photo, index) => (
            <button key={photo.id} type="button" onClick={() => setSelectedId(photo.id)}
              aria-label={`Seleccionar fotografía ${index + 1}`} aria-pressed={mainPhoto?.id === photo.id}
              className={`h-28 w-36 shrink-0 overflow-hidden rounded-xl border-2 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 sm:h-32 sm:w-44 ${mainPhoto?.id === photo.id ? "border-blue-700" : "border-transparent"}`}>
              {unavailable(photo) ? <span className="px-2 text-sm text-slate-500">Imagen no disponible</span> : (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={photo.image} alt="" loading="lazy" decoding="async"
                  className="block h-full w-full object-cover" onError={() => markFailed(photo)} />
              )}
            </button>
          ))}
          </div>
        </div>
      )}

      <dialog ref={dialogRef} onClose={() => setOpenedPhoto(null)}
        aria-label={`Galería de ${title}`}
        className="m-auto max-h-[94dvh] w-[96vw] max-w-7xl overflow-hidden rounded-2xl bg-white p-0 text-slate-900 shadow-2xl backdrop:bg-slate-900/40"
        onClick={(event) => { if (event.target === event.currentTarget) setOpenedPhoto(null); }}>
        <header className="flex items-center justify-between gap-4 border-b border-slate-200 px-4 py-3 sm:px-6">
          <h2 className="min-w-0 truncate font-semibold">{title}</h2>
          <button type="button" onClick={() => setOpenedPhoto(null)}
            className="min-h-11 shrink-0 rounded-lg px-4 font-semibold text-slate-700 hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-blue-700">Cerrar</button>
        </header>
        <div tabIndex={0} role="region" aria-label="Todas las fotografías del inmueble"
          className="max-h-[calc(94dvh-72px)] overflow-y-auto overscroll-contain bg-white p-2 focus-visible:outline-2 focus-visible:outline-blue-700">
          <div className="columns-1 gap-2 sm:columns-2">
            {photos.map((photo, index) => (
              <figure key={photo.id} ref={(element) => {
                if (element) photoRefs.current.set(photo.id, element);
                else photoRefs.current.delete(photo.id);
              }} className="m-0 mb-2 break-inside-avoid overflow-hidden rounded-lg bg-white">
                  {unavailable(photo) ? (
                    <p className="flex min-h-32 items-center justify-center text-slate-500">No se pudo cargar esta fotografía</p>
                  ) : (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={photo.image} alt={`${title}, fotografía ${index + 1}`}
                      loading="lazy" decoding="async" className="block h-auto w-full"
                      onError={() => markFailed(photo)} />
                  )}
              </figure>
            ))}
          </div>
        </div>
      </dialog>
    </section>
  );
}
