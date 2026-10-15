import Image from "next/image";
import Link from "next/link";
import { getPropertyById } from "@/lib/api";

//We import our images, the router and the function for move between ids
export default async function PropertyDetailPage({params}: {params: Promise<{id: string}>}) {
    try{
        //Resolvemos el params debe ser todo un promise. Al momento de el fetch
        const waitparams= await params;
        const property = await getPropertyById(waitparams.id);

         
        const mainImage = property.images && property.images.lenght > 0
            ? property.images[0].image : '/placeholder-property.jpg';
        
        return (
            <main className="container mx-auto px-4 py-8 bg-white min-h-screen">
        {/* Botón para regresar al catálogo */}
        <div className="mb-6">
          <Link href="/properties" className="text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2">
            <span>&larr;</span> Volver al catálogo
          </Link>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Columna Izquierda: Imagen Principal */}
          <div className="relative h-[400px] lg:h-[500px] w-full rounded-2xl overflow-hidden shadow-lg">
            <Image 
              src={mainImage} 
              alt={property.title} 
              fill 
              className="object-cover"
              unoptimized
            />
            
          </div>

          {/* Columna Derecha: Detalles de la Propiedad */}
          <div className="flex flex-col justify-center">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-2">{property.title}</h1>
            <p className="text-lg text-gray-500 mb-6">{property.location}</p>
            
            <div className="text-4xl font-bold text-blue-700 mb-8">
              ${Number(property.price).toLocaleString('es-EC')}
            </div>

            <div className="bg-gray-50 p-6 rounded-xl border border-gray-100 mb-8">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Características principales</h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-white rounded-lg shadow-sm">
                  <span className="block text-2xl mb-1">🛏️</span>
                  <span className="font-bold text-gray-900">{property.bedrooms}</span>
                  <p className="text-xs text-gray-500">Habitaciones</p>
                </div>
                <div className="p-3 bg-white rounded-lg shadow-sm">
                  <span className="block text-2xl mb-1">🛁</span>
                  <span className="font-bold text-gray-900">{property.bathrooms}</span>
                  <p className="text-xs text-gray-500">Baños</p>
                </div>
                <div className="p-3 bg-white rounded-lg shadow-sm">
                  <span className="block text-2xl mb-1">📐</span>
                  <span className="font-bold text-gray-900">{property.area_m2}</span>
                  <p className="text-xs text-gray-500">Metros²</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Descripción</h3>
              <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                {property.description}
              </p>
            </div>
          </div>
        </div>
      </main>
        ); 

    }catch(error){
        return(
            //Main error if its not working the main Card for each propertie on his respective detail.
            <div>
                <h2 className="text-red-600 text-2xl font-bold mb-4" >Propiedad no encontrada</h2>
                <Link href="/properties" className="text-blue-600 underline"> Regresar al catalogo </Link>
            </div>
        );
    }
}