"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import SiteNav from "@/components/SiteNav";

type Property = {
  id: number;
  title: string;
  location: string;
  price: string | number;
  status: string;
};

const STATUS_LABELS: Record<string, string> = {
  captacion: "En captación",
  disponible: "Disponible",
  reservado: "Reservado",
  vendido: "Vendido",
  arrendado: "Arrendado",
  no_disponible: "No disponible",
};

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const router = useRouter();

  // Estado del formulario para nueva propiedad
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    property_type: "departamento",
    price: "",
    area_m2: "",
    location: "",
    bedrooms: 1,
    bathrooms: 1,
    parking_spaces: 0,
  });

  useEffect(() => {
    const token = localStorage.getItem("access");

    if (!token) {
      router.replace("/login");
      return;
    }

    const controller = new AbortController();
    let isActive = true;
    const timeoutId = window.setTimeout(() => controller.abort(), 10000);

    async function loadProperties() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/auth/properties/mine/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
            cache: "no-store",
            signal: controller.signal,
          },
        );

        if (!response.ok) {
          throw new Error(
            response.status === 401
              ? "La sesión venció. Inicia sesión nuevamente."
              : `No se pudieron cargar tus propiedades (error ${response.status}).`,
          );
        }

        const data: Property[] = await response.json();
        setProperties(data);
      } catch (fetchError) {
        if (!isActive) {
          return;
        }

        if (fetchError instanceof Error && fetchError.name === "AbortError") {
          setError(
            "La API tardó demasiado en responder. Verifica que Django esté activo e intenta de nuevo.",
          );
          return;
        }

        setError(
          fetchError instanceof Error
            ? fetchError.message
            : "Ocurrió un error al cargar tus propiedades.",
        );
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    }

    void loadProperties();

    return () => {
      isActive = false;
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [router]);

  async function handlePublish(propertyId: number) {
    const token = localStorage.getItem("access");

    if (!confirm("¿Estás seguro de publicar esta propiedad en el catálogo?")) return;

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/auth/properties/${propertyId}/publish/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
      });

      if (response.ok) {
        setProperties(prevProps =>
          prevProps.map(prop =>
            prop.id === propertyId ? { ...prop, status: "disponible" } : prop
          )
        );
        alert("¡Propiedad publicada con éxito!");
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || "No se pudo publicar."}`);
      }
    } catch (error) {
      console.error("Error al publicar:", error);
      alert("Error de conexión con el servidor.");
    }
  }

  async function handleCreateProperty(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem("access");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/properties/", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("No se pudo crear la propiedad");
      }

      const newProperty: Property = await response.json();
      setProperties((prev) => [newProperty, ...prev]);
      setShowModal(false);
      alert("¡Propiedad registrada en estado de captación!");

      // Limpiar formulario
      setFormData({
        title: "",
        description: "",
        property_type: "departamento",
        price: "",
        area_m2: "",
        location: "",
        bedrooms: 1,
        bathrooms: 1,
        parking_spaces: 0,
      });
    } catch (err) {
      alert("Error al registrar la propiedad. Revisa que los campos estén completos.");
    }
  }

  function handleLogout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    router.replace("/login");
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 px-4 py-12">
        <p className="mx-auto max-w-6xl animate-pulse text-slate-600">
          Cargando tus propiedades...
        </p>
      </main>
    );
  }

  return (
    <>
      <SiteNav />
      <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">
                Urbanex
              </p>
              <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
                Mis propiedades
              </h1>
              <p className="mt-2 text-slate-600">
                Consulta y administra las propiedades asociadas a tu cuenta.
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setShowModal(true)}
                className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800"
              >
                + Registrar propiedad
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100"
              >
                Cerrar sesión
              </button>
            </div>
          </header>

          {error ? (
            <div
              role="alert"
              className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800"
            >
              {error}
            </div>
          ) : properties.length === 0 ? (
            <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
              <p className="font-medium text-slate-800">
                Aún no tienes propiedades registradas.
              </p>
            </div>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-left">
                  <thead className="bg-slate-100">
                    <tr>
                      <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">
                        Título
                      </th>
                      <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">
                        Ubicación
                      </th>
                      <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">
                        Precio
                      </th>
                      <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">
                        Estado
                      </th>
                      <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">
                        Acción
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {properties.map((property) => (
                      <tr key={property.id} className="hover:bg-slate-50">
                        <td className="whitespace-nowrap px-6 py-4 font-medium text-slate-900">
                          {property.title}
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {property.location}
                        </td>
                        <td className="whitespace-nowrap px-6 py-4 text-slate-700">
                          {Number(property.price).toLocaleString("es-EC", {
                            style: "currency",
                            currency: "USD",
                          })}
                        </td>
                        <td className="whitespace-nowrap px-6 py-4">
                          <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                            {STATUS_LABELS[property.status] ??
                              property.status.replace("_", " ")}
                          </span>
                        </td>
                        <td className="whitespace-nowrap px-6 py-4">
                          {property.status !== "disponible" && (
                            <button
                              type="button"
                              onClick={() => handlePublish(property.id)}
                              className="rounded-lg bg-blue-700 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            >
                              Publicar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Modal para Registrar Nueva Propiedad */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white p-6 shadow-xl border border-slate-200">
            <h2 className="text-xl font-bold text-slate-900 mb-4">
              Registrar Nueva Propiedad
            </h2>
            <form onSubmit={handleCreateProperty} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
                  Título
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                  placeholder="Ej. Casa de tres pisos en Cumbayá"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
                    Tipo
                  </label>
                  <select
                    value={formData.property_type}
                    onChange={(e) => setFormData({ ...formData, property_type: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                  >
                    <option value="departamento">Departamento</option>
                    <option value="casa">Casa</option>
                    <option value="terreno">Terreno</option>
                    <option value="oficina">Oficina</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
                    Precio (\$)
                  </label>
                  <input
                    type="number"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                    placeholder="120000"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
                    Área (m²)
                  </label>
                  <input
                    type="number"
                    required
                    value={formData.area_m2}
                    onChange={(e) => setFormData({ ...formData, area_m2: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                    placeholder="85"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
                    Ubicación
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                    placeholder="Sector / Ciudad"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">
                  Descripción
                </label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none"
                  rows={3}
                  placeholder="Detalles principales de la propiedad..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800"
                >
                  Guardar Propiedad
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}