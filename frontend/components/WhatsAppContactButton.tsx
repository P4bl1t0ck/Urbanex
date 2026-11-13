"use client";

// P-07 (HU-15, RF-02, DS-50): botón "Escribir por WhatsApp" con el mensaje prellenado (título y
// código de la propiedad). El número del asesor captador lo da el backend ya normalizado
// (regla DS-28). El botón no se muestra si el backend devuelve null (asesor inactivo o sin
// celular válido), si la propiedad dejó de estar Disponible (404) o si la consulta falla.
// Simplificación aprobada (DS-50): no se registra el contacto en el backend antes de redirigir.

import { useEffect, useState } from "react";
import { getWhatsAppContact } from "@/lib/opportunities";
import { buildWhatsAppLink } from "@/lib/opportunityPipeline";

export default function WhatsAppContactButton({
  propertyId,
  title,
}: {
  propertyId: number;
  title: string;
}) {
  const [phone, setPhone] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    getWhatsAppContact(propertyId)
      .then((data) => {
        if (isActive) setPhone(data.whatsapp_phone);
      })
      .catch(() => {
        if (isActive) setPhone(null); // Ante cualquier error el botón queda oculto
      });
    return () => {
      isActive = false;
    };
  }, [propertyId]);

  if (!phone) return null;

  return (
    <a
      href={buildWhatsAppLink(phone, title, propertyId)}
      target="_blank"
      rel="noopener noreferrer"
      className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-3 text-base font-semibold text-white shadow-sm transition hover:bg-green-700 sm:w-auto"
    >
      <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5 fill-current">
        <path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.6.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3a.4.4 0 0 0 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.2 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.4-.3Z" />
      </svg>
      Escribir al asesor por WhatsApp
    </a>
  );
}
