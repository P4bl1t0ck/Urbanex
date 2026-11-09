// Fechas y horas del agendamiento en hora de Ecuador (America/Guayaquil, sin horario de verano),
// sin importar la zona del navegador (lote 2: I-09, P-07 e I-08). Funciones puras: las prueba
// visitsCalendar.test.mjs con `npm test`. Las fechas sin hora son cadenas "AAAA-MM-DD".

export const ECUADOR_TIME_ZONE = "America/Guayaquil";

const isoDateFormat = new Intl.DateTimeFormat("en-CA", {
  timeZone: ECUADOR_TIME_ZONE,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

const timeFormat = new Intl.DateTimeFormat("es-EC", {
  timeZone: ECUADOR_TIME_ZONE,
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

// Fecha calendario: se interpreta a medianoche UTC solo para contar días, nunca para mostrar horas.
function toUtcDate(isoDate: string) {
  return new Date(`${isoDate}T00:00:00Z`);
}

function fromUtcDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

export function ecuadorToday(now: Date = new Date()) {
  return isoDateFormat.format(now);
}

export function ecuadorDateOf(isoDateTime: string) {
  return isoDateFormat.format(new Date(isoDateTime));
}

export function addDays(isoDate: string, days: number) {
  const date = toUtcDate(isoDate);
  date.setUTCDate(date.getUTCDate() + days);
  return fromUtcDate(date);
}

// 0 = lunes ... 6 = domingo, igual que el backend.
export function weekdayOf(isoDate: string) {
  return (toUtcDate(isoDate).getUTCDay() + 6) % 7;
}

export function weekStart(isoDate: string) {
  return addDays(isoDate, -weekdayOf(isoDate));
}

export function weekRange(isoDate: string) {
  const from = weekStart(isoDate);
  return { from, to: addDays(from, 6) };
}

export function daysBetween(from: string, to: string) {
  const days: string[] = [];
  for (let day = from; day <= to; day = addDays(day, 1)) days.push(day);
  return days;
}

export function formatTime(isoDateTime: string) {
  return timeFormat.format(new Date(isoDateTime));
}

// "HH:MM:SS" (API) -> "HH:MM" (input type=time y pantalla).
export function toHourMinute(value: string | null) {
  return value ? value.slice(0, 5) : "";
}

export function formatDayLabel(isoDate: string, options: { weekday?: boolean } = {}) {
  return new Intl.DateTimeFormat("es-EC", {
    timeZone: "UTC",
    weekday: options.weekday === false ? undefined : "long",
    day: "numeric",
    month: "short",
  }).format(toUtcDate(isoDate));
}

export function formatWeekLabel(from: string, to: string) {
  return `Semana del ${formatDayLabel(from, { weekday: false })} al ${formatDayLabel(to, { weekday: false })}`;
}

// Agrupa por fecha de Ecuador y devuelve todas las fechas del rango, también las vacías.
export function groupByEcuadorDay<T>(
  items: T[],
  getStart: (item: T) => string,
  from: string,
  to: string,
) {
  const groups = new Map<string, T[]>(daysBetween(from, to).map((day) => [day, []]));
  for (const item of items) {
    const day = ecuadorDateOf(getStart(item));
    const bucket = groups.get(day);
    if (bucket) bucket.push(item);
  }
  return [...groups.entries()].map(([day, dayItems]) => ({ day, items: dayItems }));
}
