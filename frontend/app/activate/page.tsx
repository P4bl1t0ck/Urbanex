"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { ApiError, apiFetch } from "@/lib/api";

export default function ActivateAccountPage() {
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function activate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const hash = window.location.hash.slice(1);
    const token =
      new URLSearchParams(hash).get("token") ??
      (hash && !hash.includes("=") ? hash : null) ??
      new URLSearchParams(window.location.search).get("token");
    if (!token) {
      setError("El enlace no incluye un token. Solicita que te envíen otro enlace.");
      return;
    }

    if (password !== confirmation) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);
    try {
      const response = await apiFetch<{ detail: string }>("/api/auth/users/activate/", {
        method: "POST",
        body: JSON.stringify({ token, password }),
      });
      setSuccess(response.detail);
      setPassword("");
      setConfirmation("");
    } catch (activationError: unknown) {
      if (activationError instanceof ApiError && activationError.status === 400) {
        const body = activationError.body;
        const tokenError =
          body && typeof body === "object" && "token" in body
            ? body.token
            : null;
        if (tokenError) {
          setError(
            "El enlace ya se usó, venció o no es válido. Si ya activaste tu cuenta, intenta iniciar sesión. Si no, solicita al administrador que reenvíe la invitación.",
          );
        } else {
          setError(activationError.message);
        }
      } else {
        setError(
          activationError instanceof Error
            ? activationError.message
            : "No se pudo activar la cuenta. Solicita un nuevo enlace al administrador.",
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-16">
      <section className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Urbanex</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Activa tu cuenta</h1>
        <p className="mt-2 text-sm text-slate-600">
          Define una contraseña para completar la activación. El enlace es de un solo uso y vence en 24 horas.
        </p>

        <form onSubmit={activate} className="mt-6 space-y-4">
          <label className="block text-sm font-medium text-slate-700">
            Nueva contraseña
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Confirma la contraseña
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
          {success && <p role="status" className="text-sm text-green-700">{success}</p>}
          <button
            type="submit"
            disabled={loading || Boolean(success)}
            className="w-full rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
          >
            {loading ? "Activando..." : "Activar cuenta"}
          </button>
        </form>

        <Link href="/login" className="mt-5 inline-block text-sm font-semibold text-blue-700 hover:underline">
          Ir a iniciar sesión
        </Link>
      </section>
    </main>
  );
}
