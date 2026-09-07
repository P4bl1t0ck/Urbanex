const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
//New Path for out project. Its the same as Setting on Django

export async function apiFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}