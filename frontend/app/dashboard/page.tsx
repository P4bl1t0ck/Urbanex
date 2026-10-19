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
  // Agregamos estos campos al tipo para poder leerlos al editar
  description?: string;
  property_type?: string;
  area_m2?: string | number;
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

  //Estado para saber si estabamos editando (guarda el ID) o si esta creadno es null.
  const [editingId, setEditingId] = useState<number | null>(null);

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

  const [selectedImages, setSelectedImages] = useState<File[]>([]);

  useEffect(() => {
    const token = sessionStorage.getItem("access");
    //const token = localStorage.getItem("access");

    if (!token) {
      router.replace("/login");
      return;
    }

    const controller = new AbortController();
    let isActive = true;
    const timeoutId = window.setTimeout(() => controller.abort(), 10000);
    //Timeof if the page detects there´s no any type of activity.

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

  function openEditModal(property: Property) {
    setEditingId(property.id);
    setFormData({
      title: property.title,  
      description: property.description || "",
      property_type: property.property_type || "departamento",
      price: property.price.toString(),
      area_m2 : property.area_m2 ? property.area_m2.toString() : "",
      location: property.location,
      bedrooms: 1, 
      bathrooms: 1,
      parking_spaces: 0,
    });
    setSelectedImages([]);
    setShowModal(true);
  }

  function openCreateModal(){
    setEditingId(null);
    setFormData({
      title: "", description: "", property_type: "departamento",
      price: "", area_m2: "", location: "", bedrooms: 1, bathrooms: 1, parking_spaces: 0,

    });
    setSelectedImages([]);
    setShowModal(true);
  }

  //Esta funcion es inteligente, decide s i hace POST o Patch ante una propiedad.
  async function handleSaveProperty(e: React.FormEvent){
    e.preventDefault();
    const token = sessionStorage.getItem("access");

    // Lógica dinámica: PATCH para actualizar, POST para crear
    const url = editingId 
      ? `http://127.0.0.1:8000/api/auth/properties/${editingId}/` 
      : "http://127.0.0.1:8000/api/auth/properties/";
    
    const method = editingId ? "PATCH" : "POST";
    
     try {
      const responseProp = await fetch(url, {
        method: method,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      if (!responseProp.ok) {
        // Leemos el chisme exacto de Django
        const errorDetails = await responseProp.json();
        console.error( "Django rechazó la solicitud:", errorDetails);
        alert(`Error desde el servidor: ${JSON.stringify(errorDetails)}`);
        return; // Detenemos la ejecución aquí
      }
      
      const savedProperty: Property = await responseProp.json();

      // Subida de imágenes (Solo útil si estamos creando o agregando nuevas)
      if (selectedImages.length > 0) {
        for (const file of selectedImages) {
          const imageFormData = new FormData();
          imageFormData.append("property", savedProperty.id.toString());
          imageFormData.append("image", file);

          await fetch("http://127.0.0.1:8000/api/auth/property-images/", {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: imageFormData,
          });
        }
      }

      // Actualizar la tabla visualmente sin recargar
      if (editingId) {
        // Modo edición: Reemplaza la propiedad modificada en la lista
        setProperties(prev => prev.map(p => p.id === editingId ? savedProperty : p));
        alert("¡Propiedad actualizada con éxito!");
      } else {
        // Modo creación: Agrega la nueva propiedad al inicio de la lista
        setProperties(prev => [savedProperty, ...prev]);
        alert("¡Propiedad registrada con éxito!");
      }
      
      setShowModal(false);
    } catch (err) {
      alert("Error al procesar la solicitud. Verifica los datos.");
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setSelectedImages(Array.from(e.target.files));
  }

  async function handlePublish(propertyId: number) {
    //const token = localStorage.getItem("access");
    const token = sessionStorage.getItem("access");

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
    /**
     localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    router.replace("/login");
     */
    sessionStorage.removeItem("access");
    sessionStorage.removeItem("refresh");
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
               <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Urbanex</p>
               <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Mis propiedades</h1>
               <p className="mt-2 text-slate-600">Consulta y administra las propiedades asociadas a tu cuenta.</p>
             </div>
             
             <div className="flex items-center gap-3">
               <button onClick={openCreateModal} className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800">
                 + Registrar propiedad
               </button>
               <button onClick={handleLogout} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100">
                 Cerrar sesión
               </button>
             </div>
           </header>
 
           {error ? (
             <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-800">{error}</div>
           ) : properties.length === 0 ? (
             <div className="rounded-xl border border-slate-200 bg-white p-8 text-center shadow-sm">
               <p className="font-medium text-slate-800">Aún no tienes propiedades registradas.</p>
             </div>
           ) : (
             <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
               <div className="overflow-x-auto">
                 <table className="min-w-full divide-y divide-slate-200 text-left">
                   <thead className="bg-slate-100">
                     <tr>
                       <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Título</th>
                       <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Ubicación</th>
                       <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Precio</th>
                       <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Estado</th>
                       <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Acción</th>
                     </tr>
                   </thead>
                   <tbody className="divide-y divide-slate-100">
                     {properties.map((property) => (
                       <tr key={property.id} className="hover:bg-slate-50">
                         <td className="whitespace-nowrap px-6 py-4 font-medium text-slate-900">{property.title}</td>
                         <td className="px-6 py-4 text-slate-600">{property.location}</td>
                         <td className="whitespace-nowrap px-6 py-4 text-slate-700">
                           {Number(property.price).toLocaleString("es-EC", { style: "currency", currency: "USD" })}
                         </td>
                         <td className="whitespace-nowrap px-6 py-4">
                           <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                             {STATUS_LABELS[property.status] ?? property.status.replace("_", " ")}
                           </span>
                         </td>
                         <td className="whitespace-nowrap px-6 py-4 flex gap-2">
                           <button
                             type="button"
                             onClick={() => openEditModal(property)}
                             className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
                           >
                             Editar
                           </button>
                           {property.status !== "disponible" && (
                             <button
                               type="button"
                               onClick={() => handlePublish(property.id)}
                               className="rounded-lg bg-blue-700 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-800"
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
 
       {showModal && (
         <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm">
           <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white p-6 shadow-xl border border-slate-200">
             <h2 className="text-xl font-bold text-slate-900 mb-4">
               {editingId ? "Editar Propiedad" : "Registrar Nueva Propiedad"}
             </h2>
             <form onSubmit={handleSaveProperty} className="space-y-4">
               <div>
                 <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Título</label>
                 <input type="text" required value={formData.title} onChange={(e) => setFormData({ ...formData, title: e.target.value })} className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none" />
               </div>
 
               <div className="grid grid-cols-2 gap-4">
                 <div>
                   <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Tipo</label>
                   <select value={formData.property_type} onChange={(e) => setFormData({ ...formData, property_type: e.target.value })} className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none">
                     <option value="departamento">Departamento</option>
                     <option value="casa">Casa</option>
                     <option value="terreno">Terreno</option>
                     <option value="oficina">Oficina</option>
                   </select>
                 </div>
                 <div>
                   <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Precio (\$)</label>
                   <input type="number" required value={formData.price} onChange={(e) => setFormData({ ...formData, price: e.target.value })} className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none" />
                 </div>
               </div>
 
               <div className="grid grid-cols-2 gap-4">
                 <div>
                   <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Área (m²)</label>
                   <input type="number" required value={formData.area_m2} onChange={(e) => setFormData({ ...formData, area_m2: e.target.value })} className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none" />
                 </div>
                 <div>
                   <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Ubicación</label>
                   <input type="text" required value={formData.location} onChange={(e) => setFormData({ ...formData, location: e.target.value })} className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none" />
                 </div>
               </div>
 
               <div>
                 <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Descripción</label>
                 <textarea required value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })} className="w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none" rows={3} />
               </div>
 
               <div>
                 <label className="block text-xs font-semibold uppercase text-slate-700 mb-1">Imágenes</label>
                 <input type="file" multiple accept="image/*" onChange={handleImageChange} className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
               </div>
 
               <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
                 <button type="button" onClick={() => setShowModal(false)} className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">Cancelar</button>
                 <button type="submit" className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800">Guardar</button>
               </div>
             </form>
           </div>
         </div>
       )}
     </>
   );
 }