"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function DashboardPage(){
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("access");
        if(!token){
            router.push("/login");
            return;
        }
        setLoading(false);
    }, [router]);

    function handleLogout(){
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        router.push("/login");
    }
    if (loading) return <p className="p-8">Cargando...</p>

    return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold mb-4">Dashboard</h1>
      <p className="mb-6">Sesión iniciada correctamente.</p>
      <button
        onClick={handleLogout}
        className="bg-black text-white rounded px-4 py-2"
      >
        Cerrar sesión
      </button>
    </div>
  );
}