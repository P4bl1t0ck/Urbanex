import type { Property, PropertyCatalogFilters, PropertyCatalogPage } from '@/types/property';
import { clearAuthSession, notifyAuthSessionChanged } from "@/lib/auth-session";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

//We create the modular function for handle the infor from the DANJO API.

export async function apiFetch<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const body = await parseResponseBody(res);
  if (!res.ok) throw new ApiError(res.status, body);
  return body as T;
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
  if (body && typeof body === "object") {
    const data = body as Record<string, unknown>;
    if (typeof data.detail === "string") return data.detail;
    // DRF: {campo: ["mensaje"]} o {non_field_errors: [...]} o ["mensaje"]
    const first = Array.isArray(body) ? body[0] : Object.values(data)[0];
    const message = Array.isArray(first) ? first[0] : first;
    if (typeof message === "string") return message;
  }
  if (status === 401) return "La sesión venció. Inicia sesión nuevamente.";
  return `Error ${status} al comunicarse con el servidor.`;
}

async function parseResponseBody(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getCookie(name: string): string | null {
  const cookie = document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : null;
}

async function getCsrfToken(): Promise<string> {
  let token = getCookie("csrftoken");
  if (!token) {
    const response = await fetch(`${API_URL}/api/auth/csrf/`, {
      cache: "no-store",
      credentials: "include",
    });
    const body = await parseResponseBody(response);
    if (!response.ok) throw new ApiError(response.status, body);
    token = getCookie("csrftoken");
  }
  if (!token) throw new Error("No se pudo preparar la protección CSRF.");
  return token;
}

async function refreshAccessToken(): Promise<string | null> {
  const csrfToken = await getCsrfToken();
  const response = await fetch(`${API_URL}/api/token/refresh/`, {
    method: "POST",
    cache: "no-store",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: "{}",
  });
  const body = await parseResponseBody(response);

  if (response.status === 401) return null;
  if (!response.ok) throw new ApiError(response.status, body);
  if (
    !body ||
    typeof body !== "object" ||
    !("access" in body) ||
    typeof body.access !== "string"
  ) {
    throw new Error("El servidor no devolvió un token de acceso válido.");
  }

  sessionStorage.setItem("access", body.access);
  notifyAuthSessionChanged();
  return body.access;
}

export async function logoutRefreshSession(): Promise<void> {
  const csrfToken = await getCsrfToken();
  const response = await fetch(`${API_URL}/api/auth/logout/`, {
    method: "POST",
    cache: "no-store",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: "{}",
  });
  const body = await parseResponseBody(response);
  if (!response.ok) throw new ApiError(response.status, body);
}

// Peticiones autenticadas con el token de la pestaña (HU-46: sessionStorage).
export async function authFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = sessionStorage.getItem("access");
  const requestWithToken = (accessToken: string | null) => {
    const headers = new Headers({ "Content-Type": "application/json" });
    new Headers(options.headers).forEach((value, key) => headers.set(key, value));
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    return fetch(`${API_URL}${path}`, {
      cache: "no-store",
      ...options,
      headers,
    });
  };

  let res = await requestWithToken(token);
  if (res.status === 401 && token) {
    let refreshedToken: string | null;
    try {
      refreshedToken = await refreshAccessToken();
    } catch (error: unknown) {
      clearAuthSession();
      throw error;
    }

    if (refreshedToken) {
      res = await requestWithToken(refreshedToken);
    }
    if (!refreshedToken || res.status === 401) clearAuthSession();
  }

  const body = await parseResponseBody(res);

  if (!res.ok) {
    if (res.status === 401) {
      throw new ApiError(res.status, {
        detail: "La sesión venció. Inicia sesión nuevamente.",
      });
    }
    throw new ApiError(res.status, body);
  }
  return body as T;
}

//The API router of how we are gonna used the informaqtion.
//The asyncronic function that we are gonna use for fetch the images and the database info.

export async function getProperties(filters: PropertyCatalogFilters = {}): Promise<PropertyCatalogPage> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value?.trim()) params.set(key, value.trim());
  }
  return apiFetch<PropertyCatalogPage>(`/api/auth/properties/?${params}`, {
    cache: "no-store",
  });
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
