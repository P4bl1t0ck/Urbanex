"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useSyncExternalStore } from "react";
import {
  clearAuthSession,
  getAuthSessionSnapshot,
  subscribeToAuthSession,
} from "@/lib/auth-session";

const links = [
  { href: "/properties", label: "Propiedades" },
  { href: "/dashboard", label: "Panel del agente" },
];

export default function SiteNav() {
  const pathname = usePathname();
  const router = useRouter();
  const sessionSnapshot = useSyncExternalStore(
    subscribeToAuthSession,
    getAuthSessionSnapshot,
    () => "",
  );
  const session = sessionSnapshot
    ? (JSON.parse(sessionSnapshot) as { access: string | null; email: string | null })
    : null;

  function handleLogout() {
    clearAuthSession();
    router.replace("/login");
  }

  return (
    <nav className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <Link
          href="/properties"
          className="text-xl font-extrabold tracking-tight text-slate-900"
        >
          Urbanex
        </Link>
        <div className="flex items-center gap-1 sm:gap-2">
          {links.map(({ href, label }) => {
            const isActive = pathname === href || pathname.startsWith(`${href}/`);

            return (
              <Link
                key={href}
                href={href}
                aria-current={isActive ? "page" : undefined}
                className={`rounded-lg px-3 py-2 text-sm font-semibold transition ${
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
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
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
