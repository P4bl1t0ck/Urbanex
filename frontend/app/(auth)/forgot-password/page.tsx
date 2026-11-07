"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { ApiError, apiFetch } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function requestReset(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const response = await apiFetch<{ detail: string }>(
        "/api/auth/password-reset/request/",
        {
          method: "POST",
          body: JSON.stringify({ email }),
        },
      );
      setMessage(response.detail);
    } catch (requestError: unknown) {
      setError(
        requestError instanceof ApiError
          ? requestError.message
          : requestError instanceof Error
            ? requestError.message
            : "No se pudo procesar la solicitud. Intenta de nuevo.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-16">
      <section className="mx-auto max-w-md rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Urbanex</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Recuperar contraseña</h1>
        <p className="mt-2 text-sm text-slate-600">
          Escribe el correo de tu cuenta. Si está registrado, recibirás un enlace válido por 60 minutos.
        </p>

        <form onSubmit={requestReset} className="mt-6 space-y-4">
          <label className="block text-sm font-medium text-slate-700">
            Correo electrónico
            <input
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </label>
          {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
          {message && <p role="status" className="text-sm text-green-700">{message}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
          >
            {loading ? "Enviando..." : "Enviar instrucciones"}
          </button>
        </form>

        <Link href="/login" className="mt-5 inline-block text-sm font-semibold text-blue-700 hover:underline">
          Volver a iniciar sesión
        </Link>
      </section>
    </main>
  );
}
