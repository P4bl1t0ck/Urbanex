"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function SiteNav() {
  const [userInfo, setUserInfo] = useState({ email: "", role: "" });
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Revisamos la "libreta" de la sesión actual
    const token = sessionStorage.getItem("access");
    if (token) {
      setIsLoggedIn(true);
      const email = sessionStorage.getItem("userEmail") || "Usuario";
      const role = sessionStorage.getItem("userRole") || "Asesor";
      setUserInfo({ email, role });
    }
  }, []);

  function handleLogout() {
    sessionStorage.removeItem("access");
    sessionStorage.removeItem("refresh");
    sessionStorage.removeItem("userEmail");
    sessionStorage.removeItem("userRole");
    router.replace("/login");
  }

  return (
    <nav className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo y Enlaces Principales */}
          <div className="flex items-center gap-8">
            <Link href="/" className="text-xl font-black tracking-wider text-blue-700 uppercase">
              Urbanex
            </Link>
            <div className="hidden md:flex gap-6">
              <Link href="/properties" className="text-sm font-medium text-slate-600 hover:text-blue-700 transition">
                Catálogo Público
              </Link>
            </div>
          </div>
          
          {/* Controles de Usuario */}
          <div className="flex items-center gap-4">
            {isLoggedIn ? (
              <>
                <Link href="/dashboard" className="text-sm font-medium text-slate-600 hover:text-blue-700 transition">
                  Mi Panel
                </Link>
                {/* La píldora con el usuario logueado */}
                <div className="hidden sm:flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-full border border-slate-200">
                  <span className="text-xs font-semibold text-slate-700">{userInfo.email}</span>
                  <span className="text-slate-300">|</span>
                  <span className="text-xs font-bold text-blue-700 capitalize">{userInfo.role}</span>
                </div>
                <button 
                  onClick={handleLogout}
                  className="text-sm font-medium text-red-600 hover:text-red-800 transition ml-2"
                >
                  Salir
                </button>
              </>
            ) : (
              <Link href="/login" className="bg-blue-700 hover:bg-blue-800 text-white px-4 py-2 rounded-lg text-sm font-semibold transition shadow-sm">
                Iniciar Sesión
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}