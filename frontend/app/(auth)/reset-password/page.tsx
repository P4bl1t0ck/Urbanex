"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { ApiError, apiFetch } from "@/lib/api";

export default function ResetPasswordPage() {
  const tokenRef = useRef("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const tokenFromLink = new URLSearchParams(window.location.hash.slice(1)).get("token");
    if (tokenFromLink) tokenRef.current = tokenFromLink;
    window.history.replaceState(
      null,
      "",
      `${window.location.pathname}${window.location.search}`,
    );
  }, []);

  async function resetPassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setSuccess("");

    if (!tokenRef.current) {
      setError("El enlace no incluye un token. Solicita que te envíen otro enlace.");
      return;
    }
    if (password !== confirmation) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    setLoading(true);
    try {
      const response = await apiFetch<{ detail: string }>(
        "/api/auth/password-reset/confirm/",
        {
          method: "POST",
          body: JSON.stringify({ token: tokenRef.current, password }),
        },
      );
      setSuccess(response.detail);
      setPassword("");
      setConfirmation("");
    } catch (resetError: unknown) {
      setError(
        resetError instanceof ApiError
          ? resetError.message
          : resetError instanceof Error
            ? resetError.message
            : "No se pudo restablecer la contraseña. Intenta de nuevo.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-16">
      <section className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Urbanex</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Define una nueva contraseña</h1>
        <p className="mt-2 text-sm text-slate-600">
          El enlace solo puede utilizarse una vez y vence a los 60 minutos.
        </p>

        <p className="mt-6 text-sm text-slate-600">
          ¿No tienes el enlace o ya venció? Solicita uno nuevo.
        </p>
        <Link
          href="/forgot-password"
          className="mt-2 inline-block text-sm font-semibold text-blue-700 hover:underline"
        >
          Solicitar enlace nuevo
        </Link>

        <form onSubmit={resetPassword} className="mt-6 space-y-4">
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
            {loading ? "Guardando..." : "Restablecer contraseña"}
          </button>
        </form>

        <Link href="/login" className="mt-5 inline-block text-sm font-semibold text-blue-700 hover:underline">
          Ir a iniciar sesión
        </Link>
      </section>
    </main>
  );
}
