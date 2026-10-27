import { Property } from '@/types/property';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

//We create the modular function for handle the infor from the DANJO API.

export async function apiFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

// Error de la API que conserva el estado HTTP y el cuerpo (errores por campo de DRF,
// missing_requirements de publicar, etc.) para que cada pantalla los muestre.
export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super(getErrorMessage(status, body));
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function getErrorMessage(status: number, body: unknown): string {
  if (status === 401) return "La sesión venció. Inicia sesión nuevamente.";
  if (body && typeof body === "object") {
    const data = body as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    // DRF: {campo: ["mensaje"]} o {non_field_errors: [...]} o ["mensaje"]
    const first = Array.isArray(body) ? body[0] : Object.values(data)[0];
    const message = Array.isArray(first) ? first[0] : first;
    if (typeof message === "string") return message;
  }
  return `Error ${status} al comunicarse con el servidor.`;
}

// Peticiones autenticadas con el token de la pestaña (HU-46: sessionStorage).
export async function authFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = sessionStorage.getItem("access");
  const res = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  const text = await res.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text; // p. ej. página HTML de error de Django
    }
  }

  if (!res.ok) throw new ApiError(res.status, body);
  return body as T;
}

//The API router of how we are gonna used the informaqtion.
//The asyncronic function that we are gonna use for fetch the images and the database info.

export async function getProperties(): Promise<Property[]>  {
  const res = await fetch(`${API_URL}/api/auth/properties/`,{
    cache: 'no-store', // SWe didnt store any type of data inside the we html based.
  }); //We pass all the info from the backend.
  
  if(!res.ok){
    throw new Error('Error al obtener la lista de propiedades');
  } //We handle the error with this.

  return res.json(); 
  //La devolvemos en json.
}

//More specific Function of seacrhing the Property.
export async function getPropertyById(id:string): Promise<Property> {
  const res = await fetch(`${API_URL}/api/auth/properties/${id}/`, {
    cache: 'no-store',
    //Para que no se guarde dentro del cache.
  })
  
  if(!res.ok){
    throw new Error(`Error al obtener la propiedad con ID: ${id}`)
  }
  return res.json();
}

