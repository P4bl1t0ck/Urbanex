import Link from "next/link";
import SiteNav from "@/components/SiteNav";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <SiteNav />
      
      <main className="flex-grow flex flex-col items-center justify-center text-center px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-wider text-blue-700 mb-4">
            Plataforma Inmobiliaria Integrada
          </p>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mb-6">
            Encuentra tu próximo hogar con <span className="text-blue-700">Urbanex</span>
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 mb-10 leading-relaxed">
            Explora nuestro portafolio de propiedades, coordina visitas y gestiona tus oportunidades comerciales con la plataforma más avanzada del mercado.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Link 
              href="/properties" 
              className="w-full sm:w-auto rounded-lg bg-blue-700 px-8 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Explorar Catálogo Público
            </Link>
            <Link 
              href="/login" 
              className="w-full sm:w-auto rounded-lg bg-white px-8 py-3 text-base font-semibold text-slate-700 border border-slate-300 shadow-sm transition hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
            >
              Acceso Portal Asesores
            </Link>
            
          </div>
        </div>
      </main>

      <footer className="bg-slate-900 py-8 text-center text-slate-400 text-sm">
        <p>&copy; {new Date().getFullYear()} Urbanex Real Estate. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}