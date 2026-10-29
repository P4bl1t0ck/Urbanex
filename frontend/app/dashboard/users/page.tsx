"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";
import { ApiError, authFetch } from "@/lib/api";
import type { ManagedUser, ManagedUserInput, UserRole } from "@/types/user";

const EMPTY_FORM: ManagedUserInput = {
  email: "",
  first_name: "",
  last_name: "",
  phone: "",
  role: "asesor",
};

const inputClass =
  "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100";

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Ocurrió un error inesperado.";
}

export default function UserManagementPage() {
  const router = useRouter();
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<ManagedUserInput>(EMPTY_FORM);
  const [editingUser, setEditingUser] = useState<ManagedUser | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [deactivatingUser, setDeactivatingUser] = useState<ManagedUser | null>(null);
  const [deactivationReason, setDeactivationReason] = useState("");

  useEffect(() => {
    const token = sessionStorage.getItem("access");
    const role = sessionStorage.getItem("userRole");
    if (!token) {
      router.replace("/login");
      return;
    }
    if (role !== "admin") {
      router.replace("/dashboard");
      return;
    }

    let active = true;
    async function loadUsers() {
      try {
        const data = await authFetch<ManagedUser[]>("/api/auth/users/");
        if (active) setUsers(data);
      } catch (loadError: unknown) {
        if (loadError instanceof ApiError && loadError.status === 401) {
          sessionStorage.removeItem("access");
          sessionStorage.removeItem("refresh");
          router.replace("/login");
          return;
        }
        if (active) setError(getErrorMessage(loadError));
      } finally {
        if (active) setLoading(false);
      }
    }

    void loadUsers();

    return () => {
      active = false;
    };
  }, [router]);

  function startCreate() {
    setEditingUser(null);
    setForm(EMPTY_FORM);
    setError("");
    setNotice("");
    setShowForm(true);
  }

  function startEdit(user: ManagedUser) {
    setEditingUser(user);
    setForm({
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      phone: user.phone,
      role: user.role,
    });
    setError("");
    setNotice("");
    setShowForm(true);
  }

  async function submitUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setNotice("");

    try {
      const saved = editingUser
        ? await authFetch<ManagedUser>(`/api/auth/users/${editingUser.id}/`, {
            method: "PATCH",
            body: JSON.stringify({
              first_name: form.first_name,
              last_name: form.last_name,
              phone: form.phone,
              role: form.role,
            }),
          })
        : await authFetch<ManagedUser>("/api/auth/users/", {
            method: "POST",
            body: JSON.stringify(form),
          });

      if (editingUser) {
        setUsers((current) => current.map((user) => (user.id === saved.id ? saved : user)));
        setNotice("Cambios guardados.");
      } else {
        setUsers((current) => [...current, saved].sort((a, b) => a.email.localeCompare(b.email)));
        setNotice("Usuario creado. El enlace se envió por el canal configurado; en desarrollo, revisa la consola de Django.");
      }
      setShowForm(false);
    } catch (saveError: unknown) {
      setError(getErrorMessage(saveError));
    } finally {
      setSaving(false);
    }
  }

  async function deactivateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!deactivatingUser) return;

    setSaving(true);
    setError("");
    setNotice("");
    try {
      const updated = await authFetch<ManagedUser>(
        `/api/auth/users/${deactivatingUser.id}/deactivate/`,
        {
          method: "POST",
          body: JSON.stringify({ reason: deactivationReason }),
        },
      );
      setUsers((current) => current.map((user) => (user.id === updated.id ? updated : user)));
      setDeactivatingUser(null);
      setDeactivationReason("");
      setNotice("Usuario desactivado; su historial se conservó.");
    } catch (deactivationError: unknown) {
      setError(getErrorMessage(deactivationError));
    } finally {
      setSaving(false);
    }
  }

  async function resendActivation(user: ManagedUser) {
    setSaving(true);
    setError("");
    setNotice("");
    try {
      const response = await authFetch<{ detail: string }>(
        `/api/auth/users/${user.id}/resend-activation/`,
        { method: "POST", body: JSON.stringify({}) },
      );
      setNotice(response.detail);
    } catch (resendError: unknown) {
      setError(getErrorMessage(resendError));
    } finally {
      setSaving(false);
    }
  }

  function cancelEdit() {
    setShowForm(false);
    setEditingUser(null);
    setError("");
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <Link href="/dashboard" className="text-sm font-semibold text-blue-700 hover:underline">
              ← Volver a mis propiedades
            </Link>
            <p className="mt-4 text-sm font-semibold uppercase tracking-wider text-blue-700">A-01</p>
            <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
              Administración de usuarios
            </h1>
            <p className="mt-2 text-slate-600">
              Crea cuentas, edita perfiles permitidos y desactiva usuarios sin borrar su historial.
            </p>
          </div>
          <button
            type="button"
            onClick={startCreate}
            className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-800"
          >
            + Crear usuario
          </button>
        </header>

        {error && (
          <div role="alert" className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            {error}
          </div>
        )}
        {notice && (
          <div role="status" className="mb-5 rounded-lg border border-green-200 bg-green-50 p-3 text-sm text-green-800">
            {notice}
          </div>
        )}

        {showForm && (
          <section aria-labelledby="user-form-title" className="mb-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 id="user-form-title" className="text-lg font-semibold text-slate-900">
              {editingUser ? "Editar perfil" : "Crear cuenta"}
            </h2>
            {!editingUser && (
              <p className="mt-1 text-sm text-slate-600">
                La cuenta quedará inactiva hasta que la persona establezca su contraseña desde el enlace enviado.
              </p>
            )}
            <form onSubmit={submitUser} className="mt-5 grid gap-4 sm:grid-cols-2">
              <label className="text-sm font-medium text-slate-700">
                Correo electrónico
                <input
                  type="email"
                  required
                  disabled={Boolean(editingUser)}
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  className={`${inputClass} disabled:bg-slate-100`}
                />
                {editingUser && <span className="mt-1 block text-xs text-slate-500">El correo no se puede editar.</span>}
              </label>
              <label className="text-sm font-medium text-slate-700">
                Rol
                <select
                  value={form.role}
                  onChange={(event) => setForm((current) => ({ ...current, role: event.target.value as UserRole }))}
                  className={inputClass}
                >
                  <option value="asesor">Asesor</option>
                  <option value="admin">Administrador</option>
                </select>
              </label>
              <label className="text-sm font-medium text-slate-700">
                Nombre
                <input
                  value={form.first_name}
                  onChange={(event) => setForm((current) => ({ ...current, first_name: event.target.value }))}
                  className={inputClass}
                />
              </label>
              <label className="text-sm font-medium text-slate-700">
                Apellido
                <input
                  value={form.last_name}
                  onChange={(event) => setForm((current) => ({ ...current, last_name: event.target.value }))}
                  className={inputClass}
                />
              </label>
              <label className="text-sm font-medium text-slate-700 sm:col-span-2">
                Teléfono
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
                  className={inputClass}
                />
              </label>
              <div className="flex flex-wrap gap-3 sm:col-span-2">
                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60"
                >
                  {saving ? "Guardando..." : editingUser ? "Guardar cambios" : "Crear y enviar invitación"}
                </button>
                <button type="button" onClick={cancelEdit} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                  Cancelar
                </button>
              </div>
            </form>
          </section>
        )}

        {deactivatingUser && (
          <section aria-labelledby="deactivation-title" className="mb-8 rounded-xl border border-amber-300 bg-amber-50 p-5">
            <h2 id="deactivation-title" className="font-semibold text-slate-900">
              Desactivar a {deactivatingUser.first_name || deactivatingUser.email}
            </h2>
            <p className="mt-1 text-sm text-slate-700">
              No se eliminará la cuenta. Las propiedades asignadas al asesor quedarán sin responsable.
            </p>
            <form onSubmit={deactivateUser} className="mt-4">
              <label className="block text-sm font-medium text-slate-700">
                Motivo (obligatorio)
                <textarea
                  required
                  minLength={1}
                  maxLength={2000}
                  value={deactivationReason}
                  onChange={(event) => setDeactivationReason(event.target.value)}
                  className={inputClass}
                  rows={3}
                />
              </label>
              <div className="mt-3 flex gap-3">
                <button type="submit" disabled={saving} className="rounded-lg bg-red-700 px-4 py-2 text-sm font-semibold text-white hover:bg-red-800 disabled:opacity-60">
                  {saving ? "Procesando..." : "Confirmar desactivación"}
                </button>
                <button type="button" onClick={() => setDeactivatingUser(null)} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700">
                  Cancelar
                </button>
              </div>
            </form>
          </section>
        )}

        <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="border-b border-slate-200 px-5 py-4">
            <h2 className="font-semibold text-slate-900">Cuentas registradas</h2>
            <p className="mt-1 text-sm text-slate-600">{users.length} usuario(s)</p>
          </div>
          {loading ? (
            <p className="p-6 text-sm text-slate-600">Cargando usuarios...</p>
          ) : users.length === 0 ? (
            <p className="p-6 text-sm text-slate-600">No hay usuarios registrados.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th scope="col" className="px-5 py-3">Usuario</th>
                    <th scope="col" className="px-5 py-3">Rol</th>
                    <th scope="col" className="px-5 py-3">Estado</th>
                    <th scope="col" className="px-5 py-3">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-5 py-4">
                        <p className="font-medium text-slate-900">
                          {[user.first_name, user.last_name].filter(Boolean).join(" ") || user.username || user.email}
                        </p>
                        <p className="text-slate-600">{user.email}</p>
                        {user.deactivation_reason && !user.is_active && (
                          <p className="mt-1 max-w-xs text-xs text-slate-500">Motivo: {user.deactivation_reason}</p>
                        )}
                      </td>
                      <td className="px-5 py-4 capitalize text-slate-700">
                        {user.role === "admin" ? "Administrador" : "Asesor"}
                      </td>
                      <td className="px-5 py-4">
                        <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${user.is_active ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-700"}`}>
                          {user.is_active
                            ? "Activo"
                            : user.deactivation_reason
                              ? "Desactivado"
                              : "Pendiente de activación"}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <div className="flex flex-wrap gap-x-3 gap-y-2">
                          <button type="button" onClick={() => startEdit(user)} className="font-semibold text-blue-700 hover:underline">
                            Editar
                          </button>
                          {!user.is_active && !user.deactivation_reason && (
                            <button type="button" disabled={saving} onClick={() => void resendActivation(user)} className="font-semibold text-blue-700 hover:underline disabled:opacity-50">
                              Reenviar activación
                            </button>
                          )}
                          {user.is_active && (
                            <button type="button" onClick={() => { setError(""); setDeactivationReason(""); setDeactivatingUser(user); }} className="font-semibold text-red-700 hover:underline">
                              Desactivar
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}
