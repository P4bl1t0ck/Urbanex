"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

export default function LoginPage(){
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
        window.location.href = "/dashboard";
      }
    }
  }, [])

  //Funcion para manejar el error, y el inicio de sesion para el dashboard comun
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try{
      const data = await apiFetch("/api/auth/login/", //Fetchs the info from the :8. and then pass the view 
        {
          //Ya debe de estar en formato json, es por eso el error al intentar interpretar un json(json)
          method: "POST",
          body: JSON.stringify({email, password}),
        });

        if (data?.access) {
          //localStorage.setItem("access", data.access);
          //We save the token in the sessionStorage, so when the user close the tab, the token is lost.
          sessionStorage.setItem("access", data.access);
          window.location.href = "/dashboard";
        } else {
          setError("No se recibió el token de acceso.");
        }
    }catch (err: any){
      console.error("Error al iniciar sesión:", err); //Mas detalle en caso de error de login.
      setError( err.message || "Credenciales inválidas o cuenta bloqueda. ");
      //Obviusly the main error of what happens if one of the email or password is not correct.
    }
  }

  //This JSX form is going to take our data, like the email, and the password.

  return ( //This is the view that it show when we fecth the info
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-sm mx-auto mt-20">
      <h1 className="text-2xl font-semibold">Iniciar sesión</h1>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Correo"
        className="border rounded px-3 py-2"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Contraseña"
        className="border rounded px-3 py-2"
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button type="submit" className="bg-black text-white rounded px-4 py-2">
        Entrar
      </button>
    </form>
  );
}