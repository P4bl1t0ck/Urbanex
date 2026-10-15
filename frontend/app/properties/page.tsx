// app/properties/page.tsx
import { getProperties } from "@/lib/api";
import PropertyCard from "@/components/PropertyCard";
import { Property } from "@/types/property";

/*  We handle the main View  of our properties.*/
export default async function PropertiesPage() {
  try{
  //An try just in case.
   const properties = await getProperties();
    /**Despues manejramos los estilos, por el momento solo creremos la pagina principal. */
    return(
        <main className="container mx-auto px-4 py-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight mb-2">
        Catálogo de Propiedades - Urbanex</h1>
      
      {properties.length === 0 ? (
        <p className="text-gray-500">No hay propiedades registradas aún.</p>
      ) : (
        <div >
          {properties.map((prop) => (
            <PropertyCard key={prop.id} property={prop} />
          ))}
        </div>
      )}
    </main>
    );
  }catch (error){
    return(
      <div className="container mx-auto px-4 py-20 text-center flex flex-col items-center">
        <div className="bg-red-50 p-6 rounded-lg border border-red-200">
          <h2 className="text-red-700 text-2xl font-bold mb-2">Error de conexión</h2>
          <p className="text-red-600">No pudimos cargar el catálogo. Verifica que el servidor backend esté en ejecución.</p>
        </div>
      </div>
    );
  }
}


   
