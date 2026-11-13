"use client";

// P-07 (HU-18, RF-09): franjas libres del asesor responsable en la ficha pública, próximos 14 días
// en hora de Ecuador. Se vuelve a consultar al pulsar "Actualizar" y al regresar a la pestaña,
// para reflejar en tiempo real los horarios ocupados.
// HU-19 (lote 3, DS-39): cada franja es un botón; al elegirla se abre VisitRequestForm. Si la
// franja se ocupó mientras tanto, el servidor responde 400 y aquí se vuelven a cargar los horarios.

import { useEffect, useState } from "react";
import VisitRequestForm from "@/components/VisitRequestForm";
import { ApiError } from "@/lib/api";
import { getFreeSlots } from "@/lib/visits";
import { addDays, ecuadorDateOf, ecuadorToday, formatDayLabel, formatTime, groupByEcuadorDay } from "@/lib/visitsCalendar";
import type { FreeSlot, FreeSlotsResponse, VisitRequestResponse } from "@/types/visit";

const RANGE_DAYS = 14;

type Loaded = { key: number; data: FreeSlotsResponse | null; error: string; hidden: boolean };

export default function FreeSlotsPicker({ propertyId }: { propertyId: number }) {
  const [reload, setReload] = useState(0);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [chosenDay, setChosenDay] = useState("");
  const [chosenSlot, setChosenSlot] = useState<FreeSlot | null>(null);
  const [requested, setRequested] = useState<VisitRequestResponse | null>(null);
  const [notice, setNotice] = useState("");

  const loading = loaded?.key !== reload;

  function finishRequest(result: VisitRequestResponse | null) {
    setChosenSlot(null);
    if (result) {
      setRequested(result);
      setNotice("");
    } else {
      setNotice("Ese horario se ocupó hace un momento. Elige otro de la lista actualizada.");
    }
    setReload((value) => value + 1);
  }

  useEffect(() => {
    let isActive = true;
    const key = reload;
    getFreeSlots(propertyId)
      .then((data) => {
        if (isActive) setLoaded({ key, data, error: "", hidden: false });
      })
      .catch((err) => {
        if (!isActive) return;
        if (err instanceof ApiError && err.status === 404) {
          // La propiedad dejó de estar Disponible: no se agenda (RF-04).
          setLoaded({ key, data: null, error: "", hidden: true });
          return;
        }
        setLoaded({
          key,
          data: null,
          hidden: false,
          error: err instanceof ApiError && err.status === 429
            ? "Hiciste muchas consultas seguidas. Espera un minuto y vuelve a intentar."
            : "No se pudieron cargar los horarios. Intenta nuevamente.",
        });
      });
    return () => {
      isActive = false;
    };
  }, [propertyId, reload]);

  useEffect(() => {
    function refreshWhenVisible() {
      if (document.visibilityState === "visible") setReload((value) => value + 1);
    }
    document.addEventListener("visibilitychange", refreshWhenVisible);
    return () => document.removeEventListener("visibilitychange", refreshWhenVisible);
  }, []);

  if (loaded?.hidden) return null;

  const data = loaded?.data ?? null;
  const today = data ? ecuadorToday() : "";
  const days = data
    ? groupByEcuadorDay(data.slots, (slot) => slot.start, today, addDays(today, RANGE_DAYS - 1))
    : [];
  const firstWithSlots = days.find((day) => day.items.length > 0)?.day ?? "";
  const selectedDay = days.some((day) => day.day === chosenDay && day.items.length > 0) ? chosenDay : firstWithSlots;
  const selectedSlots = days.find((day) => day.day === selectedDay)?.items ?? [];

  return (
    <section className="mt-8 rounded-xl border border-slate-200 bg-white p-6 shadow-sm" aria-labelledby="free-slots-title">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 id="free-slots-title" className="text-xl font-bold text-slate-900">Horarios disponibles para visitas</h2>
        <button
          type="button"
          onClick={() => setReload((value) => value + 1)}
          disabled={loading}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 hover:bg-slate-100 disabled:opacity-60"
        >
          Actualizar
        </button>
      </div>
      <p className="mt-1 text-sm text-slate-600">
        Próximos {RANGE_DAYS} días, en hora de Ecuador. Elige un horario para solicitar tu visita.
      </p>

      {requested && (
        <div role="status" className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
          <p className="font-semibold">{requested.detail}</p>
          <p className="mt-1">
            <span className="capitalize">{formatDayLabel(ecuadorDateOf(requested.scheduled_start))}</span>
            {" a las "}
            {formatTime(requested.scheduled_start)} (hora de Ecuador).
          </p>
          <p className="mt-1">
            {requested.confirmation === "email"
              ? "Te enviamos la confirmación a tu correo, con el enlace para ver los datos de tu visita."
              : "El asesor te confirmará la visita por WhatsApp."}
          </p>
        </div>
      )}
      {notice && (
        <p role="alert" className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{notice}</p>
      )}

      {loading && !data ? (
        <p className="mt-4 text-sm text-slate-500">Cargando horarios…</p>
      ) : loaded?.error ? (
        <p role="alert" className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{loaded.error}</p>
      ) : !firstWithSlots ? (
        <p className="mt-4 rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-600">
          El asesor no tiene horarios libres en los próximos {RANGE_DAYS} días.
        </p>
      ) : (
        <>
          <div role="tablist" aria-label="Días con horarios libres" className="mt-4 flex gap-2 overflow-x-auto pb-2">
            {days.filter((day) => day.items.length > 0).map((day) => (
              <button
                key={day.day}
                type="button"
                role="tab"
                aria-selected={day.day === selectedDay}
                onClick={() => setChosenDay(day.day)}
                className={`shrink-0 rounded-lg border px-3 py-2 text-left text-sm transition ${
                  day.day === selectedDay
                    ? "border-blue-600 bg-blue-50 text-blue-900"
                    : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
                }`}
              >
                <span className="block font-semibold capitalize">{formatDayLabel(day.day)}</span>
                <span className="block text-xs text-slate-500">
                  {day.items.length} {day.items.length === 1 ? "horario" : "horarios"}
                </span>
              </button>
            ))}
          </div>
          <ul role="tabpanel" className="mt-3 flex flex-wrap gap-2">
            {selectedSlots.map((slot) => {
              const isChosen = chosenSlot?.start === slot.start;
              return (
                <li key={slot.start}>
                  <button
                    type="button"
                    aria-pressed={isChosen}
                    onClick={() => {
                      setChosenSlot(slot);
                      setNotice("");
                    }}
                    className={`rounded-lg border px-3 py-1.5 text-sm font-semibold transition ${
                      isChosen
                        ? "border-blue-700 bg-blue-700 text-white"
                        : "border-slate-200 bg-slate-50 text-slate-800 hover:border-blue-400 hover:bg-blue-50"
                    }`}
                  >
                    {formatTime(slot.start)}
                  </button>
                </li>
              );
            })}
          </ul>
        </>
      )}

      {chosenSlot && (
        <VisitRequestForm
          key={chosenSlot.start}
          propertyId={propertyId}
          slot={chosenSlot}
          onCancel={() => setChosenSlot(null)}
          onDone={finishRequest}
        />
      )}
    </section>
  );
}
