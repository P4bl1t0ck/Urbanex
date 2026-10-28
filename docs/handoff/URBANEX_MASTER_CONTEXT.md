# Contexto Maestro de Ingeniería — Urbanex (desarrollo guiado por backlog)

> **Propósito:** Contexto autónomo de programación basado en ProyectoCapstoneV4, el Contexto Maestro original y el backlog definitivo acordado. Conserva los RF/RNF, pantallas y modelos originales y agrega planificación, trazabilidad y controles de implementación. **No sustituye las decisiones aún no resueltas en la tesis.**

---

## 1. Visión General del Sistema
**Urbanex** es una plataforma web inmobiliaria integral para una PYME en Quito, Ecuador (moneda: `USD`, zona horaria: `America/Guayaquil`, normativa: `LOPDP Ecuador`).
Resuelve 5 ejes operativos encadenados:
1. **Exposición del portafolio:** Catálogo público SSR con filtros dinámicos, SEO e indexabilidad.
2. **Contacto y agendamiento autónomo:** Captación por Web, WhatsApp y Messenger Webhook (Sandbox), más reserva de visitas sobre disponibilidad real del asesor.
3. **Trazabilidad comercial (CRM):** Gestión de contactos, conversaciones iniciales y oportunidades a través de una máquina de estados estricta, incluyendo co-intermediación.
4. **Control documental (Expediente Digital):** Repositorio privado con control de versiones, validación por el Administrador y alertas de vencimiento/faltantes.
5. **Avalúo comercial asistido (Motor Paramétrico + Human-in-the-Loop):** Cálculo determinista por método comparativo de mercado + nivel de confianza + borrador de justificación redactado por IA + calibración final del asesor.

---

## 2. Arquitectura, Stack Tecnológico y DevOps (C4 Nivel 2)

### Stack y Contenedores
- **Estructura de código:** Monorepo (`/frontend` y `/backend`).
- **Frontend (`Aplicación Next.js`):** React, Next.js (App Router + SSR), TypeScript, Tailwind CSS. Desplegado en **Vercel**.
- **Backend (`API REST`):** Python, Django 5, Django REST Framework (DRF), autenticación **JWT** (`djangorestframework-simplejwt`). Desplegado en **Render** mediante **Docker**.
- **Base de Datos:** PostgreSQL administrado en **Supabase**.
- **Almacenamiento Multimedia Público:** **Cloudinary** (fotografías y videos públicos de inmuebles optimizados).
- **Almacenamiento Documental Privado:** **Supabase Storage** (documentos legales en buckets privados, consultables únicamente mediante **URLs firmadas temporales** generadas por Django según el rol).
- **Correo Transaccional:** **Resend** (envío de credenciales, enlaces de restablecimiento de contraseña, confirmaciones y enlaces de cancelación de visitas).
- **Integraciones Externas:**
  - **WhatsApp Business API (Sandbox) y enlaces `wa.me`:** Contacto directo con mensaje precargado y mensaje automático de bienvenida con link a la ficha.
  - **Ecosistema Meta (Messenger API Webhook en Sandbox):** Recepción de consultas entrantes y respuesta automática dentro de la ventana de 24h solicitando teléfono.
  - **Servicio de IA (LLM API):** Redacción de borrador de justificación técnica del avalúo en lenguaje natural a partir del cálculo numérico determinista.

### Flujo DevOps, Git y Ambientes
- **Estrategia de ramas (GitHub Flow / Gitflow ligero para 2 Devs):**
  - `main`: Rama de producción (protegida). Actualiza automáticamente **Vercel** (Frontend) y **Render** (Backend Docker).
  - `develop`: Rama de integración continua del sprint.
  - `feat/URB-XX-descripcion`: Ramas efímeras por tarea/historia; generan Preview Deployments en Vercel.
- **Pipeline CI/CD (GitHub Actions):** En cada Push/PR ejecuta instalación de dependencias, análisis estático (linter/typecheck) y pruebas automatizadas (unitarias/integración). Bloquea el merge si falla.
- **Tareas Programadas (Cron Jobs):** Comando de administración de Django ejecutado periódicamente (vía GitHub Actions Cron / `pg_cron`) para evaluar inactividad de oportunidades (`RF-16`), visitas del día siguiente (`RF-16`), documentos próximos a vencer (`RF-10`) y respaldos diarios (`RNF-06`).

---

## 3. Roles del Sistema (RBAC)
1. **Cliente (Público / No autenticado):** Consulta catálogo público (`Disponible` y `Reservado`), filtra inmuebles, ve fichas de detalle, comparte enlaces, inicia contacto (WhatsApp, Formulario Web, Messenger), agenda/cancela visitas en horarios libres y se registra en la `Lista de Interesados` cuando un inmueble está `Reservado`.
2. **Asesor (Usuario Interno):** Registra inmuebles en captación (queda automáticamente como `captador` inmutable y `responsable` inicial), carga documentos en sus propiedades/oportunidades asignadas, ejecuta y calibra avalúos (HITL), publica propiedades, configura su disponibilidad horaria semanal y excepciones, gestiona su agenda y registra el resultado de sus visitas, atiende `Conversaciones Iniciales` pendientes, avanza sus oportunidades hasta `Pendiente de Cierre` y registra el precio final acordado.
3. **Administrador (Supervisión y Control):** Hereda permisos de Asesor y tiene **exclusividad** para: crear/editar/desactivar usuarios y cambiar roles (`RF-12`), desbloquear cuentas (`RF-13`), validar documentos como `Aprobado`/`Rechazado` (`RF-10`), ejecutar la transición final a `Cierre`, registrar acuerdos de comisión por co-intermediación, revertir reservas caídas, reabrir oportunidades cerradas (`RF-07`), asignar/reasignar propiedades y oportunidades entre asesores (`RF-08`), consultar trazabilidad/auditoría (`RF-14`) y el panel de indicadores (`RF-15`).

---

## 4. Especificación Completa de Requerimientos Funcionales (RF-01 a RF-16)

### RF-01: Publicar y consultar propiedades
- **Entradas:** Título, descripción, ubicación, áreas (total y útil en $m^2$), antigüedad, características (habitaciones, baños, parqueaderos, bodegas, piso, estado de conservación), tipo de operación (`Venta`, `Arriendo`), tipo de propiedad (`Casa`, `Departamento`, `Local comercial`, `Terreno`), multimedia (fotos/videos), precio referencial (`USD`), etiquetas descriptivas, estado, asesor responsable.
- **Estados de propiedad:** `En captación` (inicial al registrarse, oculta al público), `Disponible` (pública), `Reservado` (pública con badge visible), `Vendido`, `Arrendado`, `No disponible` (oculta al público).
- **Reglas estrictas:**
  - Requiere campos obligatorios y **al menos 1 fotografía**.
  - Quien registra la propiedad queda automáticamente como **asesor captador (inmutable)** y **asesor responsable inicial**.
  - **Condición de publicación (`En captación -> Disponible`):** Debe tener **Avalúo aprobado (`RF-11`)** + **Contrato de corretaje cargado (`RF-10`)**.
  - En estado `Reservado`: Se muestra en el catálogo con indicador, pero se **deshabilitan** el contacto directo (`RF-02`) y el agendamiento de visitas (`RF-04`), habilitando **únicamente** el formulario de interés (`RF-03`) hacia `Lista de Interesados`.
  - Los estados `Vendido` y `Arrendado` **jamás se asignan manualmente**; los asigna el sistema al confirmar el cierre en `RF-07`. La única vía para revertirlos es reabriendo la oportunidad en `RF-07` (regresando el inmueble a `Reservado`) y, si la operación cae definitivamente, aplicando la reversión de reserva para volver a `Disponible`.
  - El paso a `No disponible` es manual (retiro del mercado sin cierre) y **exige registrar un motivo obligatorio**.
  - Las URLs (`slug`) deben permanecer estables tras ediciones e incluir metaetiquetas OpenGraph para redes sociales.

### RF-02: Iniciar contacto con asesor por mensaje (WhatsApp)
- **Flujo:** Desde la ficha pública, despliega un formulario previo pidiendo `nombre` y `teléfono`. Crea el contacto (o reutiliza el existente si el teléfono ya está registrado), abre la oportunidad comercial (o vincula a la existente si ya hay una activa para ese inmueble), registra el evento en trazabilidad y redirige a WhatsApp con un mensaje predefinido que incluye título y código del inmueble.
- **Reglas:** El botón solo se habilita si la propiedad está `Disponible` y tiene asesor activo con teléfono. El evento se registra aunque el visitante luego no envíe el mensaje en WhatsApp.

### RF-03: Registrar el interés del visitante mediante formulario público
- **Entradas:** Nombre, teléfono (obligatorio), correo (opcional + checkbox de opt-in para novedades), mensaje opcional, propiedad, canal de origen (`catálogo web`, `campaña`, `interés en reservada`), **checkbox obligatorio de aceptación de política de privacidad (LOPDP)** guardando fecha y hora exacta.
- **Reglas:**
  - Si el contacto ya existe por teléfono, lo reutiliza. Si ya tiene oportunidad activa sobre la misma propiedad, agrega la interacción sin duplicar la oportunidad.
  - El `canal de origen` no es editable por usuarios internos.
  - Si la propiedad está en estado `Reservado`, crea la oportunidad con canal `interés en reservada` y estado `Lista de Interesados`. En caso contrario, nace en `Contacto Inicial`.

### RF-04: Solicitar y confirmar visitas presenciales
- **Flujo autónomo y manual:** Muestra horarios libres del asesor responsable (`RF-09`). Valida disponibilidad en tiempo real, exige teléfono y aceptación de política de privacidad (con timestamp). Registra la visita, **bloquea el horario**, cambia la oportunidad a `Visita Programada` y notifica a ambas partes. El asesor también puede registrar manualmente visitas coordinadas por WhatsApp o reprogramarlas (notificando al cliente).
- **Confirmación y Cancelación:** Si el cliente dio correo y marcó el check, recibe email con confirmación y **enlace único de cancelación** (válido solo antes de la hora programada). Si no, el asesor confirma por WhatsApp.
- **Regla de retroceso:** Si se cancela la **única visita activa** de una oportunidad en `Visita Programada`, el estado de la oportunidad regresa automáticamente a `Contacto Inicial`.
- **Resultado post-visita:** Cumplida la fecha, el asesor registra el resultado (`Realizada`, `No asistida`, `Cancelada`). Solo una visita `Realizada` habilita avanzar la oportunidad a `En Negociación`. Cada asesor ve únicamente su propia agenda.

### RF-05: Abrir contactos y oportunidades comerciales (Omnicanal + Messenger Webhook)
- **Reglas generales:** Toda oportunidad requiere Contacto + Propiedad + Asesor responsable. Un contacto puede tener múltiples oportunidades (máximo 1 activa por inmueble).
- **Flujo Messenger Webhook:** Los mensajes entrantes sin teléfono válido se guardan de forma persistente como `Conversación Inicial` (conservando métricas previas a conversión). El sistema responde automáticamente dentro de la **ventana de 24 horas de Meta** pidiendo el teléfono.
  - Si el usuario envía un teléfono válido: crea/reutiliza Contacto, abre Oportunidad, notifica al asesor in-app y dispara mensaje de bienvenida por WhatsApp Business API con enlace seguro a la ficha.
  - Si tras $N$ intentos no da teléfono o pregunta otra cosa: marca la `Conversación Inicial` como `Pendiente de atención` y muestra alerta en el panel del asesor para atención manual (el asesor luego puede marcarla como `Atendida`).
- **Captación manual interna:** El asesor registra contactos de canales informales (llamadas, referidos) exigiendo teléfono válido.

### RF-06: Avanzar el ciclo de seguimiento de la oportunidad comercial
- **Secuencia estricta de estados:**
  `Contacto Inicial` → `Visita Programada` → `En Negociación` → `Reservada` → `Evaluación Documental` → `Pendiente de Cierre` (Tope máximo del Asesor).
- **Reglas de transición:**
  - Solo el asesor asignado (o el Admin) puede avanzar la oportunidad.
  - Las negociaciones de precio y contraofertas se registran en el historial interno (inmutable) y **no alteran el precio referencial público**.
  - Al pasar a `Reservada` (registro de abono de reserva): el inmueble pasa a `Reservado`, bloquea nuevas reservas/visitas/contacto directo en el portal y "congela" temporalmente (impide avanzar de estado) a todas las demás oportunidades activas asociadas a ese inmueble.
  - El paso de `Evaluación Documental` a `Pendiente de Cierre` **se bloquea** si faltan documentos críticos validados o vigentes (`RF-10`).
  - Al avanzar a `Pendiente de Cierre`, el asesor debe registrar obligatoriamente el **`precio final acordado`**, ingresando a la cola de cierre del Administrador (`RF-07`).
  - **Estado `Perdida`:** Se puede marcar desde cualquier estado activo exigiendo un **motivo obligatorio**. Todos los cambios de estado guardan usuario, fecha y hora sin edición retroactiva.

### RF-07: Registrar el cierre, la reversión y la co-intermediación
- **Exclusividad:** Solo el **Administrador** ejecuta el Cierre, la Reversión de reserva y la Reapertura.
- **Flujo de Cierre y Co-intermediación:**
  - El Admin revisa la oportunidad en `Pendiente de Cierre` y confirma el `precio final acordado` (solo puede ajustarlo dejando motivo de corrección, o devolver la oportunidad al asesor si está incompleta).
  - El sistema verifica si `asesor_captador_propiedad == asesor_oportunidad`:
    - Si coinciden: pasa directo a `Cierre`.
    - Si difieren (co-intermediación): pasa a `Pendiente de comisión` y exige al Admin registrar los términos del acuerdo de comisión (inmutable) antes de confirmar el `Cierre` definitivo.
  - **Efecto del Cierre definitivo:** Actualiza el inmueble a `Vendido` o `Arrendado` según la operación, y **cierra automáticamente todas las demás oportunidades asociadas a ese inmueble** registrando el motivo.
- **Reversión de reserva caída:** Si cae en etapa de reserva, el Admin revierte con motivo obligatorio → inmueble vuelve a `Disponible` → **notifica automáticamente a todos los contactos de la `Lista de Interesados`** de ese inmueble y descongela las demás oportunidades previas del inmueble para que puedan retomar su negociación.
- **Reapertura de cierre:** Si una transacción cerrada se cae después, el Admin reabre la oportunidad con motivo obligatorio (conservando el historial del cierre original y sin duplicar el abono de reserva previo) → la oportunidad regresa a `Reservada` y el inmueble pasa a `Reservado` (manteniendo la exclusividad del cliente mientras se intenta salvar la operación). No dispara aviso a la Lista de Interesados; dicho aviso solo se emite si posteriormente se ejecuta la Reversión definitiva de la reserva pasando el inmueble a `Disponible`.

### RF-08: Asignar y reasignar el asesor responsable
- **Reglas de asignación automática:**
  - Propiedad publicada: `asesor_captador` = `asesor_responsable` inicial.
  - Oportunidad digital: se asigna al `asesor_responsable` actual de la propiedad.
  - Oportunidad manual creada por otro asesor distinto al captador: se asigna al asesor que la registra (generando futura co-intermediación).
- **Reasignación manual:** Exclusiva del **Administrador** (previa visualización de la carga operativa de cada asesor). Exige asesor activo y **motivo obligatorio**, guarda historial inmutable y notifica in-app al asesor entrante y al saliente.
- **Regla sobre visitas en curso:** Reasignar una propiedad u oportunidad **no transfiere automáticamente las visitas ya confirmadas**; estas permanecen con el asesor saliente hasta realizarse o cancelarse.

### RF-09: Configurar la disponibilidad horaria del asesor
- Cada asesor define su plantilla semanal (días y franjas de inicio/fin) y excepciones puntuales (fechas/horas bloqueadas). El Admin puede editar la de cualquier asesor.
- **Restricción:** No se admiten franjas menores a **30 minutos**. Los horarios ocupados por visitas confirmadas se bloquean en tiempo real y solo se liberan si la visita se cancela o reprograma.

### RF-10: Cargar, validar y alertar sobre documentos del expediente digital
- **Entradas y formato:** Archivos **PDF e imágenes**, tamaño máximo **20 MB**. Tipos: contrato de corretaje, cédula catastral, escrituras, certificado de gravámenes, comprobantes prediales/tributarios, certificados laborales/bancarios, otros. Requiere `fecha_emision` y `fecha_vigencia`.
- **Versionamiento inmutable:** Los documentos **jamás se eliminan**; subir un reemplazo crea una nueva versión conservando el historial de versiones previas.
- **Permisos y Seguridad:** El Asesor solo carga/consulta documentos de sus propiedades u oportunidades asignadas; el Admin en cualquiera. Descarga y visualización exclusivamente mediante **URLs firmadas temporales** en Supabase Storage.
- **Validación y Alertas:** Solo el **Administrador** marca `Aprobado` o `Rechazado`. El sistema emite alertas activas cuando falta un documento obligatorio para la etapa o cuando `fecha_vigencia` está a **30 días o menos de vencer**. Impide pasar de `Evaluación Documental` a `Pendiente de Cierre` si hay documentos críticos faltantes, rechazados o vencidos.

### RF-11: Calcular y calibrar el avalúo comercial (Motor Paramétrico + HITL)
- **Regla de oro:** El cálculo matemático es **100% determinista** (método comparativo de mercado con factores ponderados); **la IA nunca calcula ni altera el número**.
- **Comparables:** Provienen de la base interna del sistema. **Jamás se mezclan tipos de propiedad** (Casa solo con Casas, Departamento solo con Departamentos, etc.) y se segmentan por zona (idealmente 3 a 5 comparables).
- **Gradería de Nivel de Confianza y Degradación (Fallback):**
  - `Alto`: $\ge 3$ comparables afines del mismo tipo/zona y baja dispersión de precios por $m^2$.
  - `Medio`: Pocos comparables (1–2) o alta dispersión.
  - `Bajo`: 0 comparables suficientes → el módulo no se bloquea; habilita el **registro manual del valor** por parte del asesor con confianza baja.
- **Justificación IA y Calibración HITL:** Con el valor calculado, el backend solicita opcionalmente al servicio de IA un borrador de justificación técnica en lenguaje natural (si el servicio externo falla, permite redacción manual). El asesor revisa, calibra el valor final y aprueba.
- **Inmutabilidad:** Se guarda de forma inmutable (acumulativa, sin sobrescribir): `valor_sugerido_motor`, `nivel_confianza`, `valor_calibrado_aprobado`, `diferencia` y `justificacion`. El Admin audita en solo lectura las brechas entre el motor y los asesores.

### RF-12: Crear, editar y desactivar cuentas de usuario y asignar roles
- Exclusivo del **Administrador**. Roles únicos: `Administrador` y `Asesor`. Correo único por usuario. Envía un enlace de activación por correo (Resend) con un token de un solo uso para que el nuevo usuario establezca su propia contraseña de forma segura (jamás viajan contraseñas en texto plano).
- **Reglas:** No existe borrado de usuarios; se desactivan con motivo conservando su historial. Un usuario inactivo no puede iniciar sesión ni recibir asignaciones. **El Administrador no puede desactivar su propia cuenta.**

### RF-13: Autenticar el acceso y controlar el ciclo de sesión
- Solo usuarios activos inician sesión (JWT). Cierre automático de sesión tras periodo de inactividad. Contraseñas con hash irreversible (PBKDF2/Argon2 de Django).
- **Seguridad de acceso:** Bloqueo automático de la cuenta tras **5 intentos fallidos consecutivos** (notifica in-app al Admin, y **solo el Admin puede desbloquearla**).
- **Recuperación de contraseña:** Enlace enviado al correo con **vigencia máxima de 60 minutos y de un solo uso**.

### RF-14: Registrar la trazabilidad de eventos para auditoría
- Captura automática e inmutable (sin edición ni borrado) de los eventos generados por `RF-01, RF-05, RF-06, RF-07, RF-08, RF-10, RF-11 y RF-12`.
- Cada registro guarda: `usuario`, `fecha_hora`, `modulo`, `accion` y `detalle/entidad afectada`.
- Consulta exclusiva del **Administrador** filtrable por usuario, módulo y rango de fechas (con opción de exportación CSV).

### RF-15: Consultar el panel de indicadores operativos (KPIs)
- Exclusivo del **Administrador**, calculado en tiempo real y filtrable por rango de fechas (por defecto: mes en curso).
- **Indicadores exigidos:**
  1. Distribución de propiedades por estado (`En captación`, `Disponible`, `Reservado`, `Vendido`, `Arrendado`, `No disponible`).
  2. Carga operativa por asesor (propiedades activas y oportunidades activas asignadas).
  3. Oportunidades cerradas exitosamente frente al total de oportunidades del periodo.
  4. Volumen de `Conversaciones Iniciales` entrantes, cuántas se convirtieron en `Contacto` (tasa de conversión digital) y cuántas siguen pendientes de atención.
  5. Visualización global de recordatorios activos del equipo (`RF-16`).

### RF-16: Generar recordatorios de seguimiento de oportunidades
- Proceso programado que evalúa oportunidades en **estados activos** (`Contacto Inicial`, `Visita Programada`, `En Negociación`, `Reservada`, `Evaluación Documental`, `Pendiente de Cierre`). *No genera recordatorios de inactividad para `Cierre`, `Perdida` ni `Lista de Interesados`.*
- **Los 4 disparadores de recordatorios in-app al asesor:**
  1. **Inactividad:** Oportunidad supera el umbral de días sin cambio de estado ni interacción (umbrales por estado configurables por el Admin).
  2. **Visita próxima:** Visita confirmada programada para el **día siguiente**.
  3. **Vencimiento documental:** Documento crítico del expediente a **$\le 30$ días de vencer**.
  4. **Nueva asignación:** Nueva oportunidad asignada al asesor.
- **Regla de no duplicidad:** No crea un recordatorio nuevo si ya existe uno activo del mismo tipo para la misma oportunidad. El asesor puede marcarlos como `Atendido`.

---

## 5. Requerimientos No Funcionales y Métricas de Calidad (ISO/IEC 25010-2023)

| Código | Atributo | Métrica / Regla Técnica de Implementación |
| :--- | :--- | :--- |
| **RNF-01** | **Desempeño Móvil** | Core Web Vitals en móvil (p75): **LCP < 2,5 s**, **INP < 200 ms**, **CLS < 0,1** (usar SSR en Next.js, `next/image` y optimización de Cloudinary). |
| **RNF-02** | **Usabilidad y Fluidez** | Tasa de finalización $\ge 80\%$, SUS $\ge 70/100$. **Pasos para iniciar contacto $\le 2$**; **pasos para solicitar visita $\le 3$**. |
| **RNF-03** | **SEO e Indexabilidad** | **Lighthouse SEO $\ge 90/100$**. URLs semánticas estables (`slug`), metaetiquetas dinámicas (título, descripción, imagen), `sitemap.xml` dinámico y JSON-LD `RealEstateListing` en todas las fichas. |
| **RNF-04** | **Seguridad y LOPDP** | 100% de endpoints internos protegidos con JWT y permisos CRUD por rol en DRF. Comunicación HTTPS (SSL Labs $\ge$ A). Política de privacidad pública y registro de consentimiento. URLs firmadas temporales para documentos. |
| **RNF-05** | **Mantenibilidad** | Separación estricta Frontend/Backend; **cobertura de tests automatizados $\ge 60\%$** en catálogo, agendamiento y autenticación; API documentada (OpenAPI/Swagger) y versionada (`/api/v1/`); CI/CD automatizado. |
| **RNF-06** | **Disponibilidad** | Uptime mensual $\ge 99,5\%$, RTO $< 2$ horas, backup diario automatizado de PostgreSQL y healthcheck endpoint (`/api/v1/health/`). |
| **RNF-07** | **Resiliencia Externa** | Timeouts definidos y política de reintentos hacia Meta, WhatsApp y LLM. Cola/persistencia de webhooks entrantes. **Degradación elegante (Fallback):** si cae el LLM, el avalúo permite redacción manual; si no hay comparables, habilita avalúo manual con confianza baja; todo fallo externo se registra en auditoría. |

---

## 6. Mapa de Pantallas del Prototipo (28 Pantallas Figma → Rutas Next.js)

### Portal Público (Cliente)
- `P-01`: Inicio / Landing (Buscador principal, métricas y propiedades destacadas).
- `P-02`: Catálogo de propiedades con filtros combinados y paginación (`Disponible` y `Reservado`).
- `P-03`: Ficha de detalle de propiedad (`Disponible` — galería, datos técnicos, botones WhatsApp y Agendar Visita, compartir URL).
- `P-04`: Ficha de detalle de propiedad (`Reservado` — bloquea contacto/visitas, muestra bloque de Lista de Interesados).
- `P-05`: Modal / Formulario público de Contacto / Interés (`RF-02` / `RF-03` con check LOPDP).
- `P-06`: Formulario de registro en `Lista de Interesados` para propiedad reservada (`RF-03`).
- `P-07`: Agendamiento de visita presencial (Selector de calendario y franjas libres del asesor `RF-04`/`RF-09`).
- `P-08`: Confirmación y Cancelación de cita mediante enlace único (`RF-04`).

### Portal Interno (Asesor y Administrador)
- `I-01`: Inicio de sesión interno (`RF-13`).
- `I-02`: Recuperación y restablecimiento de contraseña (`RF-13`).
- `I-03`: Dashboard principal del Asesor (Resumen de recordatorios `RF-16`, visitas de hoy, chats recientes, accesos rápidos).
- `I-04` e `I-04A`: Bandeja y Detalle de `Conversaciones Iniciales` pendientes de Messenger (`RF-05` — marcar atendida o convertir a contacto/oportunidad).
- `I-05`: Inventario interno de propiedades (Tabla filtrable con todos los estados, acceso a crear/editar y Vista 360°).
- `I-06`: Lista de Oportunidades Comerciales (Cartera filtrable por asesor, propiedad, estado y fecha).
- `I-06A`: Detalle de la Oportunidad (Barra de progreso con la secuencia del `RF-06`, línea de tiempo de interacciones y negociación de precio, registro de abono de reserva, documentos vinculados y registro de precio final acordado).
- `I-07`: Apertura manual de contacto y oportunidad comercial (`RF-05`).
- `I-08`: Agenda semanal de visitas del asesor y modal para registrar el resultado de la visita (`Realizada`, `No asistida`, `Cancelada` — `RF-04`).
- `I-09`: Configuración de disponibilidad horaria semanal y excepciones puntuales (`RF-09`).
- `I-10`: Formulario de Registro / Edición de Propiedad en captación (`RF-01`).
- `I-10B`: Vista 360° de Propiedad Seleccionada (Resumen integral, estado documental y botón de **Publicar Propiedad** que valida Avalúo + Contrato de corretaje).
- `I-11`: Módulo de Avalúos — Captura de características estructuradas y selección de 3 a 5 comparables (o botón de Registro Manual si no hay comparables — `RF-11`).
- `I-12`: Módulo de Avalúos — Resultado del motor paramétrico, indicador de Nivel de Confianza, borrador de IA y formulario de Calibración Final HITL (`RF-11`).
- `I-13`: Expediente Digital / Gestión Documental (Carga de archivos, historial de versiones, alertas de vigencia y estado de validación — `RF-10`).

### Portal Administrativo (Exclusivo Administrador)
- `A-01`: Gestión de Usuarios y Roles (Crear, editar, activar/desactivar, desbloquear cuentas con 5 intentos fallidos — `RF-12`/`RF-13`).
- `A-02`: Administración de Cartera y Carga Operativa (Visualización de carga por asesor y reasignación de propiedades/oportunidades con motivo — `RF-08`).
- `A-03`: Cola de Cierre de Oportunidades y Registro de Acuerdos de Comisión por Co-intermediación (`RF-07` — confirmar cierre, registrar comisión, devolver al asesor, revertir reserva o reabrir cierre).
- `A-04`: Registro de Auditoría y Trazabilidad del Sistema (Log inmutable filtrable por usuario, módulo y fechas + Exportar CSV — `RF-14`).
- `A-05`: Supervisión de Historial de Avalúos (Comparativa entre Valor Sugerido del Motor vs. Valor Calibrado por Asesor y varianza % + Exportar CSV — `RF-11`).
- `A-06`: Panel de Indicadores Operativos y Embudo de Conversión (`RF-15`).

---

## 7. Esquema Relacional de Base de Datos (Apps de Django)

1. **`apps.users` (`RF-12`, `RF-13`):**
   - `User`: `id (UUID)`, `email (unique)`, `full_name`, `phone`, `role (ADMIN | ASESOR)`, `is_active`, `failed_login_attempts (int)`, `is_locked (bool)`, `deactivation_reason`, `created_at`.
   - `PasswordResetToken`: `id`, `user (FK)`, `token_hash`, `expires_at (60m)`, `is_used (bool)`.
2. **`apps.properties` (`RF-01`, `RF-08`):**
   - `Property`: `id (UUID)`, `code (unique, ej. INM-0001)`, `slug (unique)`, `title`, `description`, `operation_type (VENTA | ARRIENDO)`, `property_type (CASA | DEPARTAMENTO | LOCAL | TERRENO)`, `status (EN_CAPTACION | DISPONIBLE | RESERVADO | VENDIDO | ARRENDADO | NO_DISPONIBLE)`, `unavailable_reason`, `reference_price (Decimal)`, `zone`, `address`, `latitude`, `longitude`, `total_area_m2`, `usable_area_m2`, `age_years`, `bedrooms`, `bathrooms`, `parking_spaces`, `storage_units`, `floor_number`, `conservation_state (EXCELENTE | BUENO | REGULAR)`, `tags (JSONField)`, `captor_agent (FK User, editable=False)`, `responsible_agent (FK User)`, `published_at`, `created_at`, `updated_at`.
   - `PropertyMedia`: `id`, `property (FK)`, `cloudinary_public_id`, `url`, `media_type (IMAGE | VIDEO)`, `is_cover (bool)`, `order (int)`.
3. **`apps.appraisals` (`RF-11` — Inmutable):**
   - `Appraisal`: `id (UUID)`, `folio`, `property (FK)`, `agent (FK User)`, `suggested_value (Decimal, nullable)`, `calibrated_value (Decimal)`, `difference_amount (Decimal)`, `difference_percentage (Decimal)`, `confidence_level (ALTO | MEDIO | BAJO)`, `is_manual_fallback (bool)`, `ai_draft_justification (Text)`, `final_justification (Text)`, `comparables_snapshot (JSONField)`, `created_at`. *(Sin update ni delete)*.
4. **`apps.documents` (`RF-10`):**
   - `Document`: `id (UUID)`, `property (FK nullable)`, `opportunity (FK nullable)`, `doc_type (CORRETAJE | CEDULA_CATASTRAL | ESCRITURA | GRAVAMENES | PREDIAL | CERT_LABORAL | CERT_BANCARIO | OTRO)`, `is_critical (bool)`, `storage_path`, `file_size_bytes (<= 20MB)`, `mime_type`, `version (int)`, `is_current_version (bool)`, `issue_date`, `expiration_date`, `validation_status (PENDIENTE | APROBADO | RECHAZADO)`, `rejection_reason`, `uploaded_by (FK User)`, `validated_by (FK User nullable)`, `validated_at (datetime nullable)`, `created_at.`. *(Regla de inmutabilidad documental: el archivo físico, storage_path y version jamás se sobrescriben ni eliminan; toda nueva carga genera una fila con version = n + 1 pasando la anterior a is_current_version = False en la misma transacción. La validación administrativa actualiza únicamente validation_status, validated_by, validated_at y rejection_reason).*
5. **`apps.crm` (`RF-02`, `RF-03`, `RF-05`, `RF-06`, `RF-07`):**
   - `InitialConversation`: `id`, `external_sender_id`, `channel (MESSENGER)`, `property (FK nullable)`, `messages_log (JSONField)`, `bot_attempts (int)`, `status (ACTIVA | PENDIENTE_ATENCION | ATENDIDA | CONVERTIDA)`, `attended_by (FK User nullable)`, `created_at`.
   - `Contact`: `id`, `full_name`, `phone (unique)`, `email`, `origin_channel`, `privacy_accepted_at`, `email_opt_in (bool)`, `created_at`.
   - `Opportunity`: `id`, `contact (FK)`, `property (FK)`, `assigned_agent (FK User)`, `origin_channel (CATALOGO_WEB | WHATSAPP | MESSENGER | CAMPANA | INTERES_RESERVADA | MANUAL)`, `status (CONTACTO_INICIAL | LISTA_INTERESADOS | VISITA_PROGRAMADA | EN_NEGOCIACION | RESERVADA | EVALUACION_DOCUMENTAL | PENDIENTE_CIERRE | PENDIENTE_COMISION | CIERRE | PERDIDA)`, `reservation_amount (Decimal nullable)`, `agreed_final_price (Decimal nullable)`, `admin_confirmed_price (Decimal nullable)`, `price_adjustment_reason`, `loss_or_reversion_reason`, `last_activity_at`, `closed_at`, `created_at`.
   - `OpportunityInteraction` (Inmutable): `id`, `opportunity (FK)`, `author (FK User)`, `interaction_type (NOTA | CONTRAOFERTA | SISTEMA)`, `offered_price (Decimal nullable)`, `notes`, `created_at`.
   - `OpportunityStatusHistory` (Inmutable): `id`, `opportunity (FK)`, `previous_status`, `new_status`, `changed_by (FK User)`, `reason`, `created_at`.
   - `CommissionAgreement` (Inmutable): `id`, `opportunity (OneToOne)`, `captor_agent (FK User)`, `closing_agent (FK User)`, `captor_percentage`, `closing_percentage`, `agency_percentage`, `observations`, `registered_by_admin (FK User)`, `created_at`.
6. **`apps.visits` (`RF-04`, `RF-09`):**
   - `AgentAvailability`: `id`, `agent (FK User)`, `day_of_week (0-6)`, `start_time`, `end_time`, `slot_duration_minutes (>= 30)`.
   - `AvailabilityException`: `id`, `agent (FK User)`, `exception_date`, `start_time`, `end_time`, `reason`.
   - `Visit`: `id`, `opportunity (FK)`, `property (FK)`, `agent (FK User)`, `scheduled_start`, `scheduled_end`, `status (PROGRAMADA | REALIZADA | NO_ASISTIDA | CANCELADA)`, `cancellation_token (UUID unique)`, `outcome_notes`, `created_at`.
7. **`apps.governance` (`RF-08`, `RF-14`, `RF-15`, `RF-16`):**
   - `AssignmentHistory` (Inmutable): `id`, `entity_type (PROPERTY | OPPORTUNITY)`, `entity_id`, `previous_agent (FK User)`, `new_agent (FK User)`, `changed_by_admin (FK User)`, `reason`, `created_at`.
   - `Reminder`: `id`, `opportunity (FK)`, `agent (FK User)`, `reminder_type (INACTIVIDAD | VISITA_MANANA | DOC_POR_VENCER | NUEVA_ASIGNACION)`, `message`, `is_attended (bool)`, `attended_at`, `created_at`. *(Unique constraint parcial sobre `opportunity + reminder_type` cuando `is_attended=False`)*.
   - `AuditLog` (Inmutable): `id`, `user (FK User nullable)`, `module (PROPIEDADES | CONTACTOS | OPORTUNIDADES | USUARIOS | DOCUMENTOS | AVALUOS | SEGURIDAD)`, `action`, `entity_reference`, `metadata (JSONField)`, `ip_address`, `created_at`.

---

## 8. Orden de Construcción por Releases (Resumen Ejecutivo)
- **Sprint 1 (R1):** Infraestructura (`URB-01`), Auth JWT + bloqueo 5 intentos + recuperación clave (`RF-12`, `RF-13`), Registro de propiedad en captación + multimedia Cloudinary + docs iniciales Supabase + características técnicas (`RF-01`, `RF-10`).
- **Sprint 2 (R1):** Edición de propiedad, Motor paramétrico de avalúos + nivel de confianza + borrador IA + calibración HITL (`RF-11`), Ficha de detalle pública.
- **Sprint 3 (R1):** Publicación de propiedad (`En captación -> Disponible`), Catálogo público con filtros y SEO (`RNF-03`), Disponibilidad horaria del asesor (`RF-09`), Contacto por Formulario y WhatsApp (`RF-02`, `RF-03`).
- **Sprint 4 (R1):** Webhook de Messenger en Sandbox (`RF-05`), Solicitud, confirmación y cancelación de visitas + agenda del asesor (`RF-04`).
- **Sprint 5 (R1):** Resultado de visitas, bandeja de `Conversaciones Iniciales`, apertura manual de oportunidades, reasignación de oportunidades, estado `Perdida`, detalle y filtros de oportunidades (`RF-05`, `RF-06`, `RF-08`).
- **Sprint 6 (R1 — Cierre del MVP):** Avance de estados hasta `Pendiente de Cierre`, negociación de precios, recordatorios automáticos (`RF-16`), consulta de documentos con URLs firmadas (`RF-10`) y registro de abono de reserva (`RF-06`).
- **Sprint 7 (R2 — Cierre y Supervisión):** Versionamiento y validación documental por Admin + alertas a 30 días (`RF-10`), Cierre definitivo y acuerdo de co-intermediación (`RF-07`), reversión de reserva caída y panel de inventario/carga operativa (`RF-15`).
- **Sprint 8 (R3 — Estabilización y Entrega Final):** Reapertura de cierres, `Lista de Interesados` y aviso automático de liberación (`RF-03`, `RF-07`), reasignación de propiedades e historial (`RF-08`), historial de avalúos, consolidación del Log de Auditoría (`RF-14`), panel de conversión (`RF-15`) y pruebas integrales E2E.

---

## 9. Gobierno del contexto, alcance y decisiones

- **Fuente funcional:** `ProyectoCapstoneV4` (anexos RF, HU, pantallas y backlog). **Plan de ejecución adoptado:** backlog definitivo abajo. **Fuente técnica:** secciones 1–8 de este Markdown, conservadas del Contexto Maestro previo.
- En caso de discrepancia: documentar en **Decisiones pendientes**, identificar los RF/HU afectados y pedir aprobación; **no cambiar silenciosamente** requisitos, puntos ni sprints. Esta edición contiene algunas recomendaciones técnicas explícitas, no nuevos requisitos de la tesis.
- **Línea base inalterada:** 3 releases, 6 épicas, 8 sprints de 2 semanas, **53 historias, 166 puntos**, y 2 tareas técnicas (`URB-01`, `URB-55`) sin puntos. `URB-53/HU-51` queda en Sprint 7 y `URB-46/HU-43` en Sprint 8.
- **Auditoría para tesis:** `URB-51/HU-49` se entrega en Sprint 8. No se exige el módulo completo antes de la entrega final. Se conservarán los historiales funcionales que cada historia ya requiera (estados, versiones, avalúos). No prometer auditoría retroactiva sobre eventos nunca registrados.
- **No confundir identificadores:** las claves `URB-XX` corresponden exclusivamente a issues de Jira; los códigos comerciales de inmueble utilizan el formato `INM-0001`.
- No adelantar una interfaz o funcionalidad entera de otro sprint por reutilizar modelos o servicios compartidos; sí preparar dependencias técnicas mínimas del sprint actual.

### 9.1 Releases y épicas

| Código | Tipo | Nombre | Sprint(s) |
|---|---|---|---|
| R1 | Release | Núcleo operativo (MVP) | 1–6 |
| R2 | Release | Cierre y supervisión | 7 |
| R3 | Release | Estabilización | 8 |
| EP-1 | Épica | Acceso y administración de usuarios | 1 |
| EP-2 | Épica | Gestión de propiedades y avalúos | 1–3 |
| EP-3 | Épica | Exploración del portafolio | 2–3, 8 |
| EP-4 | Épica | Contacto y agendamiento | 3–5 |
| EP-5 | Épica | Seguimiento comercial | 5–6 |
| EP-6 | Épica | Negociación, cierre y supervisión | 6–8 |

## 10. Backlog definitivo vinculado a la trazabilidad

Esta tabla es simultáneamente **backlog**, **matriz HU→URB→RF→pantalla→modelo→sprint** y catálogo de **verificaciones mínimas propuestas**. Las verificaciones son guías de implementación; los criterios completos del Anexo 2 de la tesis prevalecen cuando ofrecen más detalle. Las rutas de API concretas se definirán en OpenAPI por historia y se versionarán en `/api/v1/`.

| Sprint | Jira | Historia / tarea | EP | Pts | RF | Pantalla | Modelos principales | Prueba/aceptación mínima |
|---:|---|---|---|---:|---|---|---|---|
| 1 | URB-01 | Tarea: infraestructura, repositorio, CI/CD | — | — | RNF-05/06 | — | Transversal | Arranque local, CI y ambientes de desarrollo |
| 1 | URB-02 | HU-44 Gestionar usuarios internos | EP-1 | 3 | RF-12 | A-01 | `User` | Crear/editar/desactivar y roles solo admin |
| 1 | URB-03 | HU-45 Desbloquear una cuenta | EP-1 | 2 | RF-13 | A-01 | `User` | Bloqueo tras 5 fallos y desbloqueo admin |
| 1 | URB-04 | HU-46 Iniciar sesión y recuperar contraseña | EP-1 | 3 | RF-13 | I-01,I-02 | `User,PasswordResetToken` | JWT, sesión y token único con vencimiento |
| 1 | URB-05 | HU-01 Registrar una propiedad en captación | EP-2 | 5 | RF-01 | I-10 | `Property, PropertyMedia` | Alta en EN_CAPTACION sin visibilidad pública |
| 1 | URB-06 | HU-02 Registrarse como captador y responsable inicial | EP-2 | 2 | RF-01,RF-08 | I-10 | `Property` | Captador inmutable y responsable inicial automáticos |
| 1 | URB-07 | HU-03 Cargar la documentación inicial | EP-2 | 2 | RF-10 | I-13 | `Document` | Archivo privado vinculado y accesible por permisos |
| 1 | URB-08 | HU-05 Registrar características del inmueble | EP-2 | 3 | RF-01,RF-11 | I-10,I-11 | `Property` | Características estructuradas válidas |
| 2 | URB-09 | HU-09 Actualizar una propiedad publicada | EP-2 | 2 | RF-01 | I-10,I-10B | `Property` | Edición interna; prueba de publicada tras HU-53 |
| 2 | URB-10 | HU-04 Seleccionar comparables para el avalúo | EP-2 | 3 | RF-11 | I-11 | `Appraisal,Property` | Comparables del mismo tipo y zona |
| 2 | URB-11 | HU-06 Obtener el valor sugerido del motor | EP-2 | 5 | RF-11 | I-12 | `Appraisal` | Cálculo determinista y nivel de confianza |
| 2 | URB-12 | HU-07 Recibir el borrador de justificación | EP-2 | 3 | RF-11 | I-12 | `Appraisal` | Borrador IA y edición manual ante falla |
| 2 | URB-13 | HU-08 Calibrar y aprobar el avalúo | EP-2 | 5 | RF-11 | I-12 | `Appraisal` | Valor calibrado con justificación e historial |
| 2 | URB-14 | HU-11 Consultar la ficha de detalle | EP-3 | 3 | RF-01 | P-03 | `Property,PropertyMedia` | Ficha consultable; publicar en Sprint 3 |
| 3 | URB-15 | HU-53 Publicar una propiedad | EP-2 | 3 | RF-01,RF-10,RF-11 | I-10B,P-03 | `Property,Appraisal,Document` | Avalúo aprobado + corretaje y fotografía |
| 3 | URB-16 | HU-10 Explorar el catálogo con filtros | EP-3 | 5 | RF-01 | P-01,P-02 | `Property` | Filtros, paginación, estados visibles y SEO |
| 3 | URB-17 | HU-12 Compartir la ficha | EP-3 | 2 | RF-01 | P-03 | `Property` | Slug estable y metadatos de compartición |
| 3 | URB-18 | HU-18 Consultar la disponibilidad del asesor | EP-4 | 3 | RF-04,RF-09 | P-07 | `AgentAvailability,AvailabilityException,Visit` | BLOQUEADA hasta completar URB-19 (HU-22); muestra solo franjas libres reales |
| 3 | URB-19 | HU-22 Configurar la disponibilidad horaria | EP-4 | 3 | RF-09 | I-09 | `AgentAvailability,AvailabilityException` | Reglas semanales y excepciones, mínimo 30m |
| 3 | URB-20 | HU-16 Registrar interés desde el formulario | EP-4 | 2 | RF-03,RF-05 | P-05 | `Contact,Opportunity` | Consentimiento y no duplicación |
| 3 | URB-21 | HU-15 Iniciar contacto por WhatsApp | EP-4 | 3 | RF-02 | P-03,P-05 | `Contact,Opportunity` | Registrar lead antes de redirección wa.me |
| 4 | URB-22 | HU-17 Iniciar contacto por Messenger | EP-4 | 5 | RF-05 | I-04,I-04A | `InitialConversation,Contact,Opportunity` | Webhook validado; no duplicar mensajes |
| 4 | URB-23 | HU-19 Solicitar una visita | EP-4 | 5 | RF-04,RF-09 | P-07 | `Visit,Opportunity` | Bloqueo transaccional sin doble reserva |
| 4 | URB-24 | HU-20 Recibir la confirmación de la visita | EP-4 | 3 | RF-04 | P-08 | `Visit` | Confirmación por canal permitido |
| 4 | URB-25 | HU-21 Cancelar una visita | EP-4 | 3 | RF-04 | P-08 | `Visit,Opportunity` | Token válido; liberar horario y retroceso si aplica |
| 4 | URB-26 | HU-23 Registrar o reprogramar una visita coordinada | EP-4 | 3 | RF-04 | I-08 | `Visit` | Reprogramar sin solapes y notificar |
| 4 | URB-27 | HU-24 Consultar la agenda de visitas | EP-4 | 2 | RF-04 | I-08 | `Visit` | Agenda restringida al asesor |
| 5 | URB-28 | HU-25 Registrar el resultado de la visita | EP-4 | 2 | RF-04 | I-08 | `Visit` | Solo visita realizada habilita negociación |
| 5 | URB-29 | HU-26 Atender conversaciones pendientes | EP-5 | 3 | RF-05 | I-04,I-04A | `InitialConversation` | Gestionar pendientes y conservar trazabilidad |
| 5 | URB-30 | HU-27 Abrir un contacto y una oportunidad manualmente | EP-5 | 3 | RF-05 | I-07 | `Contact,Opportunity` | Teléfono válido y una oportunidad activa/inmueble |
| 5 | URB-31 | HU-28 Asignar o reasignar el asesor de la oportunidad | EP-5 | 3 | RF-08 | I-06A,A-02 | `Opportunity,AssignmentHistory` | Motivo, admin y notificación; vista de carga básica |
| 5 | URB-32 | HU-31 Marcar una oportunidad como perdida | EP-5 | 2 | RF-06 | I-06A | `Opportunity,OpportunityStatusHistory` | Motivo obligatorio e historial |
| 5 | URB-33 | HU-33 Consultar una oportunidad y su seguimiento | EP-5 | 3 | RF-06 | I-06A | `Opportunity,OpportunityInteraction` | Detalle y cronología autorizados |
| 5 | URB-34 | HU-34 Buscar oportunidades con filtros | EP-5 | 3 | RF-05,RF-06 | I-06 | `Opportunity` | Filtros sin fuga entre asesores |
| 6 | URB-35 | HU-29 Avanzar el estado de la oportunidad | EP-5 | 5 | RF-06 | I-06A | `Opportunity,OpportunityStatusHistory` | Transiciones y precondiciones válidas |
| 6 | URB-36 | HU-30 Registrar interacciones y negociación de precio | EP-5 | 5 | RF-06 | I-06A | `OpportunityInteraction` | Historial inmutable y precio público intacto |
| 6 | URB-37 | HU-32 Recibir y atender recordatorios | EP-5 | 5 | RF-16 | I-03 | `Reminder` | Generación repetible sin duplicados |
| 6 | URB-38 | HU-38 Consultar la documentación | EP-6 | 2 | RF-10 | I-13 | `Document` | URL firmada, permiso por objeto |
| 6 | URB-39 | HU-35 Registrar el abono de reserva | EP-6 | 3 | RF-06,RF-07 | I-06A | `Opportunity,Property` | Cambio atómico de ambos estados |
| 7 | URB-40 | HU-36 Cargar la documentación de la transacción | EP-6 | 3 | RF-10 | I-13 | `Document` | Versionado, tipos permitidos y privacidad |
| 7 | URB-41 | HU-37 Validar un documento | EP-6 | 3 | RF-10 | I-13 | `Document` | Solo admin aprueba/rechaza |
| 7 | URB-42 | HU-39 Recibir alertas documentales | EP-6 | 3 | RF-10,RF-16 | I-13 | `Document,Reminder` | Aviso faltante o vencimiento <=30 días |
| 7 | URB-43 | HU-40 Confirmar el cierre de una oportunidad | EP-6 | 5 | RF-07 | A-03 | `Opportunity,Property,CommissionAgreement` | Admin, precio y transacción atómica |
| 7 | URB-44 | HU-41 Registrar el acuerdo de comisión | EP-6 | 3 | RF-07 | A-03 | `CommissionAgreement` | Obligatorio antes de cierre cointermediado |
| 7 | URB-45 | HU-42 Revertir una reserva caída | EP-6 | 3 | RF-07 | A-03 | `Opportunity,Property` | Motivo y liberación coherente; avisos en S8 |
| 7 | URB-53 | HU-51 Visualizar el inventario y la carga operativa | EP-6 | 3 | RF-15,RF-08 | A-02,A-06 | `Property,Opportunity` | Conteos por estado/asesor autorizados |
| 8 | URB-46 | HU-43 Reabrir una oportunidad cerrada | EP-6 | 3 | RF-07 | A-03 | `Opportunity,Property` | Motivo obligatorio; oportunidad a RESERVADA e inmueble a RESERVADO sin duplicar abono ni notificar lista |
| 8 | URB-47 | HU-13 Registrar interés en propiedad reservada | EP-3 | 3 | RF-03 | P-04,P-06 | `Contact,Opportunity` | Estado LISTA_INTERESADOS; sin duplicados |
| 8 | URB-48 | HU-14 Recibir aviso de disponibilidad | EP-3 | 2 | RF-03,RF-07 | P-06 | `Opportunity,Property` | Avisar al liberar propiedad con consentimiento adecuado |
| 8 | URB-49 | HU-47 Reasignar propiedades entre asesores | EP-6 | 3 | RF-08 | A-02 | `Property,AssignmentHistory` | Solo admin y motivo, visitas no transferidas |
| 8 | URB-50 | HU-48 Consultar las asignaciones anteriores | EP-6 | 2 | RF-08 | A-02 | `AssignmentHistory` | Historial de reasignaciones consultable |
| 8 | URB-51 | HU-49 Consultar el registro de auditoría | EP-6 | 3 | RF-14 | A-04 | `AuditLog` | Auditoría final y filtros/exportación |
| 8 | URB-52 | HU-50 Consultar los avalúos anteriores | EP-6 | 2 | RF-11 | A-05 | `Appraisal` | Histórico inmutable de valores y justificaciones |
| 8 | URB-54 | HU-52 Analizar la conversión del periodo | EP-6 | 3 | RF-15 | A-06 | `Opportunity,InitialConversation` | Indicadores filtrables y fórmula definida |
| 8 | URB-55 | Tarea: pruebas integrales y despliegue | — | — | RNF-01–07 | Transversal | Transversal | E2E, smoke test, seguridad y evidencias de entrega |

### 10.1 Balance verificado (solo historias)

| Sprint | Objetivo | Release | HU | Puntos |
|---:|---|---|---:|---:|
| 1 | Fundación técnica, usuarios y registro básico | R1 | 7 | 20 |
| 2 | Motor de avalúo y calibración | R1 | 6 | 21 |
| 3 | Publicación, catálogo y primer contacto | R1 | 7 | 21 |
| 4 | Contacto y agendamiento de visitas | R1 | 6 | 21 |
| 5 | Seguimiento comercial inicial | R1 | 7 | 19 |
| 6 | Seguimiento comercial y reserva | R1 | 5 | 20 |
| 7 | Cierre, validación documental y supervisión del inventario | R2 | 7 | 23 |
| 8 | Historiales, auditoría, indicadores y estabilización | R3 | 8 | 21 |
| **Total** | **8 sprints / 3 releases** | | **53** | **166** |

| Épica | Historias | Puntos |
|---|---:|---:|
| EP-1 | 3 | 8 |
| EP-2 | 10 | 33 |
| EP-3 | 5 | 15 |
| EP-4 | 11 | 34 |
| EP-5 | 9 | 32 |
| EP-6 | 15 | 44 |
| **Total** | **53** | **166** |

> Los puntos no incluyen el esfuerzo sin estimar de URB-01 y URB-55. Estos totales no prueban por sí solos la capacidad real del equipo.

## 11. Reglas de integridad, estados y dependencias

### 11.1 Propiedad

| Estado origen | Acción / condición | Estado destino | Protección |
|---|---|---|---|
| Nueva | Asesor/Admin registra ficha | EN_CAPTACION | Captador asignado automáticamente, no público |
| EN_CAPTACION | Publicar con foto + avalúo aprobado + contrato corretaje | DISPONIBLE | Comprobar todo en backend, transacción |
| DISPONIBLE | Abono de reserva aceptado | RESERVADO | Oportunidad RESERVADA en misma transacción |
| RESERVADO | Reserva revertida por Admin y motivo | DISPONIBLE | Registros de motivos, desbloqueos y notificación al incorporar HU-14 |
| DISPONIBLE o RESERVADO | Retirada justificada por proceso autorizado | NO_DISPONIBLE | Motivo obligatorio; revisar alcance exacto |
| RESERVADO | Cierre definitivo | VENDIDO o ARRENDADO | Según operación, solo por RF-07 |
| VENDIDO o ARRENDADO | Reabrir cierre (Sprint 8) | RESERVADO | Oportunidad vuelve a RESERVADA en la misma transacción; solo pasa a DISPONIBLE si luego se ejecuta Reversión de reserva |

No permitir el cierre transaccional ni la reserva por solo modificar un campo `status` genérico. Ejecutar servicios de dominio y comprobar condiciones en transacción. Evitar dos reservas simultáneas de la misma propiedad y horarios de visita solapados.

### 11.2 Oportunidad

Secuencia ordinaria: `CONTACTO_INICIAL → VISITA_PROGRAMADA → EN_NEGOCIACION → RESERVADA → EVALUACION_DOCUMENTAL → PENDIENTE_CIERRE → [PENDIENTE_COMISION si aplica] → CIERRE`. Salidas especiales: `PERDIDA` con motivo; `LISTA_INTERESADOS` es un flujo propio de propiedad reservada, no un paso normal hacia cierre.

- `VISITA_PROGRAMADA`: disponibilidad confirmada; al cancelar la única visita activa vuelve a `CONTACTO_INICIAL` según RF-04.
- `EN_NEGOCIACION`: habilitar solo tras visita `REALIZADA`, de acuerdo con RF-04.
- `RESERVADA`: requiere abono y cambia la propiedad a `RESERVADO` atómicamente.
- `PENDIENTE_CIERRE`: validar documentos críticos y registrar precio final acordado.
- `PENDIENTE_COMISION`: solo si captador y asesor de oportunidad difieren; convenio obligatorio antes de cerrar.
- `CIERRE`: solo Admin; actualizar propiedad, conservar evidencia y resolver restantes oportunidades en transacción.
- `PERDIDA`: motivo obligatorio; comprobar compatibilidad con reserva antes de liberar inmueble.
- **Reapertura de cierre (Regla D-01 aprobada):** Al reabrir un cierre (RF-07 / HU-43), la oportunidad regresa a `RESERVADA` y la propiedad a `RESERVADO` conservando el abono original sin duplicarlo. Si la negociación fracasa definitivamente, el Admin ejecuta la Reversión de reserva (HU-42), pasando la oportunidad a `PERDIDA`, la propiedad a `DISPONIBLE` y disparando en ese momento las notificaciones a la Lista de Interesados.

### 11.3 Orden funcional dentro de sprints

1. **Sprint 2:** `URB-09/HU-09` implementa edición, aunque su prueba de edición de *publicada* depende de `URB-15/HU-53` (Sprint 3). Registrar validación pendiente, no falsificar aceptación integral.
2. **Sprint 3:** implementar `URB-19/HU-22` (configurar horarios) antes de habilitar `URB-18/HU-18` (consultar horarios), independientemente del orden de claves Jira.
3. **Sprint 5:** `URB-31/HU-28` requiere visibilidad mínima de carga en la asignación de oportunidad; el panel amplio `URB-53/HU-51` corresponde a Sprint 7.
4. **Sprint 7:** desarrollar `URB-44/HU-41` antes de cerrar casos de co-intermediación en `URB-43/HU-40`.
5. **Sprint 7–8:** `URB-45/HU-42` libera la reserva en Sprint 7; `URB-47/HU-13` y `URB-48/HU-14` habilitan lista/avisos en Sprint 8. No prometer notificaciones reales antes de integrar esos casos. Validar el comportamiento final en E2E.
6. **Sprint 8:** `URB-51/HU-49` incorpora módulo de auditoría; historiales funcionales de etapas anteriores son independientes del panel de auditoría.

## 12. Contratos técnicos y convenciones para los dos desarrolladores

**Lo que sigue son pautas de implementación propuestas, no nuevos requisitos funcionales de la tesis.**

### 12.1 API y frontend

- Base: `/api/v1/`, JSON UTF-8, DTOs con tipos y validación en DRF, esquema OpenAPI (`drf-spectacular` es una opción a aprobar, no dependencia ya acordada).
- Convención tentativa de recursos (no endpoints definitivos): `/auth/`, `/users/`, `/properties/`, `/appraisals/`, `/documents/`, `/contacts/`, `/opportunities/`, `/visits/`, `/availability/`, `/reminders/`, `/admin/`.
- Para cada HU: definir método y ruta, request/response de ejemplo, errores (400, 401, 403, 404, 409, 429 cuando aplique), autorización por rol **y por objeto**, paginación, filtros y efecto transaccional.
- No escribir frontend contra un contrato supuesto. Confirmar schema y estados con backend; mantener tipos TypeScript alineados con OpenAPI.
- Evitar endpoints genéricos de actualización de estado que omitan servicios de negocio y permisos.

### 12.2 Seguridad

- JWT con políticas documentadas de vencimiento, refresh, revocación/cierre de sesión, rotación según la configuración definitiva, cookies seguras si se eligen y defensa CSRF si el token viaja en cookies.
- CORS con allowlist de orígenes por ambiente; secretos únicamente en entornos seguros, nunca en repositorio ni cliente.
- Validación backend de acceso a `Property`, `Opportunity`, `Visit`, `Document` y archivos firmados según el usuario asignado; el rol no basta por sí solo.
- Rate limiting para login, recuperación de contraseña, formularios públicos, creación de visitas y webhooks; mensajes de error que no filtren existencia de cuentas.
- Proteger archivos por MIME/tamaño, nombres no confiables, rutas privadas, URLs firmadas de duración limitada; no almacenar datos personales sensibles en logs generales.
- Política LOPDP: registrar consentimiento cuando aplique, distinguir aceptación de privacidad y consentimiento para novedades; definir minimización, retención y eliminación conforme a la tesis y decisiones aprobadas.

### 12.3 Asincronía e integraciones

- Messenger webhook: verificar origen/firma siguiendo integración aprobada, almacenar identificador externo de evento y rechazar duplicados; procesar respuesta sin perder evento recibido.
- WhatsApp: distinguir enlace `wa.me` (solo redirección, **no prueba de mensaje enviado**) y API Business (entrega externa dependiente del proveedor). No prometer notificación entregada sin acuse.
- Tareas programadas: ejecución repetible/idempotente; usar unicidad parcial de `Reminder` y política de reintentos, backoff y observabilidad.
- Agendamiento y reserva: usar transacciones e índices/restricciones para impedir doble ocupación; definir tratamiento de carrera para solicitudes simultáneas.
- Resend/IA/Meta: timeouts y fallbacks coherentes con RNF-07; no reintentar operaciones con efectos secundarios sin clave idempotente.

### 12.4 Datos y migraciones

- Crear índices para filtros y FKs frecuentes (`status`, `property`, `assigned_agent`, `created_at`, franjas y calendario); justificar índices reales con consultas.
- Reglas únicas en BD donde sean viables: `User.email`, `Property.code`, `Property.slug`, `Contact.phone`; una oportunidad activa por `(contact,property)` mediante validación y, de ser posible, constraint condicional.
- Documento asociado a **exactamente una** propiedad u oportunidad: validar nulidad exclusiva (según caso de uso real). Versiones numeradas únicas por expediente/tipo; no confundir versión de archivo con validación.
- Documentos, avalúos, interacciones y cambios de estado: preservar historiales exigidos, con prohibición de borrado mediante permisos/servicios; definir qué metadatos sí pueden cambiar.
- Conservar migrations como código versionado; jamás editar migraciones ya ejecutadas en un ambiente compartido.
- Datos iniciales para pruebas de avalúo: comparables sintéticos autorizados, cubriendo 0, 1–2 y 3+ comparables, dispersión y tipo de inmueble.

### 12.5 CI/CD, entornos y calidad

- En PR: lint, types, pruebas de unidad/integración y verificación de migraciones; exigir revisión de otro desarrollador cuando sea posible.
- Definir `.env.example` sin secretos, README de arranque, seed de desarrollo, scripts de test y healthcheck.
- Separar desarrollo, prueba y producción; no usar datos reales de clientes para seeds o demos.
- Respaldos: no basta generar backup; documentar restauración y medir la recuperación propuesta por RNF-06.
- La meta RNF de cobertura y Core Web Vitals es **de entrega**; cada historia debe incluir pruebas apropiadas desde su sprint.

## 13. Definition of Ready, Definition of Done y trabajo con IA

### 13.1 Definition of Ready (antes de programar una HU)

- Identificar `URB`, `HU`, sprint, epic, RF, pantallas, modelos y criterio(s) del Anexo 2.
- Enumerar dependencias ya implementadas y las que requieren stub/feature flag.
- Aclarar autorización, estado inicial/final, validaciones, errores y condiciones límite.
- Identificar datos de prueba; señalar decisiones bloqueantes sin inventar su resultado.

### 13.2 Definition of Done

- Implementación de la HU según alcance del sprint y criterios originales; sin funcionalidad extra silenciosa.
- Reglas de negocio y permisos probados en backend; cambios de BD migrables.
- API documentada y frontend integrado si corresponde; errores y estados cubiertos.
- Pruebas unitarias/integración y E2E para flujos críticos aplicables; CI verde, revisión PR.
- Evidencia breve para Jira: commit/PR, casos probados, capturas si aplica y pendientes conocidos.
- Si una aceptación depende de historia posterior, dejarla explícitamente **pendiente de integración**, no cerrarla fingiendo validación integral.

### 13.3 Instrucción para cualquier asistente de programación

Al recibir `Implementar URB-XX`:
1. Leer primero sección 10 y extraer HU/RF/pantalla/modelos/sprint; consultar las secciones 4, 6 y 7 relevantes.
2. Confirmar el alcance específico y las precondiciones de la historia; no implementar RF completos no planificados.
3. Identificar contratos API, migraciones, permisos y tests; indicar decisiones no resueltas antes de tocar código dependiente.
4. Implementar backend/frontend/migraciones y tests incrementales, sin añadir paquetes innecesarios.
5. Entregar resumen: cambios, endpoints, pruebas ejecutadas, riesgos, dependencias y estado de aceptación.
6. Actualizar `PROJECT_PROGRESS.md` (ver plantilla abajo). No modificar este maestro por cambios tácticos del día.

### 13.4 Plantilla mínima de `PROJECT_PROGRESS.md`

```md
# Urbanex — Progreso
- Sprint actual:
- Historia activa (URB / HU):
- Rama / PR:
- Terminado:
- En curso:
- Pruebas ejecutadas y resultado:
- Migraciones / endpoints nuevos:
- Decisiones aprobadas:
- Bloqueos:
- Próxima tarea:
```

## 14. Decisiones técnicas pendientes

Las siguientes decisiones se resolverán antes de implementar las funcionalidades que dependen de ellas. El asistente de programación no debe inventar valores ni dar por aprobadas decisiones todavía abiertas.

| ID | Decisión | Momento de resolución |
|---|---|---|
| D-04 | Definir fórmula matemática del motor de avalúo, factores ponderados, umbrales de confianza y datos iniciales de comparables. **(2026-10-28) Resuelta provisionalmente con DS-21** (`URBANEX_DS-21_MOTOR_AVALUOS.md`). C-02 sigue pendiente de confirmar con el tutor | Sprint 2, antes de URB-11 |
| D-05 | Definir almacenamiento, expiración, renovación y revocación de JWT, incluyendo mecanismos de protección de sesión. | Sprint 1, antes de URB-04 |
| D-06 | Elegir mecanismo de ejecución de procesos programados, webhooks y reintentos, considerando los servicios disponibles en la arquitectura. | Antes del Sprint 4 |

Una decisión aprobada debe trasladarse a la sección funcional o técnica correspondiente y registrarse en PROJECT_PROGRESS.md.

