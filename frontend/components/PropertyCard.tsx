// components/PropertyCard.tsx
import Image from 'next/image';
import Link from 'next/link';
import { Property } from '@/types/property';
//We import our packages for images, and the property that we made. We fetch the infor from the API django to here. using a 'model' we do this. We can use this information from the API. Here.
export default function PropertyCard({ property }: { property: Property }) {
    /*
    We create the ImageCard of the property, setting the Property model or object as a property
     */
  // Tomamos la primera imagen subida o un placeholder por defecto
  const mainImage = property.images && property.images.length > 0 ? property.images[0].image : '/placeholder-property.jpg';
  //Una rapida comprobacion tomamos los valores de el largo de la imagen ,comprobamos que sea mayo a 0, Si es verdadero, Entonces otmamors de esas images. el inicial [0] y entonces renderizadas la ruta de esa imagen.

 //Devolvemos un HTML que consumira la imagen y la mostrara. 
  return (
    <div >
      <div >
        /*We bring literally the image */
        <img
        
          src={mainImage}
          alt={property.title}
          className="w-full h-full object-cover"
        />
        /*Agregamos el status */
        <span>
          {property.status.replace('_', ' ')}
        </span>
      </div>
    
      /*The put the title the bedrooms and the area_m2 */
      <div >
        <h3 >{property.title}</h3>
        <p >{property.location}</p>
        
        <div >
          <span> {property.bedrooms} hab</span>
          <span> {property.bathrooms} baños</span>
          <span> {property.area_m2} m2</span>
        </div>

        <div >
          <span >\${property.price}</span>
          <Link 
            href={`/properties/${property.id}`}
            className="bg-blue-600 text-white text-sm px-3 py-1.5 rounded hover:bg-blue-700"
          >
            Ver Detalle
          </Link>
        </div>
      </div>
    </div>
  );
}