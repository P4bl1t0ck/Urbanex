// app/properties/page.tsx
import { getProperties } from "@/lib/api";
import PropertyCard from "@/components/PropertyCard";

/*  We handle the main View  of our properties.*/
export default async function PropertiesPage() {
    const properties = await getProperties();
    /**Despues manejramos los estilos, por el momento solo creremos la pagina principal. */
    return(
        <main>
      <h1 >Catálogo de Propiedades - Urbanex</h1>
      
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
}
