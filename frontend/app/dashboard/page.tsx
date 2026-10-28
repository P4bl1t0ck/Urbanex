"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import Dialog from "@/components/Dialog";
import type { LatLng } from "@/components/MapPicker";
import { ApiError, authFetch } from "@/lib/api";
import type {
  Appraisal,
  MissingRequirement,
  PublicationRequirementsResponse,
  PublishErrorResponse,
} from "@/types/appraisal";
import type { Property, PropertyImage } from "@/types/property";

//Importamos el mapa desactivando el SSR
const MapPicker = dynamic(() => import("@/components/MapPicker"),{
  ssr: false,
  loading: () => <div className="h-[320px] w-full animate-pulse bg-slate-200 rounded-lg">Cargando Mapa. Por favor espere...</div>
})

type PropertyForm = {
  title: string;
  description: string;
  property_type: string;
  price: string;
  area_m2: string;
  location: string; //Conservamos esto como direccion en texto (Nayon quito por ejemplo.)
  latitude: number;
  longitude: number;
  bedrooms: number;
  bathrooms: number;
  parking_spaces: number;
};

type StagedImage = { file: File; preview: string };

type StagedDocument = {
  key: string;
  doc_type: string;
  issue_date: string;
  expiration_date: string;
  is_critical: boolean;
  file: File;
};

// Respuesta de GET /api/documents/ (apps.documents.serializers.DocumentSerializer)
type SavedDocument = {
  id: string;
  doc_type: string;
  doc_type_display: string;
  is_critical: boolean;
  original_filename: string;
  file_size_bytes: number;
  version: number;
  expiration_date: string;
  is_expired: boolean;
  is_expiring_soon: boolean;
  validation_status: string;
  validation_status_display: string;
};

type TabId = "general" | "location" | "media" | "docs";

// Estado del requisito "Avalúo aprobado" en la pestaña Expediente (HU-53).
type AppraisalRequirement = "loading" | "approved" | "draft" | "none" | "error";

// Requisitos de publicación según el servidor (DS-15), mostrados en la pestaña Expediente.
type RequirementsState =
  | { kind: "loading" }
  | { kind: "ready"; data: PublicationRequirementsResponse }
  | { kind: "error" };

// Aviso sobre la tabla tras guardar o publicar (reemplaza los alert nativos, DS-15).
type Notice = { kind: "success" | "warning"; title: string; lines: string[] };

// Rechazo al publicar: se explica en un modal con enlaces a lo que falta (HU-53).
type PublishProblem = { property: Property; detail: string; missing: MissingRequirement[] };

const REQUIREMENT_TABS: Partial<Record<MissingRequirement["code"], { tab: TabId; label: string }>> = {
  image: { tab: "media", label: "Abrir Multimedia" },
  brokerage_contract: { tab: "docs", label: "Abrir Expediente" },
};

// Convierte el cuerpo de error de DRF ({campo: [mensajes]}) en líneas legibles.
function drfErrorLines(body: unknown): string[] {
  if (!body || typeof body !== "object") return [];
  return Object.entries(body as Record<string, unknown>).map(([field, value]) => {
    const text = Array.isArray(value) ? value.join(" ") : String(value);
    return field === "detail" || field === "non_field_errors" ? text : `${field}: ${text}`;
  });
}

const STATUS_LABELS: Record<string, string> = {
  captacion: "En captación",
  disponible: "Disponible",
  reservador: "Reservado", // Valor real en Django (errata DT-16, DT-47)
  vendido: "Vendido",
  arrendado: "Arrendado",
  no_disponible: "No disponible",
};

// Deben coincidir con Property.PROPERTY_TYPES en Django
const PROPERTY_TYPES = [
  { value: "departamento", label: "Departamento" },
  { value: "casa", label: "Casa" },
  { value: "local", label: "Local comercial" },
  { value: "terreno", label: "Terreno" },
];

// Deben coincidir con Document.DocType en apps.documents
const DOC_TYPES: Record<string, string> = {
  CORRETAJE: "Contrato de corretaje",
  CEDULA_CATASTRAL: "Cédula catastral",
  ESCRITURA: "Escrituras",
  GRAVAMENES: "Certificado de gravámenes",
  PREDIAL: "Comprobante predial / tributario",
  CERT_LABORAL: "Certificado laboral",
  CERT_BANCARIO: "Certificado bancario",
  OTRO: "Otro",
};
const DOCUMENTS_URL = "http://127.0.0.1:8000/api/documents/";
const DOC_ACCEPT = "application/pdf,image/jpeg,image/png,image/webp";
const MAX_DOC_BYTES = 20 * 1024 * 1024; // RF-10

const TABS: { id: TabId; label: string; hint: string }[] = [
  { id: "general", label: "Datos generales", hint: "Tipo, precio y características" },
  { id: "location", label: "Ubicación", hint: "Dirección y punto en el mapa" },
  { id: "media", label: "Multimedia", hint: "Fotografías del inmueble" },
  { id: "docs", label: "Expediente", hint: "Documentación inicial" },
];

const DEFAULT_COORDS: LatLng = { lat: -0.180653, lng: -78.467834 };

const EMPTY_FORM: PropertyForm = {
  title: "",
  description: "",
  property_type: "departamento",
  price: "",
  area_m2: "",
  location: "",
  latitude: DEFAULT_COORDS.lat,
  longitude: DEFAULT_COORDS.lng,
  bedrooms: 1,
  bathrooms: 1,
  parking_spaces: 0,
};

const EMPTY_DOC_DRAFT = { doc_type: "CORRETAJE", issue_date: "", expiration_date: "", is_critical: true };

const inputClass =
  "w-full rounded-lg border border-slate-300 p-2.5 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100";

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="block text-xs font-semibold uppercase text-slate-700 mb-1">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-xs text-slate-500">{hint}</span>}
    </label>
  );
}

function formatBytes(bytes: number) {
  return bytes >= 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${Math.ceil(bytes / 1024)} KB`;
}

// Validación por viñeta: solo se monta la viñeta activa, así que el "required" de HTML
// no alcanza a las demás. Cada error indica en qué viñeta corregirlo.
function validateForm(form: PropertyForm, imageCount: number): Partial<Record<TabId, string[]>> {
  const errors: Partial<Record<TabId, string[]>> = {};
  const add = (tab: TabId, message: string) => (errors[tab] ??= []).push(message);

  if (!form.title.trim()) add("general", "El título es obligatorio.");
  if (!(Number(form.price) > 0)) add("general", "El precio referencial debe ser mayor a 0.");
  if (!(Number(form.area_m2) > 0)) add("general", "El área debe ser mayor a 0 m².");
  if (!form.description.trim()) add("general", "La descripción es obligatoria.");
  if ([form.bedrooms, form.bathrooms, form.parking_spaces].some((n) => n < 0 || !Number.isInteger(n)))
    add("general", "Habitaciones, baños y parqueaderos deben ser enteros positivos.");

  if (!form.location.trim()) add("location", "La dirección referencial es obligatoria.");

  if (imageCount < 1) add("media", "Se requiere al menos 1 fotografía (RF-01).");

  return errors;
}

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const router = useRouter();

  const [userInfo, setUserInfo] = useState({ email: "", role: "" });

  //Estado para saber si estabamos editando (guarda el ID) o si esta creadno es null.
  const [editingId, setEditingId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("general");
  const [formErrors, setFormErrors] = useState<Partial<Record<TabId, string[]>>>({});
  const [saving, setSaving] = useState(false);

  // Estado del formulario para nueva propiedad
  const [formData, setFormData] = useState<PropertyForm>(EMPTY_FORM);
  const [existingImages, setExistingImages] = useState<PropertyImage[]>([]);
  const [selectedImages, setSelectedImages] = useState<StagedImage[]>([]);

  // Expediente (HU-03): los documentos se preparan aquí y se suben al guardar la propiedad.
  const [savedDocs, setSavedDocs] = useState<SavedDocument[]>([]);
  const [savedDocsError, setSavedDocsError] = useState("");
  const [stagedDocs, setStagedDocs] = useState<StagedDocument[]>([]);
  const [docDraft, setDocDraft] = useState(EMPTY_DOC_DRAFT);
  const [docFile, setDocFile] = useState<File | null>(null);
  const [docError, setDocError] = useState("");
  const [docInputKey, setDocInputKey] = useState(0); // Para limpiar el <input type="file">

  // Avalúo (HU-08): solo se consulta al editar; el avalúo se gestiona en su propia pantalla (I-12).
  const [appraisalRequirement, setAppraisalRequirement] = useState<AppraisalRequirement | null>(null);
  const [requirements, setRequirements] = useState<RequirementsState | null>(null);
  const [saveErrors, setSaveErrors] = useState<string[]>([]);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [publishCandidate, setPublishCandidate] = useState<Property | null>(null);
  const [publishProblem, setPublishProblem] = useState<PublishProblem | null>(null);
  const [publishingId, setPublishingId] = useState<number | null>(null);

  useEffect(() => {
    const token = sessionStorage.getItem("access");
    // NUEVO: Leer quién soy desde la memoria de la pestaña
    const userEmail = sessionStorage.getItem("userEmail") || "Usuario";
    const userRole = sessionStorage.getItem("userRole") || "Asesor";
    setUserInfo({ email: userEmail, role: userRole });

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

  function updateField<K extends keyof PropertyForm>(key: K, value: PropertyForm[K]) {
    setFormData((prev) => ({ ...prev, [key]: value }));
  }

  function resetModalState(form: PropertyForm, images: PropertyImage[], tab: TabId = "general") {
    selectedImages.forEach((img) => URL.revokeObjectURL(img.preview));
    setFormData(form);
    setExistingImages(images);
    setSelectedImages([]);
    setSavedDocs([]);
    setSavedDocsError("");
    setStagedDocs([]);
    setDocDraft(EMPTY_DOC_DRAFT);
    setDocFile(null);
    setDocError("");
    setAppraisalRequirement(null);
    setRequirements(null);
    setSaveErrors([]);
    setFormErrors({});
    setActiveTab(tab);
    setShowModal(true);
  }

  function openEditModal(property: Property, tab: TabId = "general") {
    setEditingId(property.id);
    resetModalState(
      {
        title: property.title,
        description: property.description || "",
        property_type: property.property_type || "departamento",
        price: property.price.toString(),
        area_m2: property.area_m2 ? property.area_m2.toString() : "",
        location: property.location,
        // Leemos los valores guardados para que no se pierdan al editar.
        latitude: property.latitude != null ? Number(property.latitude) : DEFAULT_COORDS.lat,
        longitude: property.longitude != null ? Number(property.longitude) : DEFAULT_COORDS.lng,
        bedrooms: property.bedrooms ?? 0,
        bathrooms: property.bathrooms ?? 0,
        parking_spaces: property.parking_spaces ?? 0,
      },
      property.images ?? [],
      tab,
    );
    void loadSavedDocuments(property.id);
    void loadAppraisalRequirement(property.id);
    void loadPublicationRequirements(property.id);
  }

  // DS-15: el Expediente muestra lo mismo que respondería el 400 de publicar.
  async function loadPublicationRequirements(propertyId: number) {
    setRequirements({ kind: "loading" });
    try {
      const data = await authFetch<PublicationRequirementsResponse>(
        `/api/auth/properties/${propertyId}/publication-requirements/`,
      );
      setRequirements({ kind: "ready", data });
    } catch {
      setRequirements({ kind: "error" });
    }
  }

  async function loadAppraisalRequirement(propertyId: number) {
    setAppraisalRequirement("loading");
    try {
      const appraisals = await authFetch<Appraisal[]>(`/api/appraisals/?property=${propertyId}`);
      setAppraisalRequirement(
        appraisals.some((a) => a.status === "APROBADO")
          ? "approved"
          : appraisals.some((a) => a.status === "BORRADOR")
            ? "draft"
            : "none",
      );
    } catch {
      setAppraisalRequirement("error");
    }
  }

  async function loadSavedDocuments(propertyId: number) {
    const token = sessionStorage.getItem("access");
    try {
      const response = await fetch(`${DOCUMENTS_URL}?property=${propertyId}`, {
        headers: { Authorization: `Bearer ${token}` },
        cache: "no-store",
      });
      if (!response.ok) throw new Error(`error ${response.status}`);
      setSavedDocs(await response.json());
    } catch {
      setSavedDocsError("No se pudo cargar el expediente guardado de esta propiedad.");
    }
  }

  // Sube cada documento preparado; devuelve los mensajes de los que el servidor rechazó.
  async function uploadStagedDocuments(propertyId: number, token: string | null) {
    const failures: string[] = [];
    for (const doc of stagedDocs) {
      const docFormData = new FormData();
      docFormData.append("property", propertyId.toString());
      docFormData.append("doc_type", doc.doc_type);
      docFormData.append("file", doc.file);
      docFormData.append("issue_date", doc.issue_date);
      docFormData.append("expiration_date", doc.expiration_date);
      docFormData.append("is_critical", String(doc.is_critical));

      try {
        const response = await fetch(DOCUMENTS_URL, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: docFormData,
        });
        if (!response.ok) {
          const details = await response.json().catch(() => ({}));
          failures.push(`${DOC_TYPES[doc.doc_type]} (${doc.file.name}): ${Object.values(details).flat().join(" ") || `error ${response.status}`}`);
        }
      } catch {
        failures.push(`${DOC_TYPES[doc.doc_type]} (${doc.file.name}): sin conexión con el servidor`);
      }
    }
    return failures;
  }

  function openCreateModal(){
    setEditingId(null);
    resetModalState(EMPTY_FORM, []);
  }

  function closeModal() {
    selectedImages.forEach((img) => URL.revokeObjectURL(img.preview));
    setSelectedImages([]);
    setShowModal(false);
  }

  //Esta funcion es inteligente, decide s i hace POST o Patch ante una propiedad.
  async function handleSaveProperty(e: React.FormEvent){
    e.preventDefault();
    if (saving) return;

    const errors = validateForm(formData, existingImages.length + selectedImages.length);
    setFormErrors(errors);
    const firstTabWithErrors = TABS.find((tab) => errors[tab.id]?.length);
    if (firstTabWithErrors) {
      setActiveTab(firstTabWithErrors.id);
      return;
    }

    const token = sessionStorage.getItem("access");

    // Lógica dinámica: PATCH para actualizar, POST para crear
    const url = editingId
      ? `http://127.0.0.1:8000/api/auth/properties/${editingId}/`
      : "http://127.0.0.1:8000/api/auth/properties/";

    const method = editingId ? "PATCH" : "POST";

    // Django guarda 6 decimales; Leaflet entrega más y DRF rechazaría el valor.
    const payload = {
      ...formData,
      latitude: Number(formData.latitude.toFixed(6)),
      longitude: Number(formData.longitude.toFixed(6)),
    };

    setSaving(true);
    setSaveErrors([]);
    try {
      const responseProp = await fetch(url, {
        method: method,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!responseProp.ok) {
        // El modal sigue abierto con los datos y muestra los errores de Django por campo.
        const errorDetails = await responseProp.json().catch(() => null);
        const lines = drfErrorLines(errorDetails);
        setSaveErrors(lines.length ? lines : [`El servidor rechazó los datos (error ${responseProp.status}).`]);
        return;
      }

      let savedProperty: Property = await responseProp.json();

      // Subida de imágenes nuevas
      const uploadedImages: PropertyImage[] = [];
      for (const { file } of selectedImages) {
        const imageFormData = new FormData();
        imageFormData.append("property", savedProperty.id.toString());
        imageFormData.append("image", file);

        const imageResponse = await fetch("http://127.0.0.1:8000/api/auth/property-images/", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: imageFormData,
        });
        if (imageResponse.ok) uploadedImages.push(await imageResponse.json());
      }
      savedProperty = { ...savedProperty, images: [...(savedProperty.images ?? []), ...uploadedImages] };

      // Actualizar la tabla visualmente sin recargar
      if (editingId) {
        // Modo edición: Reemplaza la propiedad modificada en la lista
        setProperties(prev => prev.map(p => p.id === editingId ? savedProperty : p));
      } else {
        // Modo creación: Agrega la nueva propiedad al inicio de la lista
        setProperties(prev => [savedProperty, ...prev]);
      }

      const failedDocs = await uploadStagedDocuments(savedProperty.id, token);
      const failedImages = selectedImages.length - uploadedImages.length;
      // Nunca simular éxito: el aviso detalla lo que el servidor no aceptó.
      const lines: string[] = [];
      if (failedImages > 0) lines.push(`${failedImages} imagen(es) no se pudieron subir.`);
      if (stagedDocs.length > failedDocs.length)
        lines.push(`${stagedDocs.length - failedDocs.length} documento(s) agregados al expediente.`);
      failedDocs.forEach((failure) => lines.push(`Documento rechazado: ${failure}`));
      setNotice({
        kind: failedImages > 0 || failedDocs.length > 0 ? "warning" : "success",
        title: editingId
          ? `"${savedProperty.title}" se actualizó.`
          : `"${savedProperty.title}" se registró en captación.`,
        lines,
      });

      closeModal();
    } catch {
      setSaveErrors(["No se pudo conectar con el servidor. Tus datos siguen en el formulario; intenta de nuevo."]);
    } finally {
      setSaving(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files ?? []).filter((file) => file.type.startsWith("image/"));
    setSelectedImages((prev) => [...prev, ...files.map((file) => ({ file, preview: URL.createObjectURL(file) }))]);
    e.target.value = ""; // Permite volver a elegir el mismo archivo
  }

  function removeSelectedImage(index: number) {
    setSelectedImages((prev) => {
      URL.revokeObjectURL(prev[index].preview);
      return prev.filter((_, i) => i !== index);
    });
  }

  function handleAddDocument() {
    if (!docFile) return setDocError("Selecciona un archivo.");
    if (!DOC_ACCEPT.split(",").includes(docFile.type)) return setDocError("Solo se admiten PDF o imágenes (JPG, PNG, WEBP).");
    if (docFile.size > MAX_DOC_BYTES) return setDocError("El archivo supera el máximo de 20 MB.");
    if (!docDraft.issue_date || !docDraft.expiration_date) return setDocError("Indica la fecha de emisión y la de vigencia.");
    if (docDraft.expiration_date < docDraft.issue_date) return setDocError("La vigencia no puede ser anterior a la emisión.");

    setStagedDocs((prev) => [...prev, { ...docDraft, file: docFile, key: crypto.randomUUID() }]);
    setDocDraft(EMPTY_DOC_DRAFT);
    setDocFile(null);
    setDocError("");
    setDocInputKey((k) => k + 1);
  }

  // HU-53: el servidor decide si se puede publicar. Un 400 trae la lista de requisitos
  // faltantes (missing_requirements) y un 409 indica que la propiedad no está en captación.
  async function handlePublish(property: Property) {
    setPublishingId(property.id);
    setNotice(null);
    try {
      await authFetch(`/api/auth/properties/${property.id}/publish/`, { method: "POST" });
      setProperties((prevProps) =>
        prevProps.map((prop) => (prop.id === property.id ? { ...prop, status: "disponible" } : prop)),
      );
      setNotice({ kind: "success", title: `"${property.title}" se publicó y ya está disponible en el catálogo.`, lines: [] });
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        router.replace("/login");
        return;
      }
      const body = error instanceof ApiError ? (error.body as Partial<PublishErrorResponse> | null) : null;
      setPublishProblem({
        property,
        detail:
          error instanceof ApiError
            ? body?.missing_requirements?.length
              ? "Para publicarla en el catálogo todavía falta:"
              : error.message
            : "No se pudo conectar con el servidor. Intenta de nuevo.",
        missing: body?.missing_requirements ?? [],
      });
    } finally {
      setPublishingId(null);
      setPublishCandidate(null);
    }
  }

  // Desde el modal de requisitos, abre la ficha en la pestaña donde se corrige lo que falta.
  function fixRequirement(property: Property, tab: TabId) {
    setPublishProblem(null);
    openEditModal(property, tab);
  }

  function handleLogout() {
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

  const activeIndex = TABS.findIndex((tab) => tab.id === activeTab);
  const imageCount = existingImages.length + selectedImages.length;
  const savedCorretaje = savedDocs.some((doc) => doc.doc_type === "CORRETAJE");
  const stagedCorretaje = stagedDocs.some((doc) => doc.doc_type === "CORRETAJE");

  // Al editar, lo guardado se juzga con la regla del servidor (DS-15); lo pendiente de
  // guardar se marca en ámbar porque todavía no cuenta para publicar.
  const serverMissing = requirements?.kind === "ready" ? requirements.data.missing_requirements : null;
  const missingOf = (code: MissingRequirement["code"]) => serverMissing?.find((item) => item.code === code);
  const imageOk = serverMissing ? !missingOf("image") : imageCount > 0;
  const imageRow = imageOk
    ? { dot: "bg-emerald-500", text: `${existingImages.length || imageCount} cargada(s)` }
    : selectedImages.length > 0
      ? { dot: "bg-amber-400", text: "Se subirá al guardar" }
      : { dot: "bg-slate-300", text: "Falta" };
  const corretajeMissing = missingOf("brokerage_contract");
  const corretajeOk = serverMissing ? !corretajeMissing : savedCorretaje;
  const corretajeRow = corretajeOk
    ? { dot: "bg-emerald-500", text: serverMissing ? "Vigente" : "Cargado" }
    : stagedCorretaje
      ? { dot: "bg-amber-400", text: "Se subirá al guardar" }
      : { dot: corretajeMissing ? "bg-red-400" : "bg-slate-300", text: corretajeMissing?.message ?? "Falta" };

  return (
     <>

       <main className="min-h-screen bg-slate-50 px-4 py-10 sm:px-6 lg:px-8">
         <div className="mx-auto max-w-6xl">
           <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Urbanex</p>
              <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">Mis propiedades</h1>
              <p className="mt-2 flex items-center gap-2 text-slate-600 font-medium bg-slate-200/50 inline-block px-3 py-1 rounded-full">
                {userInfo.email} <span className="text-slate-400">|</span> <span className="capitalize text-blue-700">Rol: {userInfo.role}</span>
              </p>
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

           {notice && (
             <div
               role="status"
               className={`mb-4 flex items-start justify-between gap-4 rounded-lg border p-4 text-sm ${
                 notice.kind === "warning" ? "border-amber-200 bg-amber-50 text-amber-900" : "border-green-200 bg-green-50 text-green-800"
               }`}
             >
               <div>
                 <p className="font-semibold">{notice.title}</p>
                 {notice.lines.length > 0 && (
                   <ul className="mt-2 list-disc space-y-1 pl-5">
                     {notice.lines.map((line) => <li key={line}>{line}</li>)}
                   </ul>
                 )}
               </div>
               <button type="button" onClick={() => setNotice(null)} aria-label="Cerrar aviso" className="font-bold opacity-60 hover:opacity-100">
                 ×
               </button>
             </div>
           )}

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
                       <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wider text-slate-600">Asesor a cargo</th>
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
                         <td className="whitespace-nowrap px-6 py-4 text-sm text-slate-600">
                              {property.agent_name || userInfo.email}
                         </td>
                        <td className="whitespace-nowrap px-6 py-4">
                          <div className="flex gap-2">
                           <button
                             type="button"
                             onClick={() => openEditModal(property)}
                             className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
                             Editar
                           </button>
                           <Link
                             href={`/dashboard/properties/${property.id}/appraisal`}
                             className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100">
                             Avalúo
                           </Link>
                           {/* El servidor solo publica desde captación (DS-07, DT-46) */}
                           {property.status === "captacion" && (
                             <button
                               type="button"
                               onClick={() => setPublishCandidate(property)}
                               disabled={publishingId !== null}
                               className="rounded-lg bg-blue-700 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:opacity-60">
                               {publishingId === property.id ? "Publicando..." : "Publicar"}
                             </button>
                           )}
                          </div>
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
           <form
             onSubmit={handleSaveProperty}
             noValidate
             className="flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl"
           >
             {/* Encabezado */}
             <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-6 pt-5 pb-4">
               <div>
                 <p className="text-xs font-semibold uppercase tracking-wider text-blue-700">
                   {editingId ? "Edición de ficha" : "Nueva captación"}
                 </p>
                 <h2 className="text-xl font-bold text-slate-900">
                   {editingId ? formData.title || "Editar propiedad" : "Registrar nueva propiedad"}
                 </h2>
               </div>
               <button type="button" onClick={closeModal} aria-label="Cerrar" className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700">
                 <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                   <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
                 </svg>
               </button>
             </div>

             {/* Viñetas */}
             <div role="tablist" aria-label="Secciones de la propiedad" className="grid grid-cols-2 gap-1 border-b border-slate-200 bg-slate-50 px-3 py-2 sm:grid-cols-4">
               {TABS.map((tab, index) => {
                 const isActive = tab.id === activeTab;
                 const hasErrors = Boolean(formErrors[tab.id]?.length);
                 return (
                   <button
                     key={tab.id}
                     type="button"
                     role="tab"
                     aria-selected={isActive}
                     onClick={() => setActiveTab(tab.id)}
                     className={`flex items-center gap-3 rounded-lg px-3 py-2 text-left transition ${
                       isActive ? "bg-white shadow-sm ring-1 ring-slate-200" : "hover:bg-white/60"
                     }`}
                   >
                     <span
                       className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                         hasErrors
                           ? "bg-red-100 text-red-700"
                           : isActive
                             ? "bg-blue-700 text-white"
                             : "bg-slate-200 text-slate-600"
                       }`}
                     >
                       {hasErrors ? "!" : index + 1}
                     </span>
                     <span className="min-w-0">
                       <span className={`block truncate text-sm font-semibold ${isActive ? "text-slate-900" : "text-slate-600"}`}>{tab.label}</span>
                       <span className="hidden truncate text-xs text-slate-500 lg:block">{tab.hint}</span>
                     </span>
                   </button>
                 );
               })}
             </div>

             {/* Contenido de la viñeta activa */}
             <div role="tabpanel" className="flex-1 overflow-y-auto px-6 py-5">
               {saveErrors.length > 0 && (
                 <div role="alert" className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                   <p className="font-semibold">No se pudo guardar la propiedad:</p>
                   <ul className="mt-1 list-disc space-y-0.5 pl-4">
                     {saveErrors.map((message) => <li key={message}>{message}</li>)}
                   </ul>
                 </div>
               )}
               {formErrors[activeTab]?.length ? (
                 <div role="alert" className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                   <ul className="list-disc space-y-0.5 pl-4">
                     {formErrors[activeTab]!.map((message) => <li key={message}>{message}</li>)}
                   </ul>
                 </div>
               ) : null}

               {activeTab === "general" && (
                 <div className="space-y-5">
                   <Field label="Título">
                     <input type="text" value={formData.title} onChange={(e) => updateField("title", e.target.value)} placeholder="Ej. Departamento con vista al parque La Carolina" className={inputClass} />
                   </Field>

                   <div>
                     <span className="block text-xs font-semibold uppercase text-slate-700 mb-2">Tipo de propiedad</span>
                     <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
                       {PROPERTY_TYPES.map((type) => (
                         <button
                           key={type.value}
                           type="button"
                           onClick={() => updateField("property_type", type.value)}
                           className={`rounded-lg border px-3 py-2.5 text-sm font-semibold transition ${
                             formData.property_type === type.value
                               ? "border-blue-600 bg-blue-50 text-blue-800 ring-2 ring-blue-100"
                               : "border-slate-300 text-slate-600 hover:border-slate-400"
                           }`}
                         >
                           {type.label}
                         </button>
                       ))}
                     </div>
                   </div>

                   <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                     <Field label="Precio referencial (USD)">
                       <input type="number" min="0" step="0.01" value={formData.price} onChange={(e) => updateField("price", e.target.value)} className={inputClass} />
                     </Field>
                     <Field label="Área total (m²)">
                       <input type="number" min="0" step="0.01" value={formData.area_m2} onChange={(e) => updateField("area_m2", e.target.value)} className={inputClass} />
                     </Field>
                   </div>

                   <div className="grid grid-cols-3 gap-4">
                     <Field label="Habitaciones">
                       <input type="number" min="0" value={formData.bedrooms} onChange={(e) => updateField("bedrooms", Number(e.target.value))} className={inputClass} />
                     </Field>
                     <Field label="Baños">
                       <input type="number" min="0" value={formData.bathrooms} onChange={(e) => updateField("bathrooms", Number(e.target.value))} className={inputClass} />
                     </Field>
                     <Field label="Parqueaderos">
                       <input type="number" min="0" value={formData.parking_spaces} onChange={(e) => updateField("parking_spaces", Number(e.target.value))} className={inputClass} />
                     </Field>
                   </div>

                   <Field label="Descripción" hint="Destaca acabados, entorno y servicios cercanos.">
                     <textarea value={formData.description} onChange={(e) => updateField("description", e.target.value)} className={inputClass} rows={4} />
                   </Field>
                 </div>
               )}

               {activeTab === "location" && (
                 <div className="space-y-5">
                   <Field label="Dirección referencial" hint="Se muestra en el catálogo. Puedes completarla con el buscador del mapa.">
                     <input type="text" value={formData.location} onChange={(e) => updateField("location", e.target.value)} placeholder="Ej. Sector La Carolina, Quito" className={inputClass} />
                   </Field>

                   <div>
                     <span className="block text-xs font-semibold uppercase text-slate-700 mb-1">Ubicación exacta</span>
                     <p className="text-xs text-slate-500 mb-2">Busca el sector o haz clic en el mapa para posicionar el marcador.</p>
                     <MapPicker
                       position={{ lat: formData.latitude, lng: formData.longitude }}
                       setPosition={(pos) => setFormData((prev) => ({ ...prev, latitude: pos.lat, longitude: pos.lng }))}
                       onAddressFound={(address) => setFormData((prev) => (prev.location.trim() ? prev : { ...prev, location: address }))}
                     />
                     <div className="mt-2 flex flex-wrap gap-2 font-mono text-xs">
                       <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-600">Lat {formData.latitude.toFixed(6)}</span>
                       <span className="rounded-md bg-slate-100 px-2 py-1 text-slate-600">Lng {formData.longitude.toFixed(6)}</span>
                     </div>
                   </div>
                 </div>
               )}

               {activeTab === "media" && (
                 <div className="space-y-5">
                   <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-center transition hover:border-blue-400 hover:bg-blue-50/40">
                     <svg className="mb-2 h-8 w-8 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                       <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 15.75 5.16-5.16a2.25 2.25 0 0 1 3.18 0l5.16 5.16m-1.5-1.5 1.41-1.41a2.25 2.25 0 0 1 3.18 0l2.91 2.91M3.75 21h16.5A1.5 1.5 0 0 0 21.75 19.5v-15A1.5 1.5 0 0 0 20.25 3H3.75A1.5 1.5 0 0 0 2.25 4.5v15A1.5 1.5 0 0 0 3.75 21Z" />
                     </svg>
                     <span className="text-sm font-semibold text-slate-700">Haz clic para agregar fotografías</span>
                     <span className="mt-1 text-xs text-slate-500">JPG, PNG o WEBP · Se requiere al menos 1 fotografía</span>
                     <input type="file" multiple accept="image/*" onChange={handleImageChange} className="sr-only" />
                   </label>

                   {imageCount === 0 ? (
                     <p className="text-center text-sm text-slate-500">Aún no hay fotografías para esta propiedad.</p>
                   ) : (
                     <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                       {existingImages.map((img, index) => (
                         <figure key={img.id} className="relative aspect-[4/3] overflow-hidden rounded-lg border border-slate-200">
                           {/* eslint-disable-next-line @next/next/no-img-element */}
                           <img src={img.image} alt={img.caption || "Fotografía guardada"} className="h-full w-full object-cover" />
                           <span className="absolute left-2 top-2 rounded bg-slate-900/70 px-1.5 py-0.5 text-[10px] font-semibold text-white">
                             {index === 0 ? "Portada" : "Guardada"}
                           </span>
                         </figure>
                       ))}
                       {selectedImages.map((img, index) => (
                         <figure key={img.preview} className="relative aspect-[4/3] overflow-hidden rounded-lg border-2 border-blue-300">
                           {/* eslint-disable-next-line @next/next/no-img-element */}
                           <img src={img.preview} alt={img.file.name} className="h-full w-full object-cover" />
                           <span className="absolute left-2 top-2 rounded bg-blue-700 px-1.5 py-0.5 text-[10px] font-semibold text-white">Nueva</span>
                           <button type="button" onClick={() => removeSelectedImage(index)} aria-label={`Quitar ${img.file.name}`} className="absolute right-2 top-2 rounded-full bg-white/90 px-2 text-sm font-bold text-slate-700 shadow hover:bg-white">
                             ×
                           </button>
                         </figure>
                       ))}
                     </div>
                   )}
                 </div>
               )}

               {activeTab === "docs" && (
                 <div className="space-y-5">
                   <div className="rounded-xl border border-slate-200 p-4">
                     <p className="mb-3 text-xs font-semibold uppercase text-slate-700">Requisitos para publicar</p>
                     <ul className="space-y-2 text-sm">
                       <li className="flex items-center gap-2">
                         <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${imageRow.dot}`} />
                         <span className="text-slate-700">Al menos 1 fotografía</span>
                         <span className="ml-auto text-right text-xs text-slate-500">{imageRow.text}</span>
                       </li>
                       <li className="flex items-center gap-2">
                         <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${corretajeRow.dot}`} />
                         <span className="text-slate-700">Contrato de corretaje</span>
                         <span className="ml-auto text-right text-xs text-slate-500">{corretajeRow.text}</span>
                       </li>
                       <li className="flex items-center gap-2">
                         <span
                           className={`h-2.5 w-2.5 rounded-full ${
                             appraisalRequirement === "approved" ? "bg-emerald-500" : appraisalRequirement === "draft" ? "bg-amber-400" : "bg-slate-300"
                           }`}
                         />
                         <span className="text-slate-700">Avalúo aprobado</span>
                         <span className="ml-auto text-right text-xs text-slate-500">
                           {!editingId
                             ? "Se registra después de guardar la propiedad"
                             : appraisalRequirement === "loading"
                               ? "Consultando..."
                               : appraisalRequirement === "approved"
                                 ? "Aprobado"
                                 : appraisalRequirement === "draft"
                                   ? "En borrador"
                                   : appraisalRequirement === "error"
                                     ? "No se pudo consultar"
                                     : "Falta"}
                           {editingId && (
                             <Link href={`/dashboard/properties/${editingId}/appraisal`} className="ml-2 font-semibold text-blue-700 hover:underline">
                               Abrir avalúo
                             </Link>
                           )}
                         </span>
                       </li>
                     </ul>
                     {editingId && requirements && (
                       <p
                         role="status"
                         className={`mt-3 rounded-lg px-3 py-2 text-xs font-medium ${
                           requirements.kind === "ready" && requirements.data.can_publish
                             ? "bg-emerald-50 text-emerald-800"
                             : requirements.kind === "error"
                               ? "bg-red-50 text-red-800"
                               : "bg-slate-50 text-slate-600"
                         }`}
                       >
                         {requirements.kind === "loading"
                           ? "Consultando los requisitos en el servidor..."
                           : requirements.kind === "error"
                             ? "No se pudieron consultar los requisitos en el servidor."
                             : requirements.data.status !== "captacion"
                               ? `Esta propiedad ya no está en captación (${STATUS_LABELS[requirements.data.status] ?? requirements.data.status}); no se vuelve a publicar.`
                               : requirements.data.can_publish
                                 ? "Según el servidor está lista para publicar: usa \"Publicar\" en la tabla."
                                 : `Según el servidor faltan ${requirements.data.missing_requirements.length} requisito(s) para publicar. Lo que agregues aquí cuenta después de guardar.`}
                       </p>
                     )}
                   </div>

                   {savedDocsError && (
                     <div role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{savedDocsError}</div>
                   )}

                   {savedDocs.length > 0 && (
                     <div>
                       <p className="mb-2 text-xs font-semibold uppercase text-slate-700">Expediente guardado (versiones vigentes)</p>
                       <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200">
                         {savedDocs.map((doc) => (
                           <li key={doc.id} className="flex items-center gap-3 px-4 py-3 text-sm">
                             <div className="min-w-0 flex-1">
                               <p className="font-semibold text-slate-800">
                                 {doc.doc_type_display}
                                 <span className="ml-2 text-xs font-normal text-slate-500">v{doc.version}</span>
                                 {doc.is_critical && <span className="ml-2 rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-bold uppercase text-red-700">Crítico</span>}
                               </p>
                               <p className="truncate text-xs text-slate-500">
                                 {doc.original_filename} · {formatBytes(doc.file_size_bytes)} · vigente hasta {doc.expiration_date}
                                 {doc.is_expired && <span className="ml-1 font-semibold text-red-600">(vencido)</span>}
                                 {doc.is_expiring_soon && <span className="ml-1 font-semibold text-amber-600">(vence pronto)</span>}
                               </p>
                             </div>
                             <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">{doc.validation_status_display}</span>
                           </li>
                         ))}
                       </ul>
                       <p className="mt-1 text-xs text-slate-500">Para reemplazar un documento, súbelo de nuevo: se guardará como una nueva versión.</p>
                     </div>
                   )}

                   <div className="grid grid-cols-1 gap-4 rounded-xl border border-slate-200 p-4 sm:grid-cols-2">
                     <Field label="Tipo de documento">
                       <select value={docDraft.doc_type} onChange={(e) => setDocDraft({ ...docDraft, doc_type: e.target.value })} className={inputClass}>
                         {Object.entries(DOC_TYPES).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                       </select>
                     </Field>
                     <Field label="Archivo" hint="PDF o imagen, máximo 20 MB.">
                       <input key={docInputKey} type="file" accept={DOC_ACCEPT} onChange={(e) => setDocFile(e.target.files?.[0] ?? null)} className="w-full text-sm text-slate-500 file:mr-3 file:rounded-lg file:border-0 file:bg-blue-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-blue-700 hover:file:bg-blue-100" />
                     </Field>
                     <Field label="Fecha de emisión">
                       <input type="date" value={docDraft.issue_date} onChange={(e) => setDocDraft({ ...docDraft, issue_date: e.target.value })} className={inputClass} />
                     </Field>
                     <Field label="Fecha de vigencia">
                       <input type="date" value={docDraft.expiration_date} min={docDraft.issue_date || undefined} onChange={(e) => setDocDraft({ ...docDraft, expiration_date: e.target.value })} className={inputClass} />
                     </Field>
                     <label className="flex items-center gap-2 text-sm text-slate-700 sm:col-span-2">
                       <input type="checkbox" checked={docDraft.is_critical} onChange={(e) => setDocDraft({ ...docDraft, is_critical: e.target.checked })} className="h-4 w-4 rounded border-slate-300" />
                       Documento crítico (bloquea el avance si falta o vence)
                     </label>
                     {docError && <p role="alert" className="text-sm text-red-600 sm:col-span-2">{docError}</p>}
                     <div className="sm:col-span-2">
                       <button type="button" onClick={handleAddDocument} className="rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700 transition hover:bg-blue-100">
                         + Agregar al expediente
                       </button>
                     </div>
                   </div>

                   {stagedDocs.length > 0 && (
                     <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200">
                       {stagedDocs.map((doc) => (
                         <li key={doc.key} className="flex items-center gap-3 px-4 py-3 text-sm">
                           <div className="min-w-0 flex-1">
                             <p className="font-semibold text-slate-800">
                               {DOC_TYPES[doc.doc_type]}
                               {doc.is_critical && <span className="ml-2 rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-bold uppercase text-red-700">Crítico</span>}
                             </p>
                             <p className="truncate text-xs text-slate-500">
                               {doc.file.name} · {formatBytes(doc.file.size)} · vigente hasta {doc.expiration_date}
                             </p>
                           </div>
                           <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">Por subir</span>
                           <button type="button" onClick={() => setStagedDocs((prev) => prev.filter((d) => d.key !== doc.key))} aria-label={`Quitar ${doc.file.name}`} className="text-slate-400 hover:text-red-600">
                             ×
                           </button>
                         </li>
                       ))}
                     </ul>
                   )}
                 </div>
               )}
             </div>

             {/* Pie: navegación entre viñetas y guardado */}
             <div className="flex items-center justify-between gap-3 border-t border-slate-200 bg-slate-50 px-6 py-4">
               <span className="text-xs font-medium text-slate-500">Paso {activeIndex + 1} de {TABS.length}</span>
               <div className="flex gap-2">
                 <button type="button" onClick={closeModal} className="rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-200">Cancelar</button>
                 {activeIndex > 0 && (
                   <button type="button" onClick={() => setActiveTab(TABS[activeIndex - 1].id)} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">
                     Anterior
                   </button>
                 )}
                 {activeIndex < TABS.length - 1 && (
                   <button type="button" onClick={() => setActiveTab(TABS[activeIndex + 1].id)} className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100">
                     Siguiente
                   </button>
                 )}
                 <button type="submit" disabled={saving} className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800 disabled:opacity-60">
                   {saving ? "Guardando..." : editingId ? "Guardar cambios" : "Registrar propiedad"}
                 </button>
               </div>
             </div>
           </form>
         </div>
       )}

       <Dialog
         open={publishCandidate !== null}
         title="¿Publicar esta propiedad?"
         confirmLabel={publishingId !== null ? "Publicando..." : "Publicar"}
         busy={publishingId !== null}
         onConfirm={() => publishCandidate && handlePublish(publishCandidate)}
         onCancel={() => setPublishCandidate(null)}
       >
         <p>
           &quot;{publishCandidate?.title}&quot; pasará a <strong>Disponible</strong> y será visible para cualquier
           persona en el catálogo público. El servidor comprobará antes la foto, el contrato de corretaje y el avalúo aprobado.
         </p>
       </Dialog>

       <Dialog
         open={publishProblem !== null}
         title="No se puede publicar todavía"
         tone="warning"
         confirmLabel="Entendido"
         onConfirm={() => setPublishProblem(null)}
       >
         {publishProblem && (
           <>
             <p>
               &quot;{publishProblem.property.title}&quot;: {publishProblem.detail}
             </p>
             {publishProblem.missing.length > 0 && (
               <ul className="mt-3 space-y-2">
                 {publishProblem.missing.map((item) => {
                   const fix = REQUIREMENT_TABS[item.code];
                   return (
                     <li key={`${item.code}-${item.message}`} className="flex items-start justify-between gap-3 rounded-lg bg-amber-50 px-3 py-2 text-amber-900">
                       <span>{item.message}</span>
                       {item.code === "appraisal" ? (
                         <Link href={`/dashboard/properties/${publishProblem.property.id}/appraisal`} className="shrink-0 font-semibold text-blue-700 hover:underline">
                           Ir al avalúo
                         </Link>
                       ) : fix ? (
                         <button type="button" onClick={() => fixRequirement(publishProblem.property, fix.tab)} className="shrink-0 font-semibold text-blue-700 hover:underline">
                           {fix.label}
                         </button>
                       ) : null}
                     </li>
                   );
                 })}
               </ul>
             )}
           </>
         )}
       </Dialog>
     </>
   );
}
