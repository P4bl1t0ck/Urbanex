"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function LoginPage(){
  //Our parameters defined in our Epics
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  //Funcion para manejar el error, y el inicio de sesion para el dashboard comun
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try{
      const data = await apiFetch("/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify({email, password}),
        }
      );
      localStorage.setItem("access", data.access);
      router.push("/dashboard");
      //Our try what it wants to fetch, is the email and password inside the path /api/auth/login
    }catch{
      setError("Credenciales inválidas o cuenta bloqueda. ");
      //Obviusly the main error of what happens if one of the email or password is not correct.
    }
  }

  //This JSX form is going to take our data, like the email, and the password.

  return (
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