# Urbanex — Deuda técnica, riesgos y decisiones pendientes

| Campo | Valor |
|---|---|
| Propósito | Conservar los problemas que el equipo debe conocer antes de seguir, con evidencia y criterio de cierre |
| Fecha de auditoría | 2026-10-22 · rama `develop` con cambios sin commit |
| Alcance | Configuración, pruebas, seguridad, consistencia de datos y todo lo que afecte a HU-01, 03, 05, 37, 44–46 y Avalúos |

Estados: **Confirmado** (comprobado por comando o lectura directa de código) · **Potencial** (deducido del código, no reproducido) · **POR CONFIRMAR**.
Prioridad: **P0** bloquea el proceso de negocio o la entrega · **P1** riesgo alto de seguridad o regresión · **P2** calidad o mantenibilidad · **P3** menor.

Referencias: [Auditoría de código](URBANEX_AUDITORIA_CODIGO.md) · [GPS](URBANEX_GPS_ARCHIVOS.md) · [Estado de procesos](URBANEX_ESTADO_PROCESOS.md).

---

## 1. Correcciones confirmadas (sesión de desarrollo 2026-10-21/22, sin commit)

| ID | Corrección | Evidencia | Estado real |
|---|---|---|---|
| FX-01 | `Property` no tenía `latitude`/`longitude`; las coordenadas del mapa se perdían. Se agregaron los campos y el tipo `terreno` | `backend/apps/users/migrations/0006_…py` aplicada; `showmigrations` | Corregido. **Falta validar** que la UI guarde coordenadas reales (la BD tiene 0 propiedades con coordenadas) |
| FX-02 | Pruebas de `apps.users` fallaban (`create_user()` sin `username`; la prueba de login esperaba 400 y la vista responde 401) | `manage.py test apps.users.tests` → 3/3 | Corregido. Se ajustó la **expectativa de la prueba**, no el código; ahora también verifica `failed_attempts` |
| FX-03 | Faltaba `frontend/types/property.ts` (3 archivos fallaban en `tsc`) | `npx tsc --noEmit` exit 0; `next build` OK | Corregido. El dashboard usa el tipo compartido |
| FX-04 | La primera línea de `.gitignore` era una cadena literal con `\n`, así que no ignoraba nada | `git check-ignore -v` sobre `__pycache__`, `private_media`, `media`, `.env.example` | Corregido parcialmente; ver DT-02 |
| FX-05 | Error 500 `no such column: users_property.latitude` | El usuario confirmó que "ya hace fetch" tras `migrate` | Corregido |
| FX-06 | Faltaba el endpoint de documentos | 19/19 pruebas de `apps.documents` | Implementado; validación visual pendiente |

---

## 2. Hallazgos abiertos

### P0 — Bloquean el proceso de negocio o la entrega

| ID | Hallazgo y evidencia | Estado | Impacto | Módulos | Acción recomendada | Criterio de cierre | Riesgo de regresión |
|---|---|---|---|---|---|---|---|
| DT-07 | **El catálogo público muestra propiedades en captación.** `PropertyListCreateView.queryset = Property.objects.all()` con `IsAuthenticatedOrReadOnly`; `PropertyDetailView` permite leer cualquier `id`. Ruta: `backend/apps/users/views.py` | Confirmado (código) | Incumple HU-01 y RF-01; expone fichas internas | Catálogo, ficha pública | Vistas públicas filtradas a `disponible` y `reservado` (no `reservador`, DT-16); listas internas aparte | Prueba: un anónimo no ve una propiedad `captacion` ni en lista ni en detalle | Medio: el catálogo quedará vacío si no hay publicadas |
| DT-08 | **Publicar no valida requisitos.** `PropertyPublishView` solo comprueba permisos; `test_publish_property_permission` publica sin avalúo, sin corretaje y sin foto | Confirmado | Incumple HU-53 y RF-01 | Propiedades, Avalúos, Documentos | Implementar junto con Avalúos (HU-53, Sprint 3): exigir avalúo aprobado, `Document` vigente `CORRETAJE` y ≥1 imagen, en una transacción | Pruebas de los 3 rechazos + 1 éxito; reescribir la prueba actual | **Alto**: la prueba existente fallará a propósito |
| DT-27 | **Las fuentes de requisitos no viajan con Git.** `URBANEX_MASTER_CONTEXT.md` sin rastrear; `ProyectoCapstoneV4 (3).md` y `Understanding.txt` ignorados en `.gitignore` | Confirmado (`git ls-files`, `git check-ignore`) | Sebas clonaría sin requisitos; los documentos de handoff los citan | Todos | Hacer commit del contexto maestro; decidir si la tesis se versiona o se comparte por otro canal y anotarlo en la guía | Sebas puede abrir ambos documentos desde su copia | Bajo |
| DT-36 | **Todo el trabajo reciente está sin commit** (15 archivos modificados, 13 nuevos) | Confirmado (`git status`) | Riesgo de perderlo; Sebas no lo recibe | Todos | Revisar el diff y hacer commit en `develop` (o en ramas por HU) antes de entregar | `git status` limpio salvo artefactos | Bajo |

### P1 — Seguridad, integridad o bloqueos para Avalúos

| ID | Hallazgo y evidencia | Estado | Impacto | Módulos | Acción recomendada | Criterio de cierre | Riesgo de regresión |
|---|---|---|---|---|---|---|---|
| DT-01 | `TIME_ZONE = 'UTC'` en `backend/config/settings.py:135`; RF y contexto maestro piden `America/Guayaquil` | Confirmado | Fechas de vigencia y alertas a 30 días desfasadas un día por la noche; los futuros avalúos guardarán fechas en UTC | Documentos, Avalúos, Recordatorios | Cambiar a `America/Guayaquil` (con `USE_TZ = True` se mantiene) y ejecutar todas las pruebas | 22/22 + `expiring_soon` coherente a las 23:00 locales | Bajo |
| DT-06 | `manage.py test` sin etiquetas encuentra **0 pruebas**: falta `backend/apps/__init__.py` | Confirmado | Un CI o un compañero creería que todo pasa | Calidad | Agregar `backend/apps/__init__.py` (vacío) y verificar | `manage.py test` encuentra ≥22 | Bajo (verificar los imports `apps.*`) |
| DT-10 | `PropertyImageViewSet`: `queryset = PropertyImage.objects.all()`, solo `IsAuthenticated`; cualquier usuario autenticado puede subir, editar o borrar imágenes de cualquier propiedad | Potencial (código, no reproducido) | Integridad de fichas ajenas | Propiedades | Filtrar el queryset por dueño/admin y validar `property` en la creación | Pruebas 403/404 con otro asesor | Medio |
| DT-09 | `status` escribible por `PATCH /properties/<id>/` (no está en `read_only_fields`) | Confirmado (código) | Se salta HU-53; permite estados inventados | Propiedades | Hacer `status` de solo lectura y crear transiciones explícitas (HU-09, HU-53) | Prueba: un PATCH con `status` se ignora o se rechaza | Medio |
| DT-12 | `LoginView` no comprueba `is_active`; SimpleJWT `for_user` solo advierte | Confirmado (código de la vista y de la librería) | Incumple HU-46 | Auth | Rechazar inactivos antes de emitir el token | Prueba de un inactivo → 401/403 sin token | Bajo |
| DT-13 | `User.email` no es único; el login usa `.first()` | Confirmado | Incumple HU-44; ambigüedad en el login | Auth, Usuarios | Restricción única (migración; revisar duplicados en la BD) | Prueba de duplicado rechazado | Medio (datos existentes) |
| DT-19 | Faltan campos de RF-01 en `Property`: `zone`, `operation_type` (existen choices sin campo), `usable_area_m2`, `age_years`, `conservation_state`, `floor_number`, `storage_units`, `code`, `slug`, `published_at` | Confirmado | **Bloquea HU-04** (segmentar por zona) y condiciona HU-06 | Propiedades, Avalúos, Catálogo | Definir en equipo los campos mínimos para el motor (ligado a D-04); una sola migración coordinada | Campos en modelo, serializer, `types/property.ts` y formulario | **Alto** (app compartida) |
| DT-14 | Rol `cliente` por defecto; los 3 usuarios de desarrollo son `cliente`; crear propiedades no comprueba el rol | Confirmado (código + conteo en BD) | Las reglas por rol no se pueden validar en la UI | Auth, todas | Crear usuarios `asesor`/`admin` de prueba; decidir C-08; comprobar el rol en la creación | Existe al menos 1 asesor y 1 admin de prueba | Bajo |
| DT-11 | `DELETE /properties/<id>/` permitido; si la propiedad tiene documentos, `on_delete=PROTECT` lanza `ProtectedError` → 500 | Potencial (no reproducido) | 500 en producción; RF-01 usa `no_disponible` en lugar de borrar | Propiedades, Documentos | Quitar DELETE (usar `no_disponible`) o capturar `ProtectedError` → 409 | Prueba de DELETE → 405 o 409 | Bajo |
| DT-20 | Configuración: `SECRET_KEY` con respaldo inseguro (`'clave-insegura-de-respaldo'`); `CORS_ALLOWED_CREDENTIALS` mal escrito (sin efecto); `CorsMiddleware` al final; sin `DEFAULT_PERMISSION_CLASSES` | Confirmado | Seguridad en despliegue | Config | Sin respaldo para `SECRET_KEY` en producción; corregir el nombre; mover el middleware antes de `CommonMiddleware`; `IsAuthenticated` por defecto | `manage.py check --deploy` sin errores críticos | Medio (el middleware y los permisos afectan a todas las vistas) |

### P2 — Calidad y mantenibilidad

| ID | Hallazgo y evidencia | Estado | Acción recomendada | Criterio de cierre |
|---|---|---|---|---|
| DT-02 | Ya rastreados pese al `.gitignore`: `backend/db.sqlite3`, 6 `.pyc`, 14 imágenes de `backend/media/`, `.gitignore.swp` | Confirmado | Decisión del equipo: `git rm --cached` (al hacer pull, a Sebas se le borraría su `db.sqlite3` local) + seed o fixtures | `git ls-files` sin esos artefactos |
| DT-15 | `UserAdmin` genérico no muestra `role`, `is_locked` ni `failed_attempts` | Confirmado | Agregar `fieldsets` o, mejor, hacer la pantalla A-01 (HU-44/45) | El admin puede ver y editar el rol y desbloquear |
| DT-16 | Errata de estado `'reservador'` en `Property.STATUS_CHOICES`; `frontend/types/property.ts` la refleja a propósito | Confirmado | Migración de datos a `reservado` antes del Sprint 6 (reserva) | Choices y tipo con `reservado` |
| DT-17 | Un único `agent` hace de captador y de responsable | Confirmado | `captor_agent` (inmutable) + `responsible_agent` antes de HU-28/47 y co-intermediación | Reasignar no cambia el captador |
| DT-18 | `Property` vive en `apps.users`; `apps.users.properties` está registrada y vacía | Confirmado | No mover ahora (implica migraciones complejas); documentado | Decisión registrada |
| DT-21 | No hay `.env.example`, aunque el README lo pide | Confirmado | Crear `backend/.env.example` con `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` sin valores reales, y `frontend/.env.example` con `NEXT_PUBLIC_API_URL` | Arranque desde cero siguiendo el README |
| DT-22 | 6 URLs `http://127.0.0.1:8000` hardcodeadas en `frontend/app/dashboard/page.tsx`; `lib/api.ts` sí usa `NEXT_PUBLIC_API_URL` | Confirmado | Centralizar en `lib/api.ts` | `grep 127.0.0.1` solo en `lib/api.ts` |
| DT-23 | Hay `next.config.mjs` y `next.config.ts`; Next usa el `.mjs` (log del build) | Confirmado | Borrar el que no se usa (decisión del equipo) | Un solo archivo |
| DT-24 | ESLint: 2 errores y 4 warnings (`any` en login, `setState` en `useEffect` del dashboard, `SiteNav` sin usar ×2, `window.location.href` ×2) | Confirmado | Corregirlos en una HU de limpieza | `npx eslint .` sin errores |
| DT-25 | `frontend/app/properties/[id]/page.tsx` renderiza `<SiteNav />` y el layout también: navbar duplicada | Confirmado por código; visual pendiente | Quitar el de la página | Verificación visual |
| DT-28 | Git rastrea `Project_Progress.md`; en disco es `PROJECT_PROGRESS.md` | Confirmado | `git mv` en dos pasos para normalizar | `git ls-files` muestra un solo nombre |
| DT-29 | No hay CI (`.github/` no existe) | Confirmado | GitHub Actions con pruebas de backend, `tsc`, `eslint` y `build` (RNF-05) | Pipeline verde en un PR |
| DT-30 | Documentos en `FileSystemStorage` local (`backend/private_media/`), no en Supabase; la descarga es provisional | Confirmado (diseño) | Migrar en HU-38 (Sprint 6) | URLs firmadas |
| DT-31 | `Document.opportunity` no existe (el modelo de oportunidades aún no existe) | Confirmado (planificado) | Agregar en HU-36 (Sprint 7) con la regla "exactamente uno" | Migración y pruebas |
| DT-33 | Sesión: `access` de 1 día en `sessionStorage`, `refresh` sin uso, sin cierre por inactividad | Confirmado | Resolver la decisión D-05 | Política documentada e implementada |
| DT-34 | "Al menos 1 foto" solo se valida en el frontend | Confirmado | Validarlo en el backend al publicar (DT-08) | Prueba del backend |
| DT-37 | Sin pruebas de frontend ni E2E | Confirmado | Elegir una herramienta (decisión) para los flujos críticos | Al menos un E2E del modal |

### P3 — Menores

| ID | Hallazgo | Estado | Acción |
|---|---|---|---|
| DT-26 | `apiFetch` lanza `Error ${status}` y el login muestra "Error 401" en vez del mensaje del backend | Confirmado | Propagar `detail` |
| DT-32 | Listas sin paginación | Potencial | Paginación de DRF cuando crezca el catálogo |
| DT-35 | Nominatim: 1 petición/s, sin `User-Agent` propio desde el navegador; iconos de Leaflet desde `unpkg.com` | Confirmado (política) | En producción, considerar un proxy en el backend con caché |
| DT-38 | Código comentado y `get_agent_name` duplicado en `backend/apps/users/serializers.py`; `Pipfile` vacío en la raíz | Confirmado | Limpieza |

---

## 3. Decisiones pendientes (no inventar su resultado)

| ID | Decisión | Afecta a | Fuente |
|---|---|---|---|
| D-04 | Fórmula del motor, factores ponderados, umbrales de confianza y comparables iniciales | HU-04, 06, 08, 53 | Contexto maestro §14 |
| D-05 | Almacenamiento, expiración, renovación y revocación de JWT | HU-46 | Contexto maestro §14 |
| D-06 | Mecanismo de tareas programadas, webhooks y reintentos | Sprint 4+ | Contexto maestro §14 |
| C-02 | Con 1–2 comparables: ¿calcular con confianza media o pasar a manual? | HU-04, HU-06 | [Contradicciones](URBANEX_ESTADO_PROCESOS.md#contradicciones-entre-fuentes) |
| N-01 | ¿Un `CORRETAJE` rechazado impide publicar? | HU-53, HU-37 | Pregunta de negocio |
| N-02 | ¿Qué propiedades cuentan como comparables (estados, antigüedad del dato)? | HU-04 | Pregunta de negocio |
| N-03 | ¿`zone` es una lista controlada o se deriva de las coordenadas? | HU-04, HU-05 | Pregunta de negocio |
| N-04 | ¿Se dejan de rastrear `db.sqlite3` y `media/`? ¿Con qué seed se reemplazan? | Equipo | DT-02 |
