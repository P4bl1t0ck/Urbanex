import HomeSearch from "@/components/HomeSearch";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      
      
      <main className="flex-grow bg-gradient-to-b from-blue-50/70 to-slate-50 px-4 py-12 text-center sm:px-6 sm:py-20 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <p className="text-sm font-semibold uppercase tracking-wider text-blue-700 mb-4">
            Plataforma Inmobiliaria Integrada
          </p>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight mb-6">
            Encuentra tu próximo hogar con <span className="text-blue-700">Urbanex</span>
          </h1>
          <p className="text-lg sm:text-xl text-slate-600 mb-10 leading-relaxed">
            Encuentra propiedades para comprar o alquilar en el lugar que buscas.
          </p>
          
          <HomeSearch />

        </div>
      </main>

      <footer className="bg-slate-900 py-8 text-center text-slate-400 text-sm">
        <p>&copy; {new Date().getFullYear()} Urbanex Real Estate. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}
