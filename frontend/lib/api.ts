import { Property } from '@/types/property';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

//We create the modular function for handle the infor from the DANJO API.

export async function apiFetch(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!res.ok) throw new Error(`Error ${res.status}`);
  return res.json();
}

//The API router of how we are gonna used the informaqtion.
//The asyncronic function that we are gonna use for fetch the images and the database info.

export async function getProperties(): Promise<Property[]>  {
  const res = await fetch(`${API_URL}/api/auth/properties/`,{
    cache: 'no-store', // SWe didnt store any type of data inside the we html based.
  }); //We pass all the info from the backend.
  
  if(!res.ok){
    throw new Error('Error al obtener la lista de propiedades');
  } //We handle the error with this.

  return res.json(); 
  //La devolvemos en json.
}

//More specific Function of seacrhing the Property.
export async function getPropertyById(id:string): Promise<Property> {
  const res = await fetch(`${API_URL}/properties/${id}/`, {
    cache: 'no-store',
    //Para que no se guarde dentro del cache.
  })
  
  if(!res.ok){
    throw new Error(`Error al obtener la propiedad con ID: ${id}`)
  }
  return res.json();
}

