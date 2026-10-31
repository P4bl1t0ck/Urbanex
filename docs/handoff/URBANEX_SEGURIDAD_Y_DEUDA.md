# Urbanex — Seguridad, infraestructura y deuda técnica asociada

| Campo | Valor |
|---|---|
| Propósito | Inventario de riesgos de seguridad e infraestructura del código actual, con su plan de corrección, y opciones documentadas para las decisiones pendientes (D-05 sesión/JWT, DT-42 folio, almacenamiento y base de datos) |
| Fecha | 2026-10-27 · rama `docs/DT-42-seguridad-y-deuda`, desde `develop` (`47b59ce`). **Actualizado el 2026-10-28:** SEC-09 (cuentas inutilizadas en la copia de Pablo, DS-24) y propuesta concreta en §5.3. **Actualizado el 2026-10-31:** SEC-15 / DT-79 (incidente de credenciales, sin valores); SEC-09 y §5.3: `db.sqlite3` ya no se versiona (DS-25, FX-22) |
| Método | Lectura del código del backend y del frontend. **No se hicieron pruebas de intrusión.** Lo que no se comprobó en ejecución está marcado **Por verificar** |
| Alcance | Control de acceso · sesión y JWT · validación de entradas y archivos · folio de avalúos · infraestructura y almacenamiento · requisitos previos al despliegue |
| Registro oficial | Cada riesgo tiene su DT en [Deuda técnica](URBANEX_DEUDA_TECNICA.md); el estado se actualiza allí y en la tabla de §0 |

> **🔒 Documento publicable.** El repositorio es **público**. Por eso este documento describe **qué** está en riesgo y **cómo se corregirá**, pero **no** incluye pasos de explotación, peticiones, payloads ni comandos de ataque.
>
> **Los detalles de reproducción se guardan aparte, en privado y fuera del repositorio** (responsable: Pablo). No se escriben aquí, ni en Deuda técnica, ni en los mensajes de commit o de PR.

**Estado de la evidencia:** **Confirmado (código)** = leído en el código actual · **Confirmado (validación)** = visto por una persona en la interfaz · **Por verificar** = deducido del código, sin comprobarlo en ejecución.

**Severidad:** **Alta** = expone datos internos o permite modificar datos ajenos · **Media** = facilita un ataque o filtra información menor · **Baja** = endurecimiento.

---

## ⛔ Regla de despliegue (DS-20)

> **¡NINGÚN DESPLIEGUE, NI SIQUIERA EL DE DEMOSTRACIÓN, SE HACE CON RIESGOS DE SEVERIDAD ALTA ABIERTOS!**
> Antes de desplegar, todas las filas **Alta** de la tabla de §0 deben estar en **Corregido**, con su prueba, y la lista de §6.4 debe estar completa.

---

## 0. Inventario de riesgos

| ID | Categoría | Componente afectado | Severidad | Estado | Plan de corrección | DT |
|---|---|---|---|---|---|---|
| SEC-01 | Control de acceso (BOLA) | Lista y detalle de propiedades (`PropertyListCreateView`, `PropertyDetailView` en `backend/apps/users/views.py`) | **Alta** | Abierto · Confirmado (código) | Regla de visibilidad única por rol (§1.2) + pruebas | [DT-39](URBANEX_DEUDA_TECNICA.md#p1--seguridad-integridad-o-bloqueos-para-avalúos) |
| SEC-02 | Control de acceso (BOLA) | Fotos de propiedades (`PropertyImageViewSet`, `PropertyImageSerializer`) | **Alta** | Abierto · Por verificar | Filtrar por dueño y validar la propiedad al crear, como en documentos (§1.2) | [DT-10](URBANEX_DEUDA_TECNICA.md#p1--seguridad-integridad-o-bloqueos-para-avalúos) |
| SEC-09 | Exposición de datos | `backend/db.sqlite3` versionado en un repositorio público | **Alta** | Abierto · Confirmado. **(2026-10-28)** Cuentas inutilizadas en la copia de Pablo; falta la copia de Sebas. **(2026-10-31) Resuelto en parte (DS-25, FX-22):** `db.sqlite3` ya no se versiona; `media/`, `.pyc` y el historial siguen | Cambiar credenciales, dejar de versionar la BD (§5.3, propuesta concreta) | [DT-65](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-15 | Credenciales | **Incidente de credenciales (2026-10-29):** un integrante compartió por chat su `backend/.env` con credenciales reales de Resend y de la base de datos de Supabase | **Alta** | Abierto · rotación **POR CONFIRMAR** | Rotar ambas credenciales; dar acceso **invitando** a la persona al proyecto, sin compartir claves (`AGENTS.md` §6). Se cierra cuando el dueño de cada servicio confirme la rotación, con fecha | [DT-79](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-07 | Validación de archivos | Subida y publicación de fotos (`PropertyImage.image`, `media/`) | **Alta** | Abierto · Por verificar | Límite de tamaño, formatos permitidos y fotos de captación no públicas (§3.2) | [DT-64](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-10 | Configuración | `backend/config/settings.py` (valores por defecto) | Media (**Alta** al desplegar) | Abierto · Confirmado (código) | Valores seguros por defecto y `check --deploy` (§6.4) | [DT-20](URBANEX_DEUDA_TECNICA.md#p1--seguridad-integridad-o-bloqueos-para-avalúos) |
| SEC-04 | Autenticación | Inicio de sesión (`LoginView`) | Media | Abierto · Confirmado (código) | Respuesta uniforme, bloqueo temporal y límite de peticiones (§2.5) | [DT-62](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-05 | Sesión | Token JWT en el navegador (`frontend/lib/api.ts`, `login/page.tsx`, `SIMPLE_JWT`) | Media | Abierto · Confirmado (código) | Decidir D-05; recomendación en §2.4 | [DT-33](URBANEX_DEUDA_TECNICA.md#p2--calidad-y-mantenibilidad), D-05 |
| SEC-03 | Exposición de datos | Contrato público de propiedades (`PropertySerializer`), ids consecutivos | Media | Abierto · Confirmado (código) | Serializer público sin datos del usuario interno; `slug` en URL públicas (§1.2) | [DT-61](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-06 | Validación de entradas | `PropertySerializer` (números y coordenadas) | Media | Abierto · Por verificar | Validar rangos y longitudes en el servidor (§3.1) | [DT-63](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-11 | Exposición de datos | Creación de documentos y avalúos (`DocumentUploadSerializer`, `AppraisalCreateSerializer`) | Baja | Abierto · Por verificar | Mensajes de error uniformes (§1.2) | [DT-67](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-08 | Validación de archivos | Contenido de los documentos (`DocumentUploadSerializer`) | Baja (mitigada) | Abierto · Confirmado (código) | Análisis de contenido al migrar el almacenamiento (§3.2) | [DT-30](URBANEX_DEUDA_TECNICA.md#p2--calidad-y-mantenibilidad) |
| SEC-12 | Integridad | Folio del avalúo (`generate_folio()` en `backend/apps/appraisals/models.py`) | Baja | Abierto · Confirmado (código + validación) | Formato POR CONFIRMAR (§4) | [DT-42](URBANEX_DEUDA_TECNICA.md#p3--menores), [DT-55](URBANEX_DEUDA_TECNICA.md#p2--calidad-y-mantenibilidad), [DT-66](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| INF-01 | Infraestructura | Base de datos SQLite local | Media (bloquea el despliegue) | Abierto · Confirmado | Migrar a PostgreSQL externo (§5.1) | [DT-68](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| INF-02 | Infraestructura | Archivos en disco local (`media/`, `private_media/`) | Media (bloquea el despliegue) | Abierto · Confirmado | Almacenamiento externo (§5.2) | [DT-69](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| INF-03 | Repositorio | `db.sqlite3` y `media/` versionados | Media | Abierto · Confirmado | Dejar de versionarlos; el seeder los reemplaza (§5.3) | [DT-70](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27), DT-02, N-04 |
| INF-04 | Despliegue | Requisitos previos (entorno, HTTPS, CORS, copias de seguridad) | **Alta** al desplegar | Abierto | Lista de §6.4 completa (servicios confirmados: Vercel + Render + Supabase, DS-19) | [DT-71](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |

**Controles que ya funcionan bien** (no romperlos):
- Documentos y avalúos filtran por dueño, usan UUID y validan la propiedad al crear.
- Publicar comprueba el dueño, y el `status` es de solo lectura.
- Los documentos se validan por su contenido real, tienen un máximo de 20 MB, el servidor genera su nombre, se guardan en almacenamiento privado y se descargan como adjunto.
- No hay SQL crudo: solo se usa el ORM.
- El frontend no inserta HTML sin escapar, así que React escapa todo lo que muestra.

---

## 1. Control de acceso y enumeración de IDs

**Contexto.** OWASP API Security Top 10 (2023), API1 *Broken Object Level Authorization* (BOLA): la API comprueba que el usuario inició sesión, pero no que el objeto le pertenezca. El riesgo crece cuando los identificadores son consecutivos.

### 1.1 Estado por componente (Confirmado por código, 2026-10-27)

| Componente | Control por dueño u objeto | Identificador | Evaluación |
|---|---|---|---|
| Lista y detalle de propiedades | Solo se filtra a los usuarios **anónimos** (`PUBLIC_STATUSES`) | Entero consecutivo | ⚠️ SEC-01 |
| Editar o borrar una propiedad | Dueño o admin (`PropertyOwnerOrAdminOrReadOnly`) | Entero | ✔ (borrar: ver DT-11) |
| "Mis propiedades" | Filtra por el usuario | — | ✔ |
| Publicar | Dueño o admin, en transacción | Entero | ✔ |
| Fotos de propiedades | **Sin** control por dueño | Entero | ⚠️ SEC-02 |
| Expediente (documentos) y su descarga | Filtra por dueño (admin ve todo) y valida al crear | UUID | ✔ |
| Avalúos | Filtra por dueño (admin ve todo) y valida al crear | UUID | ✔ |

### 1.2 Riesgos y plan

- **SEC-01 (DT-39). Las propiedades en captación son visibles para cualquier cuenta autenticada.** El filtro del catálogo solo se aplica sin sesión. El hallazgo original mencionaba el rol `cliente`, pero también afecta a los **asesores**, que ven las fichas internas de sus colegas. Esto contradice RF-01 y HU-01 (la ficha queda interna hasta publicarse).
  - *Plan:* una única regla de visibilidad, usada por la lista y por el detalle: el público y el `cliente` ven los estados publicados; el asesor, los publicados más los suyos; el admin, todo.
  - *Decidir junto con C-08* si el rol `cliente` sigue existiendo.
  - *Pruebas:* otro asesor y un `cliente` no ven una captación ni en la lista ni en el detalle.
- **SEC-02 (DT-10). Las fotos no comprueban quién es el dueño de la propiedad.** El componente de fotos no restringe por dueño ni las consultas ni los cambios.
  - *Plan:* aplicar el mismo patrón que el expediente: `queryset` filtrado por dueño (salvo admin), validación de la propiedad con `user_can_access_property()` al crear, y no permitir mover una foto a otra propiedad.
  - *Pruebas:* otro asesor recibe 403/404 en todas las operaciones.
- **SEC-03 (DT-61). Datos internos e ids consecutivos en el contrato público.** La respuesta pública de propiedades incluye el identificador del usuario asesor y un nombre que, si falta el nombre completo, recurre al nombre de usuario o al correo. Propiedades, fotos y usuarios usan ids consecutivos.
  - *Plan:* un serializer público con solo los campos de la ficha; el nombre visible del asesor, si el negocio lo pide (*decisión de negocio*); `slug` para las URL públicas (ya lo pide HU-53).
  - El entero interno se mantiene: cambiar la clave primaria de `Property` es una migración de alto riesgo en un archivo compartido.
- **SEC-11 (DT-67). Los mensajes de error distinguen entre "no existe" y "no tienes permiso".** Ocurre al crear documentos y avalúos.
  - *Plan:* limitar el campo `property` a las propiedades accesibles por el usuario, para que ambos casos den la misma respuesta.

---

## 2. Sesión: JWT en `sessionStorage` frente a cookies HttpOnly

### 2.1 Estado actual (Confirmado por código)

| Aspecto | Implementación |
|---|---|
| Vigencia | Token de acceso: **1 día**; token de renovación: 7 días (`SIMPLE_JWT` en `settings.py`) |
| Almacenamiento | Token de acceso, rol y correo en `sessionStorage`. El token de renovación **no se guarda** |
| Renovación | **No implementada:** no hay ruta de renovación de tokens |
| Revocación | **No implementada:** cerrar sesión borra los datos del navegador, pero el token sigue siendo válido hasta que expira (*Por verificar* el detalle del cierre de sesión) |
| Rol en el navegador | Solo decide qué muestra la interfaz. Los permisos reales se calculan en el servidor con el rol guardado en la BD ✔ |

### 2.2 Riesgos

- **Robo del token por XSS.** Todo lo que está en `sessionStorage` lo puede leer cualquier script de la página. Hoy la superficie de XSS es baja (React escapa todo), pero una sola inyección futura o un script de terceros comprometido daría acceso durante un día entero.
- **Cerrar sesión no protege** frente a un token que ya se copió.
- **Sin renovación**, el usuario vuelve a entrar cada 24 h, y acortar la vida del token sin un flujo de renovación empeoraría la experiencia.
- **Ventajas reales de `sessionStorage`:** se aísla por pestaña, se borra al cerrarla y no se envía solo en cada petición, así que no hay riesgo de CSRF.

### 2.3 Opciones (decisión D-05)

| Opción | Descripción | A favor | En contra |
|---|---|---|---|
| **A** | `sessionStorage` con un token de acceso corto (5–15 min) + renovación + lista de revocación | Cambio pequeño; sin CSRF | El token de renovación queda expuesto a XSS durante días |
| **B** | Token de acceso corto **solo en memoria** + token de renovación en cookie `HttpOnly; Secure; SameSite`, rotado y revocable | El JavaScript no puede leer el secreto de larga vida; un robo por XSS dura minutos; recargar la página no obliga a volver a entrar | Requiere rutas de renovación y cierre, CORS con credenciales bien configurado (DT-20) y protección CSRF en esa ruta; depende de los dominios de despliegue |
| **C** | Ambos tokens en cookies HttpOnly | Nada del token es legible por JavaScript | Protección CSRF en **toda** la API; más cambios en DRF y en `authFetch` |
| **D** | Sesión de Django o un backend intermedio (BFF) | Revocación inmediata; modelo clásico | Cambia toda la arquitectura de autenticación; fuera del alcance del sprint |

### 2.4 Recomendación (no implementada; la decide el equipo en D-05)

**Opción B.** Es el equilibrio habitual para una aplicación web con API propia: el secreto que dura días queda fuera del alcance del JavaScript, y el que circula dura minutos. Requisitos previos:
- corregir la configuración de CORS (DT-20);
- definir los dominios del despliegue, porque eso determina `SameSite` (ver §6);
- activar la lista de revocación de SimpleJWT;
- agregar una política **Content-Security-Policy** en el frontend (*Por verificar*: no se encontró ninguna).

Hasta entonces, **no** se acorta la vida del token sin un flujo de renovación.

### 2.5 Otros riesgos de autenticación (SEC-04, DT-62)

- Las respuestas de error del inicio de sesión **no son uniformes** en todos los casos, y eso permite deducir información sobre las cuentas. *Plan:* una única respuesta genérica.
- El bloqueo tras 5 intentos fallidos (RF-13) **no tiene desbloqueo en la interfaz** (HU-45). Un tercero podría dejar sin acceso a un usuario legítimo. *Plan:* además del desbloqueo por el admin, bloqueo temporal o espera progresiva, y registrar los intentos.
- **No hay límite de peticiones** en la API. *Plan:* límites por IP y por cuenta en el inicio de sesión, y un límite general para usuarios anónimos.
- Ya registrados: emisión de token a usuarios inactivos (DT-12) y correo no único (DT-13).

---

## 3. Validación de entradas y de archivos subidos

### 3.1 Entradas (SEC-06, DT-63)

| Aspecto | Estado |
|---|---|
| Inyección SQL | ✔ Solo ORM con parámetros; no hay SQL crudo |
| XSS almacenado | ✔ Mitigado en la UI actual (React escapa). **Regla:** si se agrega texto enriquecido o metaetiquetas (HU-53), escapar o sanitizar en el servidor |
| Rangos numéricos y coordenadas | ⚠️ Solo se validan en el frontend. El servidor debe validar precio y área mayores que 0, y latitud y longitud dentro de su rango (*Por verificar* el comportamiento con valores no finitos) |
| Longitud de textos | Parcial: título y ubicación tienen límite; la descripción y la justificación no |
| Parámetros de consulta | ✔ Los filtros por propiedad se validan como numéricos |
| Servicio externo de mapas | Privacidad: el texto que busca el asesor se envía a Nominatim desde el navegador (DT-35) |

*Plan:* validaciones en `PropertySerializer` con pruebas de rechazo (Estándares §2: toda regla de negocio se valida en el backend).

### 3.2 Archivos (SEC-07 / DT-64 y SEC-08 / DT-30)

| Aspecto | Documentos del expediente | Fotos de propiedades |
|---|---|---|
| Tipo real | ✔ Por contenido (PDF, JPEG, PNG, WEBP) | Validado como imagen, pero con una lista de formatos amplia (*Por verificar*) |
| Tamaño máximo | ✔ 20 MB | ⚠️ **Sin límite** |
| Nombre en disco | ✔ Lo genera el servidor | Conserva el nombre original (saneado) |
| Almacenamiento y acceso | ✔ Privado; solo dueño o admin | ⚠️ Público para quien conozca la URL, **también en captación** (*Por verificar*) |
| Contenido | Se valida el tipo, no el contenido interno; no hay antivirus (mitigado: privado + descarga como adjunto) | Los metadatos de la foto (por ejemplo, la ubicación GPS) se publican tal cual (*Por verificar*) |

*Plan para las fotos:*
- tamaño máximo y lista blanca JPEG/PNG/WEBP;
- nombre generado por el servidor;
- eliminación de metadatos;
- las fotos de propiedades no publicadas, fuera del acceso público (URLs firmadas o endpoint con permisos).

*Plan para los documentos:* valorar un análisis de contenido al migrar el almacenamiento (HU-38, §5.2).

---

## 4. DT-42 · Formato del folio de avalúos — **POR CONFIRMAR**

### 4.1 Situación actual (Confirmado por código y por validación)

- **Formato `AV-AAAAMMDD-XXXXXX`:** fecha + 6 caracteres hexadecimales aleatorios, generados en `generate_folio()`. Es único y no editable, y los folios emitidos son **inmutables** (DS-01).
- **Fecha en UTC (DT-55, validado por Pablo el 2026-10-27).** La fecha se calcula con la zona horaria del servidor, que es UTC (DT-01). Desde las 19:00 hora de Ecuador, el folio lleva la fecha del día siguiente.
- **Colisión sin reintento (DT-66).** La combinación aleatoria es amplia, pero si se repite, la creación falla con un error del servidor en lugar de generar otra.
- **Relación con la seguridad.** El folio **no** sirve para acceder: los avalúos se consultan por su UUID y con control de dueño. Un formato consecutivo no crearía un problema de acceso, siempre que ninguna consulta use el folio como llave.

### 4.2 Opciones

| Opción | Ejemplo | A favor | En contra |
|---|---|---|---|
| **A.** Aleatorio con la fecha local corregida | `AV-20261027-3F9A1C` | Sin contador ni bloqueos; no revela el volumen | No es correlativo: los huecos no se detectan; agregar un reintento |
| **B.** Consecutivo anual | `AV-2026-000123` | Correlativo y auditable (A-05, HU-50); fácil de citar | Revela el volumen; necesita un contador con bloqueo y una migración; decidir si se reinicia cada año |
| **C.** Fecha + consecutivo diario | `AV-20261027-0004` | Legible y correlativo dentro del día | Contador por día; depende de la zona horaria correcta |
| **D.** Consecutivo + dígito verificador | `AV-2026-000123-7` | Detecta errores al escribirlo a mano | Más largo; solo aporta si el folio se teclea |

**En cualquier opción:**
- Corregir la zona horaria (DT-01, `America/Guayaquil`) antes o en el mismo cambio.
- Los folios ya emitidos se quedan como están; el formato nuevo rige desde una fecha registrada.

### 4.3 Preguntas para cerrar DT-42 (equipo / tutor)

1. ¿La inmobiliaria o alguna norma exige numeración **correlativa** de los avalúos?
2. Si es consecutivo, ¿se reinicia cada año?
3. ¿Importa no revelar el volumen de avalúos a quien recibe un folio?
4. ¿El folio se dicta o se teclea (lo que justificaría D)?

**No se implementa nada hasta la respuesta (DS-18).**

---

## 5. Infraestructura y almacenamiento

### 5.1 Base de datos (INF-01, DT-68)

| | Detalle | Estado |
|---|---|---|
| Hoy | SQLite en un archivo local (`backend/db.sqlite3`) | Confirmado (`settings.py`) |
| Objetivo | **PostgreSQL administrado en Supabase** | **Decidido** en el contexto maestro §2 ("Stack y Contenedores") y en el README. Contradicción C-07 ya registrada |
| Respaldo | Copia diaria automatizada de PostgreSQL, con RTO < 2 h y restauración documentada y medida | **Decidido** (RNF-06, contexto maestro §5) |
| Cuándo se migra | Sprint 8 / URB-55 ("pruebas integrales y despliegue") según C-07 | **POR CONFIRMAR** |
| Cómo se migran los datos | Recomendación: no migrar los datos de desarrollo. Partir de las migraciones de Django + `setup_demo_data` (o un seeder específico de demostración) | **POR CONFIRMAR** |
| Proveedor del despliegue de demostración | **Supabase** (DS-19) | **Confirmado por Pablo (2026-10-27)** |

Antes de migrar:
- probar las migraciones y las pruebas contra PostgreSQL, porque algunas restricciones y el bloqueo de filas (`select_for_update`) se comportan distinto que en SQLite (*Por verificar*);
- leer la conexión desde una variable de entorno (`DATABASE_URL` o equivalente).

### 5.2 Archivos (INF-02, DT-69)

| | Fotos (`media/`) | Documentos (`private_media/`) |
|---|---|---|
| Hoy | Disco local; **versionadas en Git** (14 archivos, unos 1,1 MB) | Disco local; ignorados por Git ✔ |
| Objetivo (contexto maestro §2) | **Cloudinary** (fotos y videos públicos optimizados) | **Supabase Storage** en buckets privados, con **URLs firmadas temporales** generadas por Django según el rol (HU-38, Sprint 6) |
| Estado | Objetivo **decidido**; Supabase **confirmado** para la demostración (DS-19); momento de la migración **POR CONFIRMAR** | Igual |

Las herramientas están **confirmadas** (DS-19). Las opciones siguientes quedan solo como referencia, por si los límites de los planes gratuitos obligaran a revisar el reparto de archivos:

| Opción | A favor | En contra |
|---|---|---|
| **1. Cloudinary + Supabase Storage** (la del contexto maestro) | Optimización de imágenes (ayuda a RNF-01); documentos privados con URLs firmadas; ya está diseñada (`PropertyMedia` con `cloudinary_public_id`, contexto maestro §7) | Dos proveedores, dos cuentas y dos juegos de credenciales |
| **2. Solo Supabase Storage** (un bucket público para fotos y uno privado para documentos) | Un solo proveedor, junto a la base de datos; URLs firmadas nativas | Sin optimización automática de imágenes; mayor consumo de la cuota del plan |
| **3. Almacenamiento compatible con S3** (por ejemplo, Cloudflare R2 o AWS S3) mediante `django-storages` | Estándar y portable; la librería ya existe | Otro proveedor más; la optimización de imágenes va aparte |

Sea cual sea la opción, las fotos de propiedades **no publicadas** no deben ser públicas (SEC-07), y los documentos siguen con acceso solo por URL firmada.

### 5.3 Dejar de versionar `db.sqlite3` y `media/` (INF-03, DT-70, DT-02, N-04)

**Por qué ahora:**
- `setup_demo_data` (DT-14) ya genera usuarios, propiedades, fotos y documentos de prueba, así que la BD versionada ya no es necesaria para trabajar.
- Mientras siga versionada, cada desarrollador sube cambios binarios que entran en conflicto (DT-43), y el repositorio público expone los datos y credenciales cifradas que contiene (SEC-09, DT-65).

**Impacto, que debe conocer todo el equipo antes del cambio:**
- **A Sebas (y a cualquier copia) se le borrará su `db.sqlite3` local al hacer pull** del commit que la deje de versionar. Antes de hacer pull, debe **copiarla a otro lugar**. Después: `migrate` + `setup_demo_data`.
- Lo mismo pasa con los archivos de `media/` que hoy están versionados.
- **Los archivos ya subidos siguen en el historial de Git.** Dejar de versionarlos no los borra de los commits anteriores, que cualquiera puede descargar del repositorio público.

**Opciones para el historial (a decidir; NO se ejecuta nada):**

| Opción | Efecto | Costo |
|---|---|---|
| Mantener el historial | Los datos antiguos siguen descargables | Ninguno técnico. Exige **cambiar las credenciales** que contenía la BD (DT-65) |
| Reescribir el historial (por ejemplo, con `git filter-repo`) | Elimina los archivos de todos los commits | **Destructivo:** cambia todos los hashes; todos deben volver a clonar; las PR abiertas se rompen; las copias o *forks* existentes conservan los datos |
| Hacer privado el repositorio | Corta el acceso público a todo el historial | Depende de si el curso exige un repositorio público (*Por confirmar con el tutor*) |

**Acción que no depende de esta decisión:** cambiar las contraseñas de las cuentas de desarrollo que están en la BD versionada, y de cualquier servicio donde se reutilicen (DT-65).

**(2026-10-28) Hecho en la copia de Pablo (DS-24):** las 3 cuentas de desarrollo que contiene la BD publicada quedaron con la **contraseña inutilizable** (no pueden iniciar sesión) y **sin permisos de superusuario**. Para trabajar se usan las cuentas de `setup_demo_data`, que nunca se publicaron. **Pendientes:**
- Sebas hace lo mismo en su copia.
- Cada dueño cambia esas contraseñas donde las haya reutilizado. Eso no se puede hacer desde el repositorio.

**(2026-10-31) Resuelto en parte (DS-25, FX-22):** `db.sqlite3` ya no se versiona (`git rm --cached`, commit `9872e98`); `media/`, `.pyc` y el historial siguen. Es el paso 2 de la propuesta de abajo, solo para la BD. **⚠️ Antes de hacer pull de develop con este cambio, copia tu `backend/db.sqlite3` fuera del repo; Git lo va a borrar de tu carpeta.**

#### Propuesta concreta para sacar la BD del repositorio (2026-10-28; **ejecutada en parte el 2026-10-31**, ver arriba; el resto lo decide el equipo en N-04)

1. **Antes de nada:** Sebas copia su `backend/db.sqlite3` y `backend/media/` fuera del repositorio.
2. **Rama propia desde `develop`** (p. ej. `chore/DT-70-dejar-de-versionar-bd`): `git rm --cached backend/db.sqlite3`, `git rm -r --cached backend/media`, los 6 `.pyc` rastreados y `.gitignore.swp` (DT-02). El `.gitignore` ya los cubre, así que **no hay que tocarlo**. Commit y PR.
3. **Después del pull**, cada copia restaura su BD desde la copia de seguridad o crea una nueva con `migrate`, `setup_demo_data` y `setup_comparables_demo`. Las fotos de `media/` se regeneran con el seeder.
4. **Historial: se recomienda mantenerlo** (primera fila de la tabla). Las cuentas expuestas ya no pueden iniciar sesión, así que reescribirlo no compensa: es destructivo y no borra las copias ni los *forks* existentes. Si el tutor permite un repositorio privado, es la medida complementaria más barata.

---

## 6. Despliegue

### 6.1 Despliegue de demostración (DS-19)

- **Aprobado por el tutor (aprox. 2026-10-20).** Debe ir **fuera de la infraestructura de producción de la empresa**.
- **✅ Servicios CONFIRMADOS por Pablo (2026-10-27): Vercel (frontend) + Render (backend) + Supabase (base de datos y almacenamiento).** Son las mismas herramientas de la arquitectura objetivo del contexto maestro §2, así que no hay contradicción entre la demostración y el objetivo. Lo que sigue **POR CONFIRMAR** es el **momento** del despliegue y de la migración (INF-01, INF-02).
- **Restricciones de los planes gratuitos** (tesis, "Costo de operación", Tabla 28): **suspensión por inactividad y reinicios en frío**. Durante una demostración, la primera petición después de un rato sin uso puede tardar. Conviene prever una petición previa o un aviso.
- **No se configura nada todavía.**

### 6.2 Arquitectura objetivo (contexto maestro §2, ya decidida)

Frontend Next.js en Vercel · backend Django REST en Render con Docker · PostgreSQL en Supabase · fotos en Cloudinary · documentos en Supabase Storage con URLs firmadas · tareas programadas y respaldos diarios (RNF-06) · rama `main` protegida con despliegue automático.

### 6.3 Diferencias con el código actual (C-07)

- No hay `Dockerfile` ni CI (DT-29).
- La base de datos es SQLite (INF-01) y los archivos están en disco local (INF-02).
- No existe la ruta de *healthcheck* que pide RNF-06.
- `settings.py` tiene valores por defecto pensados para desarrollo (SEC-10).

### 6.4 Requisitos previos a cualquier despliegue (INF-04, DT-71)

| # | Requisito | Hoy |
|---|---|---|
| 1 | **Variables de entorno** para todos los secretos y parámetros: clave secreta, base de datos, almacenamiento, CORS y hosts. Ninguno en el código, y un `.env.example` sin valores reales (DT-21) | ⚠️ `SECRET_KEY` tiene un valor de respaldo inseguro; no existe `.env.example` |
| 2 | **`DEBUG=False`** en el servidor, y que ese sea el valor por defecto si falta la variable | ⚠️ El valor por defecto es `True` |
| 3 | **`ALLOWED_HOSTS`** con solo los dominios reales | Por defecto solo `localhost`/`127.0.0.1` ✔ (debe configurarse) |
| 4 | **HTTPS** obligatorio: redirección, HSTS y cookies `Secure` | No configurado (*Por verificar* con `manage.py check --deploy`) |
| 5 | **CORS** solo con el dominio del frontend; nombre del ajuste de credenciales corregido; middleware en el orden correcto | ⚠️ Nombre del ajuste incorrecto y middleware al final (DT-20) |
| 6 | **Permisos por defecto** `IsAuthenticated` en DRF | ⚠️ No definidos (DT-20) |
| 7 | **Copias de seguridad** diarias de la base de datos **y una prueba de restauración** documentada (RNF-06) | No existe |
| 8 | **Almacenamiento externo** para fotos y documentos (INF-02) | No existe |
| 9 | **Riesgos Altos corregidos** (DS-20): SEC-01, SEC-02, SEC-07, SEC-09 y lo que esté en Alto en §0 | Abiertos |
| 10 | **Datos de demostración** creados con un seeder, nunca copiando la BD de desarrollo | `setup_demo_data` existe; *Por confirmar* si sirve para la demostración (DT-59) |
| 11 | `manage.py check --deploy` sin advertencias críticas y la suite de pruebas en verde | No ejecutado |

---

## 7. Orden sugerido (para planificar; no aprobado)

1. **SEC-09:** cambiar las credenciales. Es una acción de Pablo y no requiere código.
2. **SEC-01 y SEC-02:** regla de visibilidad + fotos con control de dueño, con sus pruebas.
3. **SEC-07:** límites de las fotos.
4. **INF-03:** dejar de versionar la BD y `media/`, coordinado con Sebas.
5. **D-05**, junto con SEC-10 (configuración) y SEC-04.
6. **INF-01, INF-02 e INF-04** antes del despliegue de demostración (DS-19, DS-20).
7. **SEC-03, SEC-06, SEC-11 y DT-42** según el sprint.

Al cerrar un riesgo: actualizar su fila en §0, su DT en [Deuda técnica](URBANEX_DEUDA_TECNICA.md) y, si cambia el control de acceso, la tabla de §1.1.
