# Urbanex — Progreso

---

## ⚠️ DIRECTIVA DE CONTINUIDAD (GPS) — Regla estricta y obligatoria

> **La carpeta `docs/handoff/` es el ecosistema central de navegación del proyecto y la única fuente de verdad.**
> Ningún desarrollador ni asistente de IA debe escribir código, implementar una HU, alterar modelos compartidos ni modificar flujos de negocio **sin antes consultar obligatoriamente** estos tres documentos:
>
> 1. [`URBANEX_ESTADO_PROCESOS.md`](docs/handoff/URBANEX_ESTADO_PROCESOS.md): qué hace hoy cada HU frente al proceso real de la inmobiliaria.
> 2. [`URBANEX_DEUDA_TECNICA.md`](docs/handoff/URBANEX_DEUDA_TECNICA.md): riesgos abiertos (P0 primero), decisiones pendientes que **no se inventan** y decisiones ya tomadas que **no se rediscuten**.
> 3. [`URBANEX_GPS_ARCHIVOS.md`](docs/handoff/URBANEX_GPS_ARCHIVOS.md): qué archivo implementa qué HU, su riesgo y qué coordinar antes de tocarlo.

### Por qué existe
Urbanex debe reflejar los **procesos de la inmobiliaria** (captación → expediente + avalúo → publicación → …), no solo un CRUD. Cada vez que se programó sin mirar el handoff aparecieron fallas de proceso: catálogo con fichas internas (DT-07), publicación sin requisitos (DT-08). Esta directiva evita perder el hilo entre sesiones, entre personas y entre asistentes de IA.

### Protocolo de inicio (cada sesión, antes de cualquier cambio)
1. `git status --short --branch` y `git pull`: confirmar rama y cambios ajenos. Si el pull trae migraciones nuevas, ejecutar `pipenv run python manage.py migrate` (`showmigrations` para verificar).
2. Leer este archivo completo (sobre todo **Próxima tarea**).
3. Leer **Estado de procesos** → la HU objetivo y sus criterios.
4. Leer **Deuda técnica** → P0/P1 que afecten a la HU; decisiones `D-xx`/`N-xx`/`C-xx` pendientes y `DS-xx` tomadas.
5. Leer **GPS de archivos** → archivos implicados, riesgo y si son compartidos.
6. Ejecutar la línea base de pruebas (desde `backend/`) y anotar el resultado:
   `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → hoy **52 OK**. Si la sesión toca el frontend, también `npx tsc --noEmit -p .` (desde `frontend/`).

### Reglas
- **No inventar decisiones pendientes** (D-04 fórmula del motor, C-02, N-02, N-03, etc.). Si una HU depende de una, se usa un placeholder documentado y se pregunta.
- **Si el código y el handoff se contradicen, se detiene el trabajo** y se pregunta al responsable; se corrige el que esté mal y se registra.
- **Archivos compartidos** (`backend/apps/users/models.py`, `users/migrations/`, `backend/config/settings.py`, `frontend/types/property.ts`, `frontend/app/dashboard/page.tsx`): avisar antes de tocarlos (GPS §3).
- **Las transiciones de estado no son un PATCH genérico**: cada una es una acción explícita con sus precondiciones verificadas en el servidor (contexto maestro §11).
- **Un cambio no está terminado** hasta que, en el mismo PR/commit, se actualicen Estado de procesos, Deuda técnica, GPS, Avance de épicas y este archivo, con evidencia (comando + resultado).
- Estándares de código y checklist DoD: [`URBANEX_ESTANDARES_DOD.md`](docs/handoff/URBANEX_ESTANDARES_DOD.md). Requisitos: [`URBANEX_MASTER_CONTEXT.md`](docs/handoff/URBANEX_MASTER_CONTEXT.md) (la copia de `docs/handoff/` es la de referencia).

---

## Estado actual (2026-10-25)

- **Sprint según el backlog definitivo:** EP-2, Sprint 2 (URB-13 / HU-08, pantalla I-12) para desbloquear HU-53 (DT-40).
- **Rama:** `feat/URB-13-HU-08-pantalla-avaluo`, creada desde `feat/URB-15-HU-53-proceso-publicacion` (commit `4b9e52b`) por decisión de Pablo (**DS-09**), porque `develop` aún no tiene `apps.appraisals`. **Subida a `origin` el 2026-10-25** (`git push -u`, con las fases 1 y 2, antes de empezar la fase 3). PR sin abrir. Orden de integración: primero la PR de URB-15 y después la de URB-13.
- **Línea base al iniciar:** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **52/52 OK**; `npx tsc --noEmit -p .` → exit 0.

### Terminado en la sesión 2026-10-25

| Commit | Fase | Cambio | Evidencia |
|---|---|---|---|
| `161f845` | 1 | `frontend/types/appraisal.ts` (contrato de `Appraisal` y del 400 de publicar) + `authFetch`/`ApiError` en `frontend/lib/api.ts` (FX-12) | `tsc` exit 0; `eslint` sobre los 2 archivos exit 0; backend 52/52 OK |
| `af9b416` | 2 | Pantalla **I-12** en `/dashboard/properties/[id]/appraisal` (FX-13): "Iniciar avalúo" explícito, "Precio actual de publicación" gris deshabilitado, tarjeta del motor sin valor sugerido, calibración (PATCH), aprobación con confirmación, solo lectura, reevaluación e historial. `dashboard/page.tsx` **sin tocar** | `tsc` exit 0; `eslint` sobre la página exit 0; `npx next build` exit 0 con `ƒ /dashboard/properties/[id]/appraisal`; backend 52/52 OK |
| `4c9b699` | — | Handoff tras las fases 1 y 2: Deuda técnica, GPS, Estado de procesos, Avance de épicas, Guía, Estándares, Auditoría y este archivo | — |
| `3783919` | 3 | `dashboard/page.tsx` (archivo compartido, commit propio, FX-14): botón "Avalúo" hacia I-12; fila "Avalúo aprobado" del Expediente con datos reales; `missing_requirements` como lista sobre la tabla (con "Ir al avalúo"); "Publicar" solo en `captacion` (DT-46); clave `reservador` (DT-47) | `tsc` exit 0; `eslint` solo con el error previo de DT-24 (también presente en `HEAD`); `next build` exit 0; backend 52/52 OK |
| (este commit) | — | Handoff tras la fase 3 | — |

- **No ejecutado:** validación visual ni prueba en el navegador; los servidores no estaban levantados durante la sesión (`localhost:3000` y `127.0.0.1:8000` sin respuesta, comprobado antes de la fase 2 y después de la fase 3).
- **Sin migraciones ni cambios de backend** en esta sesión.

### Decisiones aprobadas por Pablo (detalle en Deuda técnica §4)
- **DS-09** Rama apilada sobre URB-15 (excepción a "ramas desde `develop`").
- **DS-10** Ruta `/dashboard/properties/[id]/appraisal`: el avalúo pertenece a la propiedad.
- **DS-11** Botón explícito "Iniciar avalúo" (crea un registro con folio que no se borra).
- **DS-12** "Precio actual de publicación" visible como referencia en un campo gris deshabilitado, para no confundirlo con el motor (D-04).
- **DS-13** Página nueva (fase 2) y archivo compartido (fase 3) en commits separados; la fase 3 va después de la fase 2.
- Corrección de Pablo registrada en Estándares §3: en Client Components `useParams()` devuelve el objeto directamente, sin `await`.

### Hallazgos nuevos registrados en Deuda técnica
- **DT-45 (P2):** `frontend/CLAUDE.md` apunta a `@AGENTS.md`, que se eliminó: la IA del frontend no recibe instrucciones.
- **DT-46 (P2):** el dashboard mostraba "Publicar" en estados que el servidor rechaza con 409. **Resuelto en la fase 3.**
- **DT-47 (P3):** `STATUS_LABELS` del dashboard usaba `reservado`; el backend guarda `reservador`. **Resuelto en la fase 3.**
- **DT-50 (P3, fase 3):** los enlaces "Abrir avalúo" / "Ir al avalúo" salen de la página y descartan los cambios sin guardar del modal.
- **DT-48 (P3):** I-12 muestra "Iniciar avalúo" aunque la propiedad no sea tuya (el servidor responde 400; no hay fuga de datos).
- **DT-49 (P3):** en PowerShell 5.1, `git commit -m` con comillas dobles falla; usar `git commit -F`.
- Actualizados: **DT-23** (el build confirma que se usa `next.config.mjs`; el `.ts` está vacío), **DT-26** y **DT-22** (en parte resueltos con `authFetch`), **DT-37** (I-12 sin pruebas automáticas), **DT-40** (fases 1 y 2 hechas).

### Validaciones pendientes (requieren a una persona)
Pablo confirmó el 2026-10-25 que **todavía no ha hecho** ninguna de las validaciones visuales de la sesión anterior. Valida I-12 y el dashboard en paralelo.
- [ ] **I-12:** como asesor dueño, entrar con el botón "Avalúo" del dashboard y seguir los 6 pasos de [Estado de procesos → HU-08](docs/handoff/URBANEX_ESTADO_PROCESOS.md#hu-08).
- [ ] Sin sesión, `/properties` no muestra una propiedad recién creada y `/properties/<id>` no la abre.
- [ ] En el dashboard, "Publicar" sobre una propiedad sin requisitos muestra la lista de lo que falta (fase 3).
- [ ] "Publicar" no aparece en propiedades que no están en captación (DT-46).
- [ ] Con avalúo aprobado en I-12 + foto + corretaje, "Publicar" funciona y la propiedad aparece en el catálogo público (cierra DT-40). Pasos en [Estado de procesos → HU-53](docs/handoff/URBANEX_ESTADO_PROCESOS.md#hu-53).

### Próxima tarea
1. ~~Fase 3 de DT-40~~ Hecha el 2026-10-25 (`3783919`).
2. Registrar el resultado de las validaciones de Pablo (quién, cuándo, qué se vio) y, si pasan, cerrar DT-40 y marcar como validados los criterios de HU-08 y HU-53 en Avance de épicas.
3. Abrir las PR en orden: URB-15 → `develop` y después URB-13 (DS-09). Tras fusionar, cada copia ejecuta `migrate`. **Avisar a Sebas** de que la fase 3 modificó `dashboard/page.tsx`.
4. Decidir DT-45 (qué hacer con `frontend/CLAUDE.md`) y DT-23 (borrar `next.config.ts`).
5. Resolver DT-39 junto con C-08.

---

## Sesión anterior (2026-10-24)

- **Sprint según el backlog definitivo:** trabajo de EP-2 que adelanta el Sprint 2 (HU-08) y el Sprint 3 (HU-53).
- **Rama:** `feat/URB-15-HU-53-proceso-publicacion` (desde `develop`; **subida a `origin` el 2026-10-24, PR todavía sin abrir**).
- **Historias trabajadas en la sesión:**
  - URB-05 / HU-01: cierre de **DT-07** (catálogo público).
  - URB-13 / HU-08: **modelo base inmutable** de avalúos (sin motor, D-04).
  - URB-15 / HU-53: **bloqueo de publicación** sin requisitos (cierre de DT-08).

### Terminado en la sesión 2026-10-24

| Commit | Cambio | Evidencia |
|---|---|---|
| `2817dcd` | **DT-07:** un anónimo solo ve `disponible`/`reservador` en la lista; el detalle de una ficha en captación responde 404. El dueño y el admin siguen viéndola | 3 pruebas nuevas en `apps.users.tests` |
| `58b968c` | **HU-08:** app `apps.appraisals` con `Appraisal` (§7 + `status` BORRADOR→APROBADO + `approved_at`), inmutabilidad idéntica a `Document`, 3 restricciones de BD, placeholder manual (`# TODO: Implementar motor de cálculo HITL`), API `/api/appraisals/` (list, retrieve, create, PATCH de calibración, `approve/`; sin PUT ni DELETE), admin de solo lectura | 18 pruebas en `apps.appraisals.tests`; `makemigrations --check` sin cambios |
| `cca371e` | **HU-53:** `PropertyPublishView` solo publica desde `captacion` (409 en otro caso) y responde 400 con `missing_requirements` si falta foto, `CORRETAJE` vigente no rechazado o avalúo `APROBADO`; todo en transacción con `select_for_update` | `test_publish_property_permission` reescrita + 7 pruebas de rechazo |
| `d33b698` | Handoff actualizado: Estado de procesos, Deuda técnica, GPS, Avance de épicas, Guía de continuidad, DoD (comando de pruebas) y esta directiva | — |
| (commit de DT-09, ver `git log`) | **DT-09 (P0) resuelto (FX-11):** `status` en `read_only_fields` de `PropertySerializer`; `POST` crea siempre en `captacion` y `PATCH` ignora `status`. `PropertyPublishView` queda como única vía hacia `disponible` | `test_patch_cannot_change_status`, `test_create_ignores_status`; 52/52 OK |

### Pruebas ejecutadas y resultado
- `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **52/52 OK** (15 users + 19 documents + 18 appraisals), tras cerrar DT-09.
- Línea base al iniciar la sesión: `apps.users.tests apps.documents.tests` → 22/22 OK.
- `pipenv run python manage.py makemigrations --check --dry-run` → sin cambios.
- **No ejecutado:** validación visual en el navegador de ninguno de los tres cambios (pendiente; ver abajo).

### Migraciones / endpoints nuevos
- Migración `appraisals/0001_initial`. **Aplicada en la BD local de Pablo el 2026-10-24** (`showmigrations appraisals` → `[X] 0001_initial`). Su `db.sqlite3` cambió pero **no se sube** (DT-02). ⚠️ **Para el próximo desarrollo:** quien haga pull de esta rama (Sebas incluido) debe ejecutar `pipenv run python manage.py migrate` antes de levantar el servidor, o `/api/appraisals/` y la publicación fallarán con `no such table: appraisals_appraisal` (DT-43).
- `GET/POST /api/appraisals/`, `GET/PATCH /api/appraisals/<uuid>/`, `POST /api/appraisals/<uuid>/approve/`.
- Cambio de contrato: `POST /api/auth/properties/<id>/publish/` ahora puede responder **400** `{detail, missing_requirements[{code, message}]}` o **409** (no está en captación).
- Archivos compartidos tocados: `backend/config/settings.py` (`INSTALLED_APPS`) y `backend/config/urls.py`, una línea cada uno. **Avisar a Sebas.**

### Decisiones aprobadas en la sesión (detalle en Deuda técnica §4)
- **DS-01** `Appraisal` con ciclo BORRADOR → APROBADO; aprobado = inmutable.
- **DS-02** Sin motor (D-04): `suggested_value = NULL`, `is_manual_fallback = True`, confianza `BAJO`. Nunca un valor ficticio.
- **DS-03** Todos los campos del §7 creados ya.
- **DS-04** Corretaje válido para publicar = versión vigente, no vencida y no `RECHAZADO` (`PENDIENTE` sí sirve). **Cierra N-01.**
- **DS-05** Avalúo: lo crean, calibran y aprueban el asesor dueño o el admin.
- **DS-06** Se permiten avalúos nuevos sobre propiedades publicadas (reevaluación); un solo borrador abierto por propiedad.
- **DS-07** Publicar es solo `captacion → disponible`.
- **DS-08** El filtro público usa `'reservador'` (errata DT-16) sin tocar `models.py`.

### Hallazgos nuevos registrados en Deuda técnica
- ~~**DT-09 subió a P0**~~ **Resuelto el mismo día (FX-11).** Efecto colateral registrado: HU-09 (retirar con motivo) ya no puede hacerse por PATCH y necesitará su propia acción; reglas de `status` en `validate()` quedan latentes (DT-44).
- **DT-39 (P1):** un usuario autenticado con rol `cliente` todavía ve propiedades en captación.
- **DT-40 (P1):** **bloqueo funcional esperado de HU-53**: sin pantallas I-11/I-12 un avalúo solo se aprueba por la API, así que hoy **no se puede publicar desde la interfaz**. Es el comportamiento correcto del proceso.
- **DT-41:** el comando de pruebas ahora incluye `apps.appraisals.tests`.
- **DT-42:** formato del `folio` POR CONFIRMAR. **DT-43:** migración aplicada en la copia de Pablo; las demás copias deben ejecutar `migrate`.

### Validaciones pendientes (requieren a una persona)
- [ ] Sin sesión, `/properties` no muestra una propiedad recién creada y `/properties/<id>` no la abre.
- [ ] En el dashboard, "Publicar" sobre una propiedad sin requisitos muestra el mensaje con lo que falta.
- [ ] Con avalúo aprobado por la API + foto + corretaje, "Publicar" funciona y la propiedad aparece en el catálogo público.

### Bloqueos
- **D-04** (fórmula del motor) sigue abierta: bloquea HU-06 y el cálculo de HU-08.
- HU-53 y HU-01 ya no tienen bloqueos técnicos de backend; falta validación en la UI (DT-40) y DT-39.

### Próxima tarea (de esa sesión; la vigente está en "Estado actual")
1. **Abrir el PR** de `feat/URB-15-HU-53-proceso-publicacion` (ya en `origin`) hacia `develop`, revisarlo y fusionarlo con autorización del responsable de integración. Tras fusionar, cada copia ejecuta `migrate`.
2. ~~Cerrar DT-09 (P0)~~ Hecho el 2026-10-24 (FX-11).
3. **Pantalla I-12** (calibrar y aprobar avalúo) + `frontend/types/appraisal.ts` en una ruta nueva; conectar la fila "Avalúo aprobado" del Expediente y mostrar `missing_requirements` al publicar (DT-40).
4. Resolver DT-39 junto con C-08 (¿se mantiene el rol `cliente`?).

---

## Historial

### Sesión anterior (registro hasta 2026-10-22)
- **Sprint:** Sprint 1
- **Historias:** URB-04 / HU-46 (sesión en cliente), URB-05 / HU-01 (registrar propiedad en captación), URB-08 / HU-05 (características y ubicación exacta).
- **Rama:** `develop` (fusionado y respaldado en `test`).
- **Terminado:**
  - Aislamiento de sesiones en el frontend con `sessionStorage` para token, email y rol (`HU-46`).
  - Identificador visual de sesión global en el `RootLayout` (`SiteNav`) y en el Dashboard.
  - Modal inteligente (detecta si usar `POST` para crear o `PATCH` para editar).
  - Carga de imágenes vinculadas al ID de la propiedad (`HU-01`).
  - Mapas interactivos con `Leaflet` (OpenStreetMap) para capturar `latitude` y `longitude` sin APIs de pago (`HU-05`).
  - Modal en 4 viñetas (Datos generales, Ubicación, Multimedia, Expediente) con validación por viñeta y previsualización de fotos (`HU-01`, `HU-05`).
  - Buscador de sectores con Nominatim + `flyTo` (`HU-05`).
  - Corrección: `Property` no tenía `latitude`/`longitude`. Agregado `terreno` a los tipos.
  - Modelo `apps.documents.Document` con versionado inmutable, sin borrado, 20 MB/PDF-imagen y validación solo Admin (`HU-03` modelo, `HU-37` regla).
  - API `/api/documents/` conectada a la viñeta Expediente (`URB-07 / HU-03`). Validación visual pendiente.
- **Pruebas de entonces:** pruebas manuales de UI en el Dashboard; corrección del error de hidratación al anidar el mapa; `ssr: false` para el mapa; manejo visual del 401; `apps.documents.tests` 19/19 OK; `apps.users.tests` con 4 errores preexistentes (corregidos después: FX-02).
- **Migraciones de entonces:** `users/0006` (latitude, longitude, terreno) y `documents/0001_initial`.
- **Decisiones aprobadas:** Leaflet en lugar de Google Maps (costos); nombres de campos en inglés (`latitude`, `longitude`) para alinear JSON y modelo.
