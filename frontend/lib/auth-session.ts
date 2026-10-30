export const AUTH_SESSION_CHANGE_EVENT = "urbanex:auth-session-change";

export function getAuthSessionSnapshot() {
  if (typeof window === "undefined") return "";
  return JSON.stringify({
    access: sessionStorage.getItem("access"),
    email: sessionStorage.getItem("userEmail"),
    role: sessionStorage.getItem("userRole"),
  });
}

export function subscribeToAuthSession(callback: () => void) {
  window.addEventListener(AUTH_SESSION_CHANGE_EVENT, callback);
  window.addEventListener("storage", callback);
  return () => {
    window.removeEventListener(AUTH_SESSION_CHANGE_EVENT, callback);
    window.removeEventListener("storage", callback);
  };
}

export function notifyAuthSessionChanged() {
  window.dispatchEvent(new Event(AUTH_SESSION_CHANGE_EVENT));
}

export function clearAuthSession() {
  sessionStorage.removeItem("access");
  sessionStorage.removeItem("refresh");
  sessionStorage.removeItem("userRole");
  sessionStorage.removeItem("userEmail");
  notifyAuthSessionChanged();
}
