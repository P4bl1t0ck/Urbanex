"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { notifyAuthSessionChanged } from "@/lib/auth-session";
import { useRouter } from "next/navigation";

export default function LoginPage(){
  const router = useRouter();
  //Our parameters defined in our Epics
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

    //Use Effect se ejecuta una sola veez cuando la pagina termina de cargar
    //Su trabajo aqui es "Mirar la libreta de esta pestaña" (SessionStorage)
    //If there´s already an saved token,  the blank pus the direct dashboard for not ask for the login again. 

    useEffect(() => { 
    //Revisa si el usuario ya esta iniciado sesion y lo redirige al /dashboard
    if (typeof window !== "undefined") {
      //const token = localStorage.getItem("access");
      const token = sessionStorage.getItem("access");
      //Change: sessionStorage for insolated session. 
      if (token) {
        router.replace("/dashboard");
      }
    }
  }, [router])

  //Funcion para manejar el error, y el inicio de sesion para el dashboard comun
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try{
      const data = await apiFetch<{ access?: string; refresh?: string; role?: string }>("/api/auth/login/", //Fetchs the info from the :8. and then pass the view
        {
          //Ya debe de estar en formato json, es por eso el error al intentar interpretar un json(json)
          method: "POST",
          body: JSON.stringify({email, password}),
        });

        if (data?.access) {     
          sessionStorage.setItem("access", data.access);
          //Guardamos el rol (si el backend lo envia) y el email que tipéo el susuario
          sessionStorage.setItem("userRole",data.role || "asesor" );
          sessionStorage.setItem("userEmail",email);
          notifyAuthSessionChanged();
          router.replace("/dashboard");
        } else {
          setError("No se recibió el token de acceso.");
        }

    }catch (err: unknown){
      console.error("Error al iniciar sesión:", err); //Mas detalle en caso de error de login.
      setError(err instanceof Error ? err.message : "Credenciales inválidas o cuenta bloqueada.");
      //Obviusly the main error of what happens if one of the email or password is not correct.
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-16">
      <form
        onSubmit={handleSubmit}
        className="mx-auto mt-8 flex max-w-md flex-col gap-5 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8"
      >
        <div>
          <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">Urbanex</p>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Iniciar sesión</h1>
          <p className="mt-2 text-sm text-slate-600">Ingresa con el correo y la contraseña de tu cuenta.</p>
        </div>
        <label className="block text-sm font-medium text-slate-700">
          Correo electrónico
          <input
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </label>
        <label className="block text-sm font-medium text-slate-700">
          Contraseña
          <input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
          />
        </label>
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        <button
          type="submit"
          className="rounded-lg bg-blue-700 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800"
        >
          Entrar
        </button>
      </form>
    </main>
  );
}