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
  reservador: "Reservado",
  vendido: "Vendido",
  arrendado: "Arrendado",
  no_disponible: "No disponible",
};

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

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
      // Llamamos a la vista PropertyPublishView que ya creaste en tu views.py
      const response = await fetch(`http://127.0.0.1:8000/api/auth/properties/${propertyId}/publish/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json"
        },
      });
      //Copi Can u tell how i can test this?
      // Puedes probar esta función haciendo clic en el botón "Publicar" en la tabla de propiedades. Asegúrate de que la propiedad tenga un estado que permita la publicación (por ejemplo, "captacion"). Al hacer clic, se enviará una solicitud POST a la API para cambiar el estado de la propiedad a "disponible". Si la solicitud es exitosa, verás una alerta confirmando que la propiedad se publicó correctamente y la tabla se actualizará en tiempo real. Si hay un error, se mostrará un mensaje de error correspondiente.
      //Ya le pruebo, gracias Copi
      // Si la respuesta es exitosa, actualizamos el estado de la propiedad en la tabla
      //Ya te digo que salga. Mhh oye se que suena mal, pero cuando me escribes por aqui se gastan tokens?
      // Sí, cada vez que interactúas conmigo, se consumen tokens. Los tokens son unidades de medida que representan la cantidad de texto procesado. Cada mensaje que envías y cada respuesta que recibes consume tokens, así que es bueno ser consciente de eso si estás usando un plan con límite de tokens.
      //Claro. 
      if (response.ok) {
        // Actualizamos la tabla en tiempo real sin recargar la página
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
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100"
          >
            Cerrar sesión
          </button>
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
                        <button
                          type="button"
                          onClick={() => handlePublish(property.id)}
                          className="rounded-lg bg-blue-700 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                        >
                          Publicar
                        </button>
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
    </>
  );
}
