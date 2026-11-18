"use client";

import Link from "next/link";
import { useEffect, useState, useSyncExternalStore } from "react";
import { ApiError, authFetch } from "@/lib/api";
import { getAuthSessionSnapshot, subscribeToAuthSession } from "@/lib/auth-session";
import type { DevStats } from "@/types/telemetry";

const number = (value: number) => value.toLocaleString("es-EC");
function bytes(value: number) {
  if (value < 1024) return `${number(value)} B`;
  if (value < 1024 ** 2) return `${(value / 1024).toLocaleString("es-EC", { maximumFractionDigits: 2 })} KiB`;
  return `${(value / 1024 ** 2).toLocaleString("es-EC", { maximumFractionDigits: 2 })} MiB`;
}

export default function DevStatsPage() {
  const snapshot = useSyncExternalStore(subscribeToAuthSession, getAuthSessionSnapshot, () => "");
  const session = snapshot ? JSON.parse(snapshot) as { access: string | null; role: string | null } : null;
  const isAdmin = Boolean(session?.access && session.role === "admin");
  const [result, setResult] = useState<{ stats?: DevStats; error?: string; snapshot: string } | null>(null);
  const [revision, setRevision] = useState(0);
  const current = result?.snapshot === snapshot ? result : null;
  const loading = isAdmin && current === null;

  useEffect(() => {
    if (!isAdmin) return;
    let active = true;
    authFetch<DevStats>("/api/dev/stats/")
      .then((stats) => { if (active) setResult({ stats, snapshot }); })
      .catch((error: unknown) => {
        if (!active) return;
        const message = error instanceof ApiError && error.status === 403
          ? "No tienes permiso para consultar estas estadísticas."
          : error instanceof ApiError && error.status === 401
            ? "Tu sesión venció. Vuelve a iniciar sesión."
            : "No se pudieron cargar las estadísticas. Intenta actualizar nuevamente.";
        setResult({ error: message, snapshot });
      });
    return () => { active = false; };
  }, [isAdmin, snapshot, revision]);

  const stats = isAdmin ? current?.stats : undefined;

  return <main className="mx-auto min-h-screen max-w-6xl px-4 py-6 sm:px-6">
    <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">← Volver al panel</Link>
    <div className="mt-5 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Estadísticas de uso</h1>
        <p className="mt-1 text-sm text-slate-600">Inventario de archivos y actividad registrada de los mapas.</p>
      </div>
      {isAdmin && <button type="button" disabled={loading} onClick={() => { setResult(null); setRevision((value) => value + 1); }}
        className="min-h-11 rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">
        {loading ? "Actualizando…" : "Actualizar"}
      </button>}
    </div>

    {!snapshot ? <p role="status" className="mt-6 text-slate-600">Comprobando sesión…</p>
      : !isAdmin ? <p role="alert" className="mt-6 rounded-xl bg-amber-50 p-4 text-amber-900">Esta sección está disponible solo para administradores.</p>
      : loading ? <p role="status" className="mt-6 text-slate-600">Cargando estadísticas…</p>
      : current?.error ? <p role="alert" className="mt-6 rounded-xl bg-amber-50 p-4 text-amber-900">{current.error}</p> : null}

    {stats && <>
      <p className="mt-6 text-sm text-slate-500">Actualizado: {new Date(stats.generated_at).toLocaleString("es-EC", { timeZone: stats.period.timezone })}. Mapas: {stats.period.from} al {stats.period.to}.</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-3">
        <section className="rounded-xl border border-slate-200 bg-slate-50 p-5">
          <h2 className="font-semibold text-slate-700">Cargas de mapas este mes</h2>
          <p className="mt-2 text-3xl font-bold text-blue-800">{number(stats.maps.total)}</p>
          <p className="mt-2 text-sm text-slate-600">Inicializaciones reportadas desde las fichas. No son visitantes únicos ni cobros de Google.</p>
        </section>
        <section className="rounded-xl border border-slate-200 bg-slate-50 p-5">
          <h2 className="font-semibold text-slate-700">Fotos registradas</h2>
          <p className="mt-2 text-3xl font-bold text-blue-800">{number(stats.images.registered_files)}</p>
          <p className="mt-2 text-sm text-slate-600">Locales: {number(stats.images.local_references)} · Cloudinary: {number(stats.images.cloudinary_references)}</p>
        </section>
        <section className="rounded-xl border border-slate-200 bg-slate-50 p-5">
          <h2 className="font-semibold text-slate-700">Versiones de documentos</h2>
          <p className="mt-2 text-3xl font-bold text-blue-800">{number(stats.documents.registered_versions)}</p>
          <p className="mt-2 text-sm text-slate-600">Actuales: {number(stats.documents.current_versions)} · {bytes(stats.documents.registered_bytes_all_versions)} registrados entre todas las versiones.</p>
        </section>
      </div>

      <section className="mt-8" aria-labelledby="map-daily">
        <h2 id="map-daily" className="text-lg font-bold text-slate-900">Actividad diaria de mapas</h2>
        {stats.maps.daily.length === 0 ? <p className="mt-3 rounded-xl border border-slate-200 p-5 text-sm text-slate-600">Todavía no hay cargas registradas este mes. El registro comienza cuando se inicializa un mapa de ficha.</p>
          : <div className="mt-3 overflow-x-auto rounded-xl border border-slate-200">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">Inicializaciones reportadas por día, pantalla y proveedor</caption>
              <thead className="bg-slate-50 text-slate-600"><tr>
                {['Fecha', 'Pantalla', 'Tecnología', 'Cargas'].map((title) => <th key={title} scope="col" className="px-4 py-3">{title}</th>)}
              </tr></thead>
              <tbody>{stats.maps.daily.map((row) => <tr key={`${row.day}-${row.screen}-${row.provider}`} className="border-t border-slate-200">
                <td className="whitespace-nowrap px-4 py-3">{row.day}</td>
                <td className="px-4 py-3">{row.screen === 'detail' ? 'Ficha de inmueble' : row.screen}</td>
                <td className="px-4 py-3">{row.provider === 'leaflet' ? 'Leaflet' : row.provider}</td>
                <td className="px-4 py-3">{number(row.loads)}</td>
              </tr>)}</tbody>
            </table>
          </div>}
      </section>

      <section className="mt-8 rounded-xl border border-slate-200 p-5">
        <h2 className="text-lg font-bold text-slate-900">Cómo interpretar estos datos</h2>
        <p className="mt-3 text-sm text-slate-600">{stats.inventory_note}</p>
        <p className="mt-2 text-sm text-slate-600">{stats.maps.limitations}</p>
        <p className="mt-2 text-sm text-slate-600">Los documentos permanecen en almacenamiento privado local. Su tamaño es el declarado en los registros.</p>
        <p className="mt-2 text-sm text-slate-600">Sin medir todavía: peso de fotos, transferencia, transformaciones de Cloudinary, correos, tamaño de la base de datos, tráfico del alojamiento y archivos sin registro. Los costos y cupos oficiales se consultan con cada proveedor.</p>
      </section>
    </>}
  </main>;
}
