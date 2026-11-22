# Continuidad de trabajo — HU-11 y fixes asociados

**Fecha de corte:** 2026-11-20  
**Rama:** `feat/URB-14-HU-11-ficha-detalle`  
**Estado:** trabajo local pendiente de commit; no hay PR abierto por esta sesión.  
**Propósito:** permitir retomar el trabajo sin depender del historial del chat. No sustituye `AGENTS.md` ni los documentos de seguimiento existentes.

## 1. Cómo retomar de forma segura

1. Leer `AGENTS.md` y después la nota de cierre más reciente de `Project_Progress.md`.
2. Ejecutar `git status --short --branch`. No descartar los cambios locales listados en este documento.
3. Antes de un PR, actualizar referencias remotas, integrar `origin/develop` según `AGENTS.md` y ejecutar la auditoría de solo lectura obligatoria en un chat nuevo.
4. No versionar `backend/db.sqlite3`, `.env`, `backend/media/`, `backend/private_media/` ni `evidence/`.

## 2. Punto de Git exacto

- Remoto de la rama y `HEAD` al iniciar esta nota: `cebd44f` (`style(URB-14): elimina espacio final del componente de mapa`). `git rev-list --left-right --count origin/feat/URB-14-HU-11-ficha-detalle...HEAD` devolvió `0 0`.
- Base conocida de `origin/develop`: `6e0caca`.
- Ya están en GitHub 21 commits de esta rama, desde `b75e227` hasta `cebd44f`. No existe autorización en esta nota para abrir PR ni fusionar.
- Después de `cebd44f` hay cambios **solo locales y sin commit**. Son los que se deben revisar y confirmar antes de guardarlos.

### Commits ya respaldados

| Rango | Contenido principal |
| --- | --- |
| `b75e227` … `aa6d12c` | Almacenamiento de fotos local/Cloudinary, operación venta/arriendo, migración `users.0010`, contrato/API, borrado de fotos, avalúos y pruebas/datos demo. |
| `8eef5af` … `44e674a` | Telemetría de cargas de mapa, endpoint/estadísticas de administración, configuración compartida y pruebas. |
| `40118d9` … `3d5552a` | Helpers, ficha pública, galería, mapa, acciones, panel y datos operativos. |
| `a73cdfb` | Fix HU-10: plantilla de catálogo y navegación distinta entre desarrollo y producción. |
| `1a8a827` … `e1f322d` | Documentación, GPS, trazabilidad, cierre y pendientes para retomar. |
| `cebd44f` | Ajuste visual mínimo del mapa. |

## 3. Qué está implementado y dónde

### Ficha pública — HU-11 / URB-14

- `frontend/app/properties/[id]/page.tsx`: distribución de ficha, precio, características principales, descripción, mapa y similares.
- `frontend/components/PropertyGallery.tsx`: galería de ficha; imagen principal completa dentro de su marco, miniaturas, navegación por teclado/gesto y collage al pulsar una imagen. El collage conserva la proporción natural de cada foto.
- `frontend/components/PropertyActions.tsx`: acciones iniciales junto a la información y barra inferior solo después de que dichas acciones ya no estén visibles. Se oculta con diálogos abiertos y en pantallas muy bajas.
- `frontend/components/PropertyLocationMap.tsx`: Leaflet con mosaicos OSM, punto de la propiedad, carga diferida, zoom abajo a la derecha y enlace a Google Maps. CARTO fue retirado: no hay clave ni selector de CARTO usados por el código actual.
- `frontend/components/PropertyCard.tsx`: toda la tarjeta abre la ficha; en desarrollo navega en la misma pestaña y en producción abre una nueva. Esto evita acumular pestañas al probar, pero la restauración de sesión al abrir otra pestaña de producción sigue fuera de alcance.
- `frontend/lib/propertyDetail.ts` y su prueba: características aplicables, similares, coordenadas y validación de celular ecuatoriano.

### Operación, datos demo e imágenes

- `Property.operation_type` distingue `venta` y `arriendo`; la interfaz muestra **Comprar** / **Alquilar** según el contexto.
- La migración `backend/apps/users/migrations/0010_property_operation_type.py` ya está versionada. No editarla.
- Los terrenos no conservan habitaciones ni baños; los comparables separan venta de arriendo.
- La SQLite local contiene siete propiedades demo y tres usuarios según el corte anterior. Es un dato local: nunca se commitea y cada entorno puede requerir sus propios datos.
- Fotos públicas: proveedor local o Cloudinary configurable; se guarda una referencia, se construye la URL con transformaciones y se intenta limpiar el archivo remoto/local al borrarlo. Los documentos privados permanecen en almacenamiento local privado.

### Catálogo y portada — fixes HU-10 / URB-16

- `frontend/components/HomeSearch.tsx` (nuevo, sin seguimiento todavía): buscador inicial con operación opcional, tipo y ubicación; usa GET y puede limpiar la búsqueda.
- `frontend/app/page.tsx`: elimina el CTA duplicado al portal de asesores y usa el buscador.
- `frontend/app/properties/page.tsx`, `frontend/components/CatalogFilters.tsx` y `frontend/lib/catalogFilters.ts`: catálogo directo sin operación obligatoria, filtro **Comprar o alquilar**, filtro de tipo, chips eliminables, limpieza por panel y compatibilidad automática para terrenos.
- Precio, habitaciones/baños, tipo y más filtros se resaltan en azul cuando hay un filtro aplicado; el borrador no altera la URL hasta pulsar Filtrar.
- Tarjetas más compactas, con título/dirección hasta dos líneas y sin leyenda repetida de precio; alquiler conserva `/mes`.

### Contacto, visita y WhatsApp — fixes HU-15/16/19/20

- `frontend/components/WhatsAppContactButton.tsx`: enseña carga, ausencia de número o error/reintento en vez de desaparecer sin explicación.
- El enlace `wa.me` solo aparece si el asesor asignado, activo, tiene celular ecuatoriano válido. En los siete datos demo comprobados anteriormente, el asesor no tenía teléfono; se debe registrar uno desde administración para probar el enlace real.
- `InterestForm.tsx` y `VisitRequestForm.tsx`: la ayuda del celular aparece solo tras un error al salir del campo o enviar. Acepta `09XXXXXXXX` y `+5939XXXXXXXX`, con separadores permitidos.
- El checkbox de novedades se retiró por solicitud de Sebas; `InterestForm` manda `email_opt_in=false`. El correo sigue opcional y llega como dato visible para el asesor en la oportunidad, pero **no existe confirmación automática por correo** para el formulario de interés.

### Mapa y estadísticas operativas

- `backend/apps/telemetry/`: agrega conteo diario de cargas del mapa y endpoints de telemetría/estadísticas. La tabla no guarda IP, identificador de propiedad ni datos personales; el throttle usa IP temporalmente en caché.
- `/dashboard/dev` es una pantalla solo para administrador con métricas de mapas, fotos y documentos. Es orientativa: no equivale a facturación de proveedores ni visitantes únicos.
- No hay mapa del catálogo ni conmutación automática Google/Leaflet. Eso requeriría alcance aparte.

### Plantilla visual de vistas

- `frontend/components/PageLayout.tsx` y `docs/handoff/PLANTILLA_VISTA.md`: espaciado superior común, ancho y encabezado reutilizables.
- Catálogo, panel, oportunidades, disponibilidad y agenda la usan. Disponibilidad y agenda se corrigieron a ancho estándar.

## 4. Cambios locales que faltan guardar

No están en GitHub. El estado observado con `git status --short --branch` fue:

```text
M  Project_Progress.md
M  docs/handoff/URBANEX_AVANCE_EPICAS.md
M  docs/handoff/URBANEX_DEUDA_TECNICA.md
M  docs/handoff/URBANEX_ESTADO_PROCESOS.md
M  docs/handoff/URBANEX_ESTANDARES_DOD.md
M  docs/handoff/URBANEX_GPS_ARCHIVOS.md
M  docs/handoff/URBANEX_SEGURIDAD_Y_DEUDA.md
M  docs/handoff/URBANEX_USM_TRAZABILIDAD.md
M  frontend/app/page.tsx
M  frontend/app/properties/[id]/page.tsx
M  frontend/app/properties/page.tsx
M  frontend/components/CatalogFilters.tsx
M  frontend/components/InterestForm.tsx
M  frontend/components/PropertyCard.tsx
M  frontend/components/VisitRequestForm.tsx
M  frontend/components/WhatsAppContactButton.tsx
M  frontend/lib/catalogFilters.test.mjs
M  frontend/lib/catalogFilters.ts
M  frontend/lib/propertyDetail.test.mjs
M  frontend/lib/propertyDetail.ts
?? frontend/components/HomeSearch.tsx
```

Además, esta nota y la nueva entrada de cierre en `Project_Progress.md` quedan locales hasta que Sebas autorice commits.

### Orden recomendado de commits

Confirmar primero cada grupo visualmente. Luego, solo con autorización expresa de Sebas, preparar cada grupo con `git add -- <rutas>` y mostrar `git diff --cached --name-only` antes del commit.

1. `style(URB-14): mejora contraste y espaciado de la ficha`
   - `frontend/app/properties/[id]/page.tsx`.
2. `feat(URB-16): agrega buscador inicial y filtros compatibles`
   - `HomeSearch.tsx`, `app/page.tsx`, `app/properties/page.tsx`, `CatalogFilters.tsx`, `catalogFilters.ts`, `catalogFilters.test.mjs`, `PropertyCard.tsx`.
3. `fix(URB-21): aclara WhatsApp y valida celular al ingresar`
   - `InterestForm.tsx`, `VisitRequestForm.tsx`, `WhatsAppContactButton.tsx`, `propertyDetail.ts`, `propertyDetail.test.mjs`.
4. `docs(URB-14): registra continuidad y pruebas pendientes`
   - Los documentos modificados de `docs/handoff/`, `Project_Progress.md` y este archivo.

Revisar antes de usar esos mensajes: un mismo grupo contiene fixes de varias HU. Si Sebas prefiere separar por HU, dividirlo sin cambiar el contenido ni usar `git add .`/`git add -A`.

## 5. Pruebas: qué ya se verificó y qué falta

### Resultados técnicos disponibles

| Comprobación | Resultado | Alcance/observación |
| --- | --- | --- |
| `npm test` | 55/55 OK el 2026-11-20 | Cubre helpers de filtros, ficha, teléfono, metadata y otros módulos frontend. |
| `git diff --check` | Sin errores; advertencias CRLF | No son errores de contenido. |
| Última suite backend registrada | 406 OK en SQLite, 2026-11-18 | No se repitió con resultado comprobable el 2026-11-20. |
| Último `makemigrations --check --dry-run` registrado | Sin cambios, 2026-11-18 | Debe repetirse antes de commit/PR. |
| TypeScript y ESLint | Últimos resultados registrados: exit 0 | Deben repetirse antes de commit/PR por los cambios locales. |
| `npm run build` hoy | Falló por conexión a Google Fonts | Next no pudo obtener Geist/Geist Mono; no se atribuye al código funcional. Reintentar con red disponible antes de PR. |
| PostgreSQL | No ejecutado | DT-68; obligatorio para cierre de lote/entrega, no contra Supabase. |

### Validación humana pendiente

Ninguna de estas validaciones está aprobada por el agente:

- Ficha en escritorio y móvil: galería, collage, navegación, estado, precio, cuadro de características, mapa y similares.
- Barra inferior: aparece solo al salir de pantalla las acciones iniciales; no tapa contenido, teclado, diálogo ni área segura del teléfono.
- Catálogo: buscador de portada sin operación obligatoria, filtros aplicados en azul, limpiar/cancelar/aplicar, terrenos sin habitaciones/baños y diseño sin overflow móvil.
- Enlace de tarjetas: misma pestaña en desarrollo y nueva pestaña en producción.
- WhatsApp: registrar un celular válido para un asesor demo, abrir Contactar agente y confirmar que el enlace real aparece; probar también ausencia/error.
- Formularios: celular inválido/missing/corregido, correo opcional, consentimiento LOPDP, envío de interés y solicitud de visita reales en un entorno permitido.
- Mapa: carga, controles, marcador, atribución, enlace externo y contador en `/dashboard/dev` con sesión administradora.
- Plantilla visual: espacios/anchos de catálogo, panel, oportunidades, disponibilidad y agenda en escritorio/móvil.

Las seis capturas antiguas de `evidence/HU11-ux/` no cubren necesariamente la interfaz final. Generar nueva evidencia solo al realizar cada validación visual, sin versionarla.

## 6. Decisiones y pendientes de producto

| Tema | Estado actual | Decisión necesaria para continuar |
| --- | --- | --- |
| Correo de interés | Opcional; el asesor lo ve en la oportunidad; no se envía confirmación automática. | Decidir si se crea una HU/fix transaccional para confirmar recepción por email. |
| Novedades por correo | Checkbox retirado y se manda `email_opt_in=false`. RF-03 histórico contemplaba opt-in. | Confirmar si esta retirada cambia formalmente el requisito de RF-03/DS-50 y documentarlo. |
| WhatsApp demo | No se mostró porque los asesores demo no tenían celular válido. | Sebas debe registrar un teléfono laboral de prueba desde el panel; no inventar uno en código. |
| Sesión en pestaña nueva | Desarrollo evita nuevas pestañas; producción las conserva. No se restaura sesión en una pestaña nueva. | Definir alcance separado para bootstrap seguro con refresh cookie; no mover tokens a `localStorage`. |
| Mapa de catálogo | No implementado. | Requiere una nueva ampliación de HU-10/URB-16 y decisión de UX/coste. |
| Costo de proveedores | Estadísticas son inventario/telemetría orientativa, no contabilidad de Cloudinary/mapas/correo. | Si se necesita control real, definir proveedor, métrica oficial, umbrales y responsables. |
| Criterios literales del Anexo 2 | POR CONFIRMAR. | Resolver antes de declarar HU-11 Lista o contabilizar puntos. |

## 7. Ruta hacia el futuro PR

1. Sebas revisa las validaciones visuales prioritarias y decide los pendientes de producto.
2. Repetir pruebas técnicas completas: suite backend, `makemigrations --check --dry-run`, `npm test`, TypeScript, ESLint, build con red y `git diff --check`.
3. Actualizar documentos con resultados reales, sin marcar validación humana como aprobada si Sebas no la registra con fecha, hora y evidencia.
4. Con autorización expresa, crear commits pequeños por el orden acordado y hacer push de la rama.
5. Antes del PR: `git pull origin develop`, resolver conflictos, repetir comprobaciones pertinentes y ejecutar la auditoría de solo lectura indicada en `AGENTS.md` §11.
6. Sebas abre el PR. No fusionar ni abrir PR automáticamente.

## 8. Límites de seguridad y datos

- No copiar ni pedir claves de Cloudinary, mapas, correo o bases de datos. La configuración local/producción se mantiene fuera de Git.
- La base SQLite, imágenes locales y documentos privados no se incluyen en commits.
- Las migraciones `users.0010` y `telemetry.0001` no se editan; no ejecutar migraciones contra Supabase desde esta rama.
- La telemetría no debe presentarse como medición de factura ni de usuarios únicos.

