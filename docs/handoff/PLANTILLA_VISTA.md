# Plantilla de vistas de Urbanex

Última actualización: 2026-11-18. Guía de presentación; no sustituye AGENTS.md ni introduce reglas de negocio.

Usar `frontend/components/PageLayout.tsx` en las vistas principales. El layout raíz ya contiene la navegación: no añadir otro `SiteNav`.

```tsx
import PageLayout, { PageHeader } from "@/components/PageLayout";

export default function ExamplePage() {
  return (
    <PageLayout width="standard">
      <PageHeader
        eyebrow="Nombre del módulo"
        title="Título de la vista"
        description="Explicación breve de lo que se puede hacer."
        actions={<button type="button">Acción principal</button>}
      />
      <section aria-label="Contenido de la vista">
        {/* Carga, error, vacío o contenido real. */}
      </section>
    </PageLayout>
  );
}
```

El botón es ilustrativo: conectar su acción antes de usarlo en una pantalla real.

| Elemento | Valor compartido |
|---|---|
| Separación desde navegación al bloque de contenido | `py-6`: 24 px con la configuración actual |
| Márgenes laterales | `px-4 sm:px-6 lg:px-8` |
| Ancho `catalog` | Máximo 1600 px; catálogo |
| Ancho `standard` | `max-w-6xl`; panel, oportunidades, disponibilidad y agenda |
| Ancho `narrow` | `max-w-5xl`; reservado para vistas que requieran un contenido estrecho |
| Separación entre encabezado y contenido | `mb-6`: 24 px |
| Antetítulo | Texto pequeño azul, mayúsculas |
| Título | Un `h1`, 24 px en móvil y 30 px desde `sm` |
| Descripción | Opcional, 8 px debajo del título |
| Acciones | Debajo del título en móvil; al lado en escritorio, con salto de línea |

El título puede ser un nodo React para variar por rol. La descripción admite texto o contenido breve; no colocar ahí formularios extensos. Para varias secciones, usar un contenedor `space-y-6` después del encabezado.

La navegación superior es el acceso entre módulos principales. Las listas de oportunidades, disponibilidad y agenda no repiten «Volver al panel». Los detalles y formularios pueden mantener un regreso contextual si ayuda a volver a su lista; esta guía no retira esos enlaces.

Usar el mismo `PageLayout` durante la carga para evitar cambiar la separación inicial. No sumar otro `pt-*`, margen superior o `SiteNav` por fuera sin revisar el resultado en móvil y escritorio. Un solo `PageHeader` por vista principal.

No generalizar esta plantilla a galerías, diálogos, login o ficha pública sin revisar sus necesidades. La primera adopción cubre catálogo, panel, oportunidades, disponibilidad y agenda; las demás vistas quedan fuera de este ajuste.

Esta plantilla solo organiza la presentación. Autorización, estado de sesión y permisos siguen siendo responsabilidad de cada flujo y de la API. Un enlace oculto no protege un endpoint.

Validación humana Pendiente: comparar inicio de los cinco antetítulos bajo la misma navegación, móvil y escritorio; comprobar acciones, estados de carga y navegación entre módulos. No marcar una V como aprobada por usar esta plantilla.
