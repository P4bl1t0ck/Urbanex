import type { Metadata } from "next";
import PublicVisitView from "./PublicVisitView";

// P-08 (HU-20, RF-04, DS-39): datos de la visita por el enlace único del correo de confirmación.
// Solo lectura y solo hasta la hora de inicio; sin botón de cancelar (llega con HU-21).
// El enlace es privado: no se indexa y no se envía como Referer a otros sitios.
export const metadata: Metadata = {
  title: "Tu visita | Urbanex",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

type PublicVisitParams = { params: Promise<{ token: string }> };

export default async function PublicVisitPage({ params }: PublicVisitParams) {
  const { token } = await params;
  return <PublicVisitView token={token} />;
}
