"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useSyncExternalStore } from "react";
import { logoutRefreshSession } from "@/lib/api";
import {
  clearAuthSession,
  getAuthSessionSnapshot,
  subscribeToAuthSession,
} from "@/lib/auth-session";

type NavLink = { href: string; label: string; exact?: boolean };

const PUBLIC_LINKS: NavLink[] = [
  { href: "/properties", label: "Propiedades" },
  // Exacto: si no, quedaría resaltado junto con Oportunidades, Disponibilidad o Agenda.
  { href: "/dashboard", label: "Panel del agente", exact: true },
];

// Asesor y admin (los únicos roles, C-08). El rol solo decide qué enlaces se muestran: los
// permisos los aplica el servidor. Usuarios (HU-44) sigue como botón del panel, no aquí.
const INTERNAL_LINKS: NavLink[] = [
  { href: "/dashboard/opportunities", label: "Oportunidades" }, // I-06 (HU-34)
  { href: "/dashboard/availability", label: "Disponibilidad" }, // I-09 (HU-22)
  { href: "/dashboard/agenda", label: "Agenda" }, // I-08 (HU-24)
];

const INTERNAL_ROLES = ["admin", "asesor"];

export default function SiteNav() {
  const pathname = usePathname();
  const router = useRouter();
  const sessionSnapshot = useSyncExternalStore(
    subscribeToAuthSession,
    getAuthSessionSnapshot,
    () => "",
  );
  const session = sessionSnapshot
    ? (JSON.parse(sessionSnapshot) as { access: string | null; email: string | null; role: string | null })
    : null;
  const hasSession = Boolean(session?.access);
  const isInternal = hasSession && INTERNAL_ROLES.includes(session?.role ?? "");
  const links = isInternal ? [...PUBLIC_LINKS, ...INTERNAL_LINKS] : PUBLIC_LINKS;

  function handleLogout() {
    void logoutRefreshSession().catch((error: unknown) => {
      console.error("No se pudo borrar la cookie de renovación:", error);
    });
    clearAuthSession();
    router.replace("/login");
  }

  useEffect(() => {
    if (pathname.startsWith("/dashboard") && !hasSession) {
      router.replace("/login");
    }
  }, [hasSession, pathname, router]);

  return (
    <nav className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          href="/properties"
          className="shrink-0 text-xl font-extrabold tracking-tight text-slate-900"
        >
          Urbanex
        </Link>
        <div className="flex min-w-0 items-center gap-1 overflow-x-auto whitespace-nowrap sm:gap-2">
          {links.map(({ href, label, exact }) => {
            const isActive = pathname === href || (!exact && pathname.startsWith(`${href}/`));

            return (
              <Link
                key={href}
                href={href}
                aria-current={isActive ? "page" : undefined}
                className={`shrink-0 rounded-lg px-3 py-2 text-sm font-semibold transition ${
                  isActive
                    ? "bg-blue-50 text-blue-800"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {label}
              </Link>
            );
          })}
          {session?.access && (
            <>
              {session.email && (
                <span className="hidden max-w-48 truncate px-2 text-sm text-slate-600 lg:inline">
                  {session.email}
                </span>
              )}
              <button
                type="button"
                onClick={handleLogout}
                className="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
              >
                Cerrar sesión
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
