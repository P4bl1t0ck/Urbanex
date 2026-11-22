# Urbanex — Seguridad, infraestructura y deuda técnica asociada

Ultima actualizacion de continuidad: 2026-11-18 - respaldo de rama autorizado; HU-11 en Pruebas.

| Campo | Valor |
|---|---|
| Última actualización lote 4 · Ronda 8 | 2026-11-12 · Pablo (con Claude Code) · **SEC-20**: decisión de Pablo (V-86), el celular del asesor puede ser público si es el de trabajo |
| Última actualización de corrección HU-09 | 2026-11-11 · minimización de datos del motivo de retiro en respuestas públicas; pruebas de regresión incorporadas |
| Última actualización aditiva HU-09 | 2026-11-11 · V-45 aprobada por Sebas el 2026-11-10; sin cambios en riesgos globales |
| Última actualización HU-46 · precisión JWT | 2026-11-09 · Corrección posterior a auditoría PR #20; HU-46 permanece en Pruebas |
| Última actualización · registro humano V-44 | 2026-11-09 · Fila incorporada por Sebas; auditoría y revisión pendientes |
| Última actualización HU-46 · desbloqueo | 2026-11-09 · Decisión de Sebas aplicada; validación visual del comportamiento nuevo Pendiente |
| Última actualización de integración HU-46 | 2026-11-09 · D-05 revisada; registro humano V-44 conservado; HU-46 en Pruebas |
| Última actualización aditiva HU-46 | 2026-11-06 · D-05 personalizado implementado; V-44 Pendiente |
| Propósito | Inventario de riesgos de seguridad e infraestructura del código actual, con su plan de corrección, y opciones documentadas para las decisiones pendientes (D-05 sesión/JWT, DT-42 folio, almacenamiento y base de datos) |
| Fecha | 2026-10-27 · rama `docs/DT-42-seguridad-y-deuda`, desde `develop` (`47b59ce`). **Actualizado el 2026-11-03:** SEC-16 / DT-117, datos personales de EP-5 (LOPDP), rama `feat/URB-30-34-HU-27-HU-34-oportunidades`. **Actualizado el 2026-11-02:** DT-96 (edición de `users.0007` tras aplicarse en Supabase; restablecimiento de la base de desarrollo y migración desde `develop` propuestos por Sebas, **POR CONFIRMAR** y no ejecutados (corregido por Pablo, 2026-11-03)); PostgreSQL local **No ejecutado**. **Actualizado el 2026-10-28:** SEC-09 (cuentas inutilizadas en la copia de Pablo, DS-24) y propuesta concreta en §5.3 (restaurado por Pablo, 2026-11-03). **Actualizado el 2026-10-31:** SEC-15 / DT-79 (incidente de credenciales, sin valores) (restaurado por Pablo, 2026-11-03); SEC-09 y §5.3: `db.sqlite3` ya no se versiona (DS-25, FX-22); DT-90/DT-91 para credenciales de Supabase y Resend; C-08/DS-30 confirma que clientes no tienen cuenta. **Actualizado el 2026-11-02:** §3.1, "XSS almacenado": metaetiquetas de HU-12 (FX-24), comprobación del escape Pendiente. **Actualizado el 2026-11-03:** §3.1, escape de las metaetiquetas de HU-12 comprobado (V-64, aprobada por Pablo). **Actualizado el 2026-11-03 (tarde):** §3.1, el payload RSC se cita como `\u003c/script\u003e` (corrección de la auditoría de HU-12) |
| Método | Lectura del código del backend y del frontend. **No se hicieron pruebas de intrusión.** Lo que no se comprobó en ejecución está marcado **Por verificar** |
| Alcance | Control de acceso · sesión y JWT · validación de entradas y archivos · folio de avalúos · infraestructura y almacenamiento · requisitos previos al despliegue |
| Actualización HU-45 | 2026-11-03 · El login usa respuesta uniforme para cuentas bloqueadas y credenciales incorrectas; se agregó desbloqueo admin-only. Mitigación parcial SEC-04; V-43 Pendiente; PostgreSQL no verificado |
| Confirmación V-43 HU-45 | 2026-11-04 · Según Sebas, la validación visual se completó después del último ajuste; ver evidencia registrada en `Project_Progress.md`. PostgreSQL no verificado |
| Aclaración aditiva HU-45 (2026-11-05) | Las afirmaciones antiguas de §2.5 sobre mensajes no uniformes y falta de desbloqueo describen el estado previo a HU-45; la tabla de actualización y la nota bajo ella documentan lo vigente. DT-117 queda asociado solo a SEC-16/LOPDP; la notificación de HU-45 se sigue en DT-120 |
| Última actualización | 2026-11-09 (noche) · Pablo (con Claude Code) · rama `feat/URB-20-21-35-36-HU-15-HU-16-HU-29-HU-30-contactos-crm` (lote 4): §1.3 con las dos rutas públicas nuevas de P-07 y riesgos **SEC-20** (celular del asesor en el enlace de WhatsApp; Pendiente de revisión de GUI por Pablo) y **SEC-21** (formulario público de interés). Antes: 2026-11-09 · Pablo (con Claude Code) · rama `feat/URB-23-24-28-HU-19-HU-20-HU-25-solicitud-visitas` (PR #21): nuevos **SEC-17** (solicitud pública de visita), **SEC-18** (P-08 por enlace) y **SEC-19** (API pública por defecto, DT-153); nueva **§1.3, superficie pública sin sesión** (revisión pedida por Pablo) |
| Última actualización aditiva | 2026-11-05 · Copilot con Sebas · afirmaciones históricas aclaradas y SEC-04 mantenido abierto |
| Registro oficial | Cada riesgo tiene su DT en [Deuda técnica](URBANEX_DEUDA_TECNICA.md); el estado se actualiza allí y en la tabla de §0 |

### Corrección aditiva de privacidad HU-09 — 2026-11-11

Se limita la representación del motivo de retiro en el catálogo público: el serializer devuelve `null` para solicitudes anónimas o sin contexto, conservando el valor almacenado y el acceso autenticado existente. Las pruebas de regresión cubren la privacidad y la conservación del dato; resultados en Estándares §4. Corrección implementada en código; validación humana **Pendiente**. No cambia el registro de V-45, la política de roles ni el estado de riesgos globales. Seguimiento en la actualización aditiva HU-09 de Deuda técnica, sin ID nuevo.

> **🔒 Documento publicable.** El repositorio es **público**. Por eso este documento describe **qué** está en riesgo y **cómo se corregirá**, pero **no** incluye pasos de explotación, peticiones, payloads ni comandos de ataque.
>
> **Los detalles de reproducción se guardan aparte, en privado y fuera del repositorio** (responsable: Pablo). No se escriben aquí, ni en Deuda técnica, ni en los mensajes de commit o de PR.

**Estado de la evidencia:** **Confirmado (código)** = leído en el código actual · **Confirmado (validación)** = visto por una persona en la interfaz · **Por verificar** = deducido del código, sin comprobarlo en ejecución.

**Severidad:** **Alta** = expone datos internos o permite modificar datos ajenos · **Media** = facilita un ataque o filtra información menor · **Baja** = endurecimiento.

---

### Actualización aditiva HU-46/SEC-05 — 2026-11-09

D-05 está aplicada; las opciones y recomendaciones anteriores se conservan como historial. Se revisaron el cambio de contraseña por recuperación, el cambio manual y la activación, que actualizan `password_changed_at`; se agregan pruebas explícitas de rechazo de access y refresh anteriores en los dos últimos casos. Refresh usa únicamente la cookie HttpOnly, SameSite=Lax, Secure cuando DEBUG=False, y exige CSRF; el frontend no lee el refresh. No se incorporan blacklist ni Redis. Se conserva el registro humano de V-44 de Sebas del 2026-11-07, 16:19 (`Project_Progress.md`), sin una aprobación nueva del agente. **SEC-05 permanece abierto**: la revisión de evidencia por criterio, los riesgos de despliegue y las limitaciones documentadas de logout siguen vigentes. La pregunta sobre recuperación de cuentas bloqueadas continúa pendiente, sin cambio de comportamiento.

### Consolidación D-05 y entorno local — 2026-11-21

La fila histórica de SEC-05 que decía «Decidir D-05» queda superada: D-05 está resuelta e implementada. Se conserva SEC-05 **Abierto** solo por riesgo residual de despliegue (HTTPS, CORS/CSRF por ambiente y copias externas de refresh que logout no puede revocar), no por falta de política JWT. El equipo usa `http://localhost:3000` y `http://localhost:8000` como pareja canónica en desarrollo; no debe alternar con `127.0.0.1` en una misma sesión. Esto mantiene coherentes cookie, `credentials`, CORS y `CSRF_TRUSTED_ORIGINS`; no equivale por sí solo a una garantía de seguridad en producción. La pregunta sobre desbloqueo por recuperación fue cerrada el 2026-11-11 y el texto anterior que la presenta pendiente es histórico.

### Decisión de recuperación y desbloqueo — 2026-11-09

**Decisión indicada por Sebas el 2026-11-09:** una cuenta activa que completa correctamente la recuperación segura de contraseña queda con `is_locked=False` y `failed_attempts=0`. El cambio se guarda junto con la contraseña dentro de la transacción existente de `PasswordResetConfirmView`; conserva la invalidación de JWT por `password_changed_at` y el consumo de los enlaces. Solicitar el correo no desbloquea. Los enlaces inválidos, vencidos o usados no cambian la contraseña, el bloqueo ni los contadores. Esta nota supersede la pregunta anterior sobre conservar el bloqueo; no se atribuye esta decisión a Pablo.

**Evidencia humana:** según Sebas en esta conversación (2026-11-09), las evidencias existentes están bien. Se conserva la fila humana de V-44 del 2026-11-07 sin añadir una aprobación del agente. El nuevo comportamiento de desbloqueo requiere una comprobación visual adicional por una persona; queda Pendiente y no se considera cubierto por la evidencia anterior.
El desbloqueo administrativo de HU-45 conserva su ruta y permisos; esta recuperación exige el enlace válido. No se habilitan cuentas inactivas. SEC-05 permanece abierto por sus riesgos ya documentados.


### Registro humano de ampliación V-44 — 2026-11-09

Sebas incorporó personalmente en `Project_Progress.md`, ampliación V-44, su comprobación del 2026-11-09 a las 15:13:56: recuperación válida con desbloqueo, reinicio de intentos e inicio de sesión con la contraseña nueva. Evidencia local: `evidence/ResetPasswordUsuarioBloqueado.png`; la fecha y hora fueron confirmadas por Sebas en la conversación. La fila humana supersede las menciones anteriores que dejaban esa comprobación o su transcripción Pendiente. El agente conserva ese registro sin emitir una aprobación nueva ni recalcular porcentajes. HU-46 permanece en Pruebas; auditoría de solo lectura y revisión para el merge pendientes. DT-92, DT-68 y los riesgos de seguridad no se cierran con esta nota.

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
| SEC-05 | Sesión | Token JWT en el navegador (`frontend/lib/api.ts`, `login/page.tsx`, `SIMPLE_JWT`) | Media | Abierto · Confirmado (código) | D-05 resuelta con política personalizada; revisar riesgos residuales de despliegue/logout, no elegir una opción nueva | [DT-33](URBANEX_DEUDA_TECNICA.md#p2--calidad-y-mantenibilidad), D-05 |
| SEC-03 | Exposición de datos | Contrato público de propiedades (`PropertySerializer`), ids consecutivos | Media | Abierto · Confirmado (código) | Serializer público sin datos del usuario interno; `slug` en URL públicas (§1.2) | [DT-61](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-06 | Validación de entradas | `PropertySerializer` (números y coordenadas) | Media | Abierto · Por verificar | Validar rangos y longitudes en el servidor (§3.1) | [DT-63](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-11 | Exposición de datos | Creación de documentos y avalúos (`DocumentUploadSerializer`, `AppraisalCreateSerializer`) | Baja | Abierto · Por verificar | Mensajes de error uniformes (§1.2) | [DT-67](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-08 | Validación de archivos | Contenido de los documentos (`DocumentUploadSerializer`) | Baja (mitigada) | Abierto · Confirmado (código) | Análisis de contenido al migrar el almacenamiento (§3.2) | [DT-30](URBANEX_DEUDA_TECNICA.md#p2--calidad-y-mantenibilidad) |
| SEC-12 | Integridad | Folio del avalúo (`generate_folio()` en `backend/apps/appraisals/models.py`) | Baja | Abierto · Confirmado (código + validación) | Formato POR CONFIRMAR (§4) | [DT-42](URBANEX_DEUDA_TECNICA.md#p3--menores), [DT-55](URBANEX_DEUDA_TECNICA.md#p2--calidad-y-mantenibilidad), [DT-66](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-13 | Gestión de secretos | Credenciales de Supabase PostgreSQL (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`) | Media | Abierto · Sebas indica que solo él tiene acceso; rotación en el proveedor por confirmar | Mantener solo en `backend/.env` local y variables de entorno del servicio; conceder acceso invitando al proyecto, no compartiendo contraseñas; confirmar rotación y fecha | [DT-90](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-14 | Gestión de secretos | API key de Resend (`RESEND_API_KEY`) | Media | Abierto · Sebas indica que solo él tiene acceso; dominio sin verificar; rotación por confirmar | Mantener solo en `backend/.env` local y variables de entorno del backend; verificar un dominio propio para enviar a otros destinatarios | [DT-91](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-16 | Datos personales | Contactos de oportunidades (`Contact` en `backend/apps/opportunities/models.py`): nombre, celular, correo y consentimiento LOPDP (EP-5, HU-27/HU-34) | Media | Abierto · Confirmado (código, 2026-11-03) | Definir la retención y el borrado, guardar la versión de la política aceptada, crear un proceso para los derechos del titular (acceso, rectificación, eliminación) y auditar quién consulta los datos (RF-14). Sin datos reales en desarrollo. (2026-11-08) La agenda del lote 2 (HU-24) muestra nombre, teléfono y correo del cliente al asesor: pregunta abierta para el tutor. | [DT-117](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-17 | Abuso / integridad | Solicitud pública de visita (`VisitRequestView`, `POST /api/visits/properties/<id>/request/`, HU-19): sin sesión **crea** contacto, oportunidad y visita, y bloquea una hora del asesor | Media | Abierto · Confirmado (código, 2026-11-09). Mitigado en parte: 3/min y 10/día por IP, solo propiedades Disponibles, la hora debe ser una de las ofrecidas, respuesta sin token ni datos del asesor e igual exista o no el contacto (DS-39) | Caché compartida y `NUM_PROXIES` para que el límite sea real (DT-148, DT-149). Riesgos que quedan (§1.3): quien conozca un celular puede pedir una visita a nombre de ese contacto (se reutiliza por teléfono, como en RF-02 y DS-28), y el 409 revela que ese celular ya tiene una visita en esa propiedad | [DT-149](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-18 | Exposición de datos | P-08 por enlace (`PublicVisitView`, `GET /api/visits/public/<token>/`, HU-20): quien tenga el enlace ve la propiedad, la fecha y hora de la visita y el **nombre, apellido y teléfono** del asesor (y del asesor de la oportunidad si es otro) | Baja | Abierto · Confirmado (código, 2026-11-09) | Token UUID4 que solo viaja en el correo al cliente; vale hasta la hora de inicio (después, el mismo 404 que un token inexistente); límite de 30/min por IP; la página no se indexa y no envía el enlace como Referer; sin datos del cliente. Datos del asesor por decisión de Pablo (DS-39). El token es el mismo que usará la cancelación de HU-21: revisar entonces su vigencia | DS-39 (sin DT) |
| SEC-19 | Control de acceso | Permisos por defecto de DRF (`REST_FRAMEWORK` en `backend/config/settings.py`) sin `DEFAULT_PERMISSION_CLASSES`: una vista nueva sin permisos queda **pública** | Media | Abierto · Confirmado (código, 2026-11-09). Hoy solo `LoginView` depende del valor por defecto | `IsAuthenticated` por defecto y `AllowAny` explícito en las rutas del inventario de §1.3 | [DT-153](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-20 | Exposición de datos | Botón de WhatsApp de P-07 (`PropertyWhatsAppView`, `GET /api/opportunities/public/properties/<id>/whatsapp/`, HU-15): sin sesión devuelve el **celular del asesor captador** de cada propiedad Disponible | Baja | Abierto · Confirmado (código, 2026-11-09). **Pendiente de revisión de GUI por Pablo** (DT-117). **(2026-11-12)** Decisión de Pablo (V-86): se acepta que sea público, siempre que sea el celular de trabajo | 30/min por IP (cuenta por proceso, DT-155); `null` si el asesor está inactivo o su celular no es válido. Si se decide no exponerlo: número de WhatsApp de la empresa (§1.3) | [DT-117](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27), [DT-155](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
| SEC-21 | Abuso / integridad | Formulario de interés de P-07 (`PropertyInterestView`, `POST /api/opportunities/public/properties/<id>/interest/`, HU-16): sin sesión crea o reutiliza contacto y oportunidad y agrega una interacción | Media | Abierto · Confirmado (código, 2026-11-09). Mitigado en parte: 3/min y 10/día por IP, LOPDP obligatoria, solo Disponibles con asesor activo, respuesta igual para todos (DS-50) | Igual que SEC-17: caché compartida y `NUM_PROXIES` (DT-148, DT-149, DT-155) | [DS-50](URBANEX_DEUDA_TECNICA.md#decisiones-tomadas-el-2026-11-09-aprobadas-por-pablo), [C-10](URBANEX_DEUDA_TECNICA.md#3-decisiones-pendientes-no-inventar-su-resultado) |
| INF-01 | Infraestructura | Base de datos SQLite local; PostgreSQL/Supabase opcional | Media (bloquea el despliegue) | Abierto · Confirmado; suite local PostgreSQL **No ejecutado**; edición histórica de `users.0007` pendiente; restablecimiento propuesto por Sebas, **POR CONFIRMAR** (DT-96) (corregido por Pablo, 2026-11-03) | Migrar a PostgreSQL externo (§5.1) solo tras coordinación y respaldo | [DT-68](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27), [DT-96](URBANEX_DEUDA_TECNICA.md#seguridad-e-infraestructura-2026-10-27) |
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

### 1.3 Superficie pública (sin sesión) (2026-11-09)

Revisión pedida por Pablo: todo lo que un visitante **sin cuenta** puede ver o hacer, y qué datos expone. Confirmado por código en la rama `feat/URB-23-24-28-HU-19-HU-20-HU-25-solicitud-visitas` (PR #21). Cualquier ruta nueva que responda sin sesión se agrega aquí en el mismo PR. Ojo: hoy DRF permite todo por defecto (SEC-19).

| Ruta (API) | Pantalla | Qué hace sin sesión | Datos que expone | Controles | Riesgo |
|---|---|---|---|---|---|
| `POST /api/auth/login/` (`LoginView`) | I-01 | Inicia sesión | Mensaje uniforme (HU-45) | Bloqueo tras 5 intentos; sin límite por IP | SEC-04 |
| `POST /api/auth/users/activate/` (`UserActivationView`) | `/activate` | Activa una cuenta invitada con su token | Ninguno | Token con hash y vencimiento, un solo uso | — |
| `GET /api/auth/properties/` y `/<id>/` | P-02, P-03 (`/properties`, `/properties/[id]`) | Catálogo y ficha | Ficha completa, coordenadas exactas, fotos, **id del asesor y su nombre; si no tiene nombre, su usuario o su correo** | Solo `disponible`/`reservador` sin sesión (DT-07); ids consecutivos | SEC-03, SEC-01 |
| Archivos de `media/` (fotos) | P-03 | Fotos de la ficha | Imágenes | Servidas por Django solo con `DEBUG` | SEC-07, SEC-02 |
| `GET /api/visits/properties/<id>/free-slots/` | P-07 | Horas libres del asesor (HU-18) | Solo horas; sin datos del asesor ni de visitas | Solo Disponibles; 30/min por IP | DT-148 |
| `POST /api/visits/properties/<id>/request/` | P-07 | **Crea** contacto, oportunidad y visita (HU-19) | Respuesta: fecha, hora y canal de confirmación; 409 si ese celular ya tiene visita en esa propiedad | 3/min y 10/día por IP; hora validada en transacción; LOPDP obligatoria | **SEC-17** |
| `GET /api/visits/public/<token>/` | P-08 (`/visits/[token]`) | Ver la visita del enlace del correo (HU-20) | Propiedad, fecha y hora, estado, **nombre, apellido y teléfono del asesor** (y del asesor de seguimiento) | Token UUID4, vale hasta la hora de inicio, 30/min por IP, `noindex` y `no-referrer` | **SEC-18** |
| `GET /api/opportunities/public/properties/<id>/whatsapp/` (lote 4, 2026-11-09) | P-07 (botón de WhatsApp) | Número para `wa.me` (HU-15) | **Celular del asesor captador**, solo dígitos, o `null` si está inactivo o su celular no es válido (DS-28) | Solo Disponibles (404 si no); 30/min por IP (DT-155) | **SEC-20** |
| `POST /api/opportunities/public/properties/<id>/interest/` (lote 4, 2026-11-09) | P-07 (formulario de interés) | **Crea** o reutiliza contacto y oportunidad y agrega una interacción SISTEMA (HU-16) | Respuesta 201 siempre igual (`detail`), sin ids ni datos del asesor | Solo Disponibles con asesor activo (404 si no, C-10); 3/min y 10/día por IP; LOPDP obligatoria; mensaje de 1000 caracteres como máximo | **SEC-21** |

Rutas que exigen sesión (comprobado): el resto de `api/auth/` (usuarios, mis propiedades, publicar, requisitos, fotos), `api/documents/`, `api/appraisals/`, `api/opportunities/` y, en `api/visits/`, disponibilidad, excepciones, agenda y resultado. El admin de Django (`/admin/`) tiene su propio inicio de sesión.

- **SEC-17. Solicitud pública de visita.** Es la primera ruta pública que **escribe** en la base. Los límites por IP cuentan por proceso (DT-149). Como el contacto se reutiliza por celular (RF-02, DS-28), quien conozca un celular puede pedir una visita a nombre de ese contacto; el contacto existente no se modifica. El 409 confirma que ese celular ya tiene una visita en esa propiedad.
  - *Plan:* caché compartida y `NUM_PROXIES` al desplegar (DT-148, DT-149); evaluar con el equipo una verificación del celular (por ejemplo, un código por WhatsApp) si el abuso aparece (*decisión de negocio*).
- **SEC-18. P-08 por enlace.** Quien tenga el enlace ve la visita y el teléfono del asesor. Es un dato de contacto comercial, mostrado por decisión de Pablo (DS-39), y el enlace solo viaja en el correo del cliente.
  - *Plan:* sin cambios por ahora; al implementar la cancelación (HU-21), revisar que el token no se pueda reutilizar y su vigencia.
- **SEC-19 (DT-153). Permiso por defecto `AllowAny`.**
  - *Plan:* `DEFAULT_PERMISSION_CLASSES = IsAuthenticated` (archivo compartido: avisar a Sebas, commit propio) y `AllowAny` explícito en las rutas de esta tabla, con una prueba que lo compruebe.
- **SEC-20 (lote 4, 2026-11-09). Celular del asesor en P-07.** El enlace `wa.me` necesita el número, así que cualquier visitante puede leer el celular del asesor captador de cada propiedad Disponible; el límite de 30/min por IP frena la recolección masiva, pero cuenta por proceso (DT-155, DT-148). Es un dato de contacto comercial y la simplificación de HU-15 la aprobó Pablo (DS-50).
  - *Plan:* **Pendiente de revisión de GUI por Pablo** (DT-117), al validar V-86. Alternativa si se decide no exponerlo: un número de WhatsApp Business de la empresa en lugar del celular personal.
- **SEC-21 (lote 4, 2026-11-09). Formulario público de interés.** Como SEC-17, **escribe** en la base sin sesión: reutiliza el contacto por celular sin cambiar sus datos, pero **renueva** la fecha del consentimiento (DS-50) y agrega una interacción a la oportunidad activa. La respuesta es la misma exista o no el contacto, así que no sirve para averiguar quién está registrado.
  - *Plan:* el mismo de SEC-17 (caché compartida y `NUM_PROXIES` al desplegar; verificación del celular si aparece abuso).

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

### Actualización aditiva D-05 para HU-46 (2026-11-06)

Según Sebas, Pablo aprobó una variante personalizada; no debe etiquetarse como la Opción A literal ni como la recomendación B:

- `access`: 24 horas en `sessionStorage`; `refresh`: 7 días en cookie `HttpOnly; SameSite=Lax`, `Secure` solo cuando `DEBUG=False`.
- No se usa blacklist ni Redis. La autenticación JWT y el refresh rechazan tokens cuyo `iat` precede `User.password_changed_at`; el campo se actualiza al cambiar la contraseña. El logout elimina la cookie del navegador, pero no revoca una copia robada del refresh.
- La ruta `POST /api/token/refresh/` exige el cookie CSRF estándar `csrftoken` y `X-CSRFToken`; CORS permite credenciales. En desarrollo ambos servicios deben usar `localhost`.
- La recuperación responde de forma neutral exista o no una cuenta activa. `PasswordResetTokenGenerator` y `PasswordResetToken` aplican vigencia de 60 minutos y uso único.
- El código y las pruebas automatizadas están implementados; V-44 y la validación visual siguen **Pendiente**. La variante no elimina la necesidad futura de límites de solicitudes ni de revisar los dominios reales de producción.
- En producción, configurar `CORS_ALLOWED_ORIGINS` y `FRONTEND_BASE_URL` en el entorno; no se fijan dominios de despliegue no confirmados en el código.

**Estado aditivo SEC-05:** D-05 ya está definido e implementado en la rama HU-46. La vigencia y la renovación de tokens tienen pruebas automatizadas; la validación humana/visual queda Pendiente y el cierre global de SEC-05 no se declara.

**Pregunta pendiente HU-46 (sin ID):** si una cuenta activa bloqueada recupera su contraseña, ¿el restablecimiento debe también limpiar `is_locked` y `failed_attempts`? El código conserva el bloqueo; no se cambia hasta confirmar la regla con el equipo.

### 2.5 Otros riesgos de autenticación (SEC-04, DT-62)

- Las respuestas de error del inicio de sesión **no son uniformes** en todos los casos, y eso permite deducir información sobre las cuentas. *Plan:* una única respuesta genérica.
- El bloqueo tras 5 intentos fallidos (RF-13) **no tiene desbloqueo en la interfaz** (HU-45). Un tercero podría dejar sin acceso a un usuario legítimo. *Plan:* además del desbloqueo por el admin, bloqueo temporal o espera progresiva, y registrar los intentos.
- **No hay límite de peticiones** en la API. *Plan:* límites por IP y por cuenta en el inicio de sesión, y un límite general para usuarios anónimos.
- Ya registrados: emisión de token a usuarios inactivos (DT-12) y correo no único (DT-13).

### Actualización aditiva HU-45 (2026-11-03)

| Control | Evidencia | Estado |
|---|---|---|
| Respuesta uniforme del login | `LoginView` centraliza `Credenciales inválidas.` y usa el mismo 401 para cuenta bloqueada y contraseña incorrecta; pruebas comparan código y mensaje | Mitigación implementada; SEC-04 sigue Abierto por la ausencia de bloqueo temporal y límites de peticiones |
| Desbloqueo administrativo | `POST /api/auth/users/<id>/unlock/` exige rol admin y reinicia bloqueo e intentos | Implementado; V-43 completada por Sebas el 2026-11-04, después del último ajuste |
| Aviso persistente al administrador | Excluido de HU-45, no hay modelo ni migración | No implementado; DT-120 |

**Aclaración aditiva (2026-11-05):** las dos primeras viñetas de §2.5 son históricas y describen el estado anterior a HU-45: hoy el login usa una respuesta uniforme y el administrador sí puede desbloquear desde A-01. No se considera cerrado SEC-04: siguen pendientes los límites de peticiones y el bloqueo temporal/espera progresiva. La notificación persistente es otro requisito, aún no implementado, y se rastrea como DT-120.

---

## 3. Validación de entradas y de archivos subidos

### 3.1 Entradas (SEC-06, DT-63)

| Aspecto | Estado |
|---|---|
| Inyección SQL | ✔ Solo ORM con parámetros; no hay SQL crudo |
| XSS almacenado | ✔ Mitigado en la UI actual (React escapa). **Regla:** si se agrega texto enriquecido o metaetiquetas (HU-53), escapar o sanitizar en el servidor. **(2026-11-02, HU-12, FX-24)** Las metaetiquetas de la ficha ya existen (`frontend/lib/propertyMetadata.ts`; las escribe Next a partir del título y la descripción). ~~**Pendiente: comprobación del escape de metaetiquetas programada tras reiniciar la BD local (DT-109, registrada en la rama de oportunidades, sin fusionar)**~~ **(2026-11-03) Comprobado: V-64 aprobada por Pablo** (`Project_Progress.md`, ronda HU-12). Con el título `XSS-HU12 </title><script>alert('titulo')</script> "><img src=x onerror=alert('atributo')> & 'fin'` en una ficha Disponible, `<title>`, `og:title`, `og:image:alt` y `twitter:title` salen escapados (`&lt;`, `&gt;`, `&quot;`, `&amp;`), sin `<script>` ni `<img>` literales y con un solo `og:title`, tanto para el navegador como para `facebookexternalhit/1.1`; en el payload RSC sale como `\u003c/script\u003e` (corregido el 2026-11-03 según la auditoría de HU-12). Sin alertas en el dashboard, el catálogo ni la ficha. El escape lo hace Next/React al escribir las etiquetas; no hay sanitización propia en `frontend/lib/propertyMetadata.ts`. Comprobado solo en local (SQLite, `next build` + `next start`) |
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
| Hoy | SQLite en un archivo local (`backend/db.sqlite3`) por defecto; PostgreSQL en Supabase es opcional mediante `DB_ENGINE=postgresql` y las variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y `DB_SSLMODE` | Confirmado en `backend/config/settings.py`; SQLite sigue siendo el valor por defecto |
| Objetivo | **PostgreSQL administrado en Supabase** | **Decidido** en el contexto maestro §2 ("Stack y Contenedores") y en el README. Contradicción C-07 ya registrada |
| Estado de Supabase | Sebas informó que `users.0007` y `users.0008` estaban aplicadas y que probó HU-44 el 2026-10-30; la edición posterior de `users.0007` no actualiza ese ambiente | Reportado por Sebas; esta sesión no consultó Supabase. Sebas propuso restablecer la base de desarrollo y migrar desde `develop` junto a Pablo (DT-96): propuesta **POR CONFIRMAR**, no ejecutada (corregido por Pablo, 2026-11-03) |
| Respaldo | Copia diaria automatizada de PostgreSQL, con RTO < 2 h y restauración documentada y medida | **Decidido** (RNF-06, contexto maestro §5) |
| Cuándo se usa en cada ambiente | PostgreSQL/Supabase opcional; la base activa de cada ambiente debe confirmarse antes de ejecutar migraciones | **POR CONFIRMAR** |
| Cómo se migran los datos | Propuesta de Sebas, **POR CONFIRMAR** por Pablo (corregido por Pablo, 2026-11-03): restablecer la base de desarrollo y aplicar desde `develop` las migraciones coordinadamente con Pablo; confirmar respaldo y que no haya datos que preservar antes de actuar | **Pendiente de ejecución y confirmación; no se hizo en esta sesión (DT-96)** |
| Proveedor del despliegue de demostración | **Supabase** (DS-19) | **Confirmado por Pablo (2026-10-27)** |

Antes de migrar:
- probar las migraciones y la suite contra PostgreSQL, porque algunas restricciones y el bloqueo de filas (`select_for_update`) se comportan distinto que en SQLite (*Pendiente*);
- verificar con Pablo la base de destino y respaldar lo necesario; el restablecimiento de Supabase propuesto por Sebas está **POR CONFIRMAR** y no se ha ejecutado (DT-96) (corregido por Pablo, 2026-11-03);
- documentar copias de seguridad y restauración según RNF-06 (*Pendiente*);
- guardar las credenciales solo en variables de entorno; no versionar ni compartir valores reales.

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
5. Riesgos residuales de **SEC-05**, junto con SEC-10 (configuración) y SEC-04; D-05 ya está resuelta.
6. **INF-01, INF-02 e INF-04** antes del despliegue de demostración (DS-19, DS-20).
7. **SEC-03, SEC-06, SEC-11 y DT-42** según el sprint.

Al cerrar un riesgo: actualizar su fila en §0, su DT en [Deuda técnica](URBANEX_DEUDA_TECNICA.md) y, si cambia el control de acceso, la tabla de §1.1.

### Actualización aditiva HU-09 — 2026-11-09

Las nuevas acciones de retirada/reactivación requieren autenticación y permiso por objeto (propietario o rol admin), además de `transaction.atomic` y `select_for_update` sobre la propiedad. Una retirada exige motivo no vacío y solo admite Disponible/Reservado; una reactivación solo admite No disponible y termina en captación. Los estados finales siguen fuera de las actualizaciones manuales y volver al catálogo requiere la acción HU-53, con comprobación de sus requisitos. Pruebas de permisos, ocultación al público y estados inválidos en `PropertyWithdrawalApiTests`; resultados en Estándares §4. Sebas aprobó la validación humana V-45 el 2026-11-10. No se cierran riesgos globales ni se prueba concurrencia PostgreSQL en esta sesión (DT-68). No se implementan cambios sobre oportunidades/visitas asociadas.

### Corrección posterior a auditoría PR #20 — precisión de JWT (2026-11-09)

**SEC-05/DT-33:** la comparación anterior truncaba microsegundos y aceptaba JWT previos al cambio dentro del mismo segundo. Los JWT nuevos llevan `password_version`, comparada con la marca completa de contraseña, y mantienen la comprobación de `iat`. Para JWT heredados sin versión precisa, el segundo ambiguo se rechaza: puede requerirse un nuevo login. La regresión cubre tanto access como refresh y comprueba que los nuevos funcionen inmediatamente. Se mantienen los límites documentados de logout, la necesidad de revisar dominios de producción y los riesgos abiertos; no se declara cierre global de SEC-05. Evidencia técnica en Estándares §4; V-44 humana se conserva.
# Actualización aditiva HU-11 / INF-02 / DT-69 — 2026-11-16

Última actualización de esta ampliación: 2026-11-16. Proveedor configurable de fotos públicas, aprobado por Sebas: local por defecto; Cloudinary exige cloud_name, api_key y api_secret desde el entorno. No se leen ni editan claves locales. SDK autenticado desde Django, identificadores aleatorios, sin sobrescritura, entrega HTTPS optimizada y timeout de subida de 30 s. Los errores Cloudinary/OSError se traducen a 503 genérico sin exponer mensajes del proveedor. Pruebas con mocks, sin uploads reales.

El expediente sigue usando su storage privado explícito; no pasa a Cloudinary. Las fotos ya locales conservan sus rutas y las remotas su cuenta original al cambiar de proveedor. La eliminación de filas no activa limpieza remota automática; no se ejecutan borrados del proveedor en esta sesión. No se modifica la autorización de PropertyImageViewSet ni el acceso público directo a multimedia; DT-10/SEC-02 y DS-20 siguen vigentes. Cloudinary entrega archivos públicos: este cambio no implementa privacidad para fotos en captación ni debe interpretarse como permiso de despliegue. DT-69/INF-02 siguen abiertos por integración real, archivos anteriores y Supabase documental. Validación humana y subida real **Pendiente**.
# Fixes aditivos HU-11 / SEC-02 / DT-10 — 2026-11-16

Última actualización de estos fixes: 2026-11-16. PropertyImageViewSet filtra lectura/escritura por asesor responsable o admin activo. Serializer valida propiedad al subir/modificar e impide trasladar fotos. Borrado bloquea el inmueble, protege la última foto Disponible/Reservado y elimina archivo antes de fila; errores remotos/locales devuelven 503 genérico sin mensajes del proveedor. Pruebas en base aislada y directorio temporal, con destroy remoto simulado; no se eliminan fotos reales.

Mitigación de DT-10 implementada y con regresiones; validación humana **Pendiente**. No modifica acceso público directo a URLs multimedia ni archivos privados, ni elimina otros riesgos: DS-20 vigente. No hay transacción distribuida archivo/BD; un fallo de commit posterior a la eliminación requiere reintento. No se implementa limpieza general de huérfanos ni borrado remoto automático en cascada. La comprobación HTTP 200 de la foto 29 solo acredita entrega pública de ese archivo, no aprobación de seguridad o despliegue.
**Última actualización aditiva (2026-11-17, operación y muestra aislada):** nueva base demo y copia de migración bajo evidence/HU11-operacion/, ignoradas por Git. Cuentas copiadas localmente para conservar acceso, sin imprimir credenciales, modificar contraseñas o leer/editar .env. Seeder compacto exige SQLite/DEBUG/proveedor local y base sin otras propiedades, sin borrados ni uploads Cloudinary. Constraints de operación y terrenos, API con elección explícita y bloqueo de reclasificación con publicación/avalúos previenen reinterpretar importes históricos mientras se decide un flujo de revisión. No se cambian permisos ni políticas de contacto/visitas. Base original comprobada sin cambios; no se migra Supabase. Validación humana/PostgreSQL pendientes, DS-20 y riesgos previos vigentes.
**Última actualización aditiva (2026-11-17, sustitución local autorizada):** backup completo de 28 y cuentas preservadas antes de activar siete demos en db.sqlite3. Tres usuarios con IDs, hashes de contraseña y todos los campos iguales; grupos/permisos (vacíos), 1 activación y 15 recuperaciones preservados. Sin imprimir credenciales/contenido de .env ni cambiar contraseñas. Backend detenido antes de reemplazar archivo, reiniciado y verificado por HTTP. Backups/DB ignorados, no versionar. No se eliminan fotos ni objetos Cloudinary; historial de la base anterior preservado en backup. Cambio local, no Supabase; DS-20 y riesgos previos siguen vigentes.
**Última actualización aditiva (2026-11-17, acciones bajo demanda):** formularios mantienen endpoints, payloads, validación LOPDP y separación DS-39/DS-50. Solo nombre/celular/correo se reutilizan en memoria de la misma ficha; no localStorage, no consentimiento/opt-in/mensaje/horario transferido. Montar otro flujo inicia casillas sin marcar. Reservado sin botones de contacto/visita; backend sigue comprobando estado y permisos. Diálogo bloquea cierre durante envío, restaura foco/scroll y oculta footer mientras abierto. Edge automático con datos ficticios, horario simulado y bloqueo de métodos mutantes: cero solicitudes enviadas y cero escrituras; archivos de evidencia ignorados. Prueba física y envíos reales Pendiente, DS-20 y riesgos anteriores vigentes.


### Ajuste HU-11: caracteristicas y acciones al desplazarse - 2026-11-17

Ultima actualizacion: 2026-11-17. Rama `feat/URB-14-HU-11-ficha-detalle`. Solicitud y autorizacion de Sebas: tarjetas blancas sobre fondo gris, titulo a la izquierda, valor encima de etiqueta y solo datos positivos/aplicables. Acciones iniciales junto a las caracteristicas; `IntersectionObserver` muestra barra inferior solo cuando el bloque inicial ya paso por encima de la pantalla. Contactar agente es principal azul; Agendar visita secundario con borde. Dialogos nativos abiertos (incluida galeria) ocultan barra; altura de pantalla <=450px tambien la oculta. Se conservan restricciones de Reservado, formularios bajo demanda, datos en memoria y consentimientos independientes. Sin dependencias nuevas ni cambios de backend/BD.

Archivos: `frontend/app/properties/[id]/page.tsx` y `frontend/components/PropertyActions.tsx`. Composicion HU-11/URB-14; presentacion de contacto fix HU-15/URB-21 y HU-16/URB-20, visitas fix HU-18/URB-18 y HU-19/URB-23; no cambian contratos ni reglas de esos flujos. Riesgos a revisar: transicion de barra, retorno de foco, zoom, teclado/safe area y telefono fisico. Validacion humana Pendiente; HU-11 en Pruebas, sin puntos ni nueva V aprobada.

Limpieza expresamente autorizada: `evidence/` conserva solo seis PNG de `HU11-ux/`. Se eliminaron borradores, scripts, JSON, perfil temporal y bases auxiliares/respaldo. `backend/db.sqlite3` se conserva. Las rutas historicas a archivos eliminados se mantienen como historial; ya no son evidencias disponibles. Los seis PNG conservados corresponden a la version anterior del footer y no verifican este ajuste. No se guardaran archivos auxiliares ni bases en evidence; solo capturas segun instruccion de Sebas. Sin commit/push/PR.


### Fixes de contacto, visita y ayuda de celular - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama `feat/URB-14-HU-11-ficha-detalle`. Alcance autorizado tras Fase 0: WhatsApp primero en panel Contactar agente, numero del asesor visible, separador antes del formulario. Fix HU-15/URB-21 y HU-16/URB-20. Si no hay asesor activo/celular valido o falla API, no se inventa enlace; se conserva formulario. No se agrega WhatsApp al selector de horarios; se agrega en tarjetas de asesores del detalle de visita existente (fix HU-20), solo celular ecuatoriano valido, normalizado a 5939 seguido de ocho digitos, target blank y rel noopener noreferrer.

Fix HU-19/URB-23 y HU-20: por instruccion expresa de Sebas se sustituye la casilla de confirmacion por correo de DS-39 por campo Correo para recibir la confirmacion (opcional) con ayuda visible de finalidad/canal. Campo vacio al montar visita, aunque haya correo en el borrador de interes. `visitConfirmation` recorta espacios y envia email_opt_in=true solo con email no vacio; vacio/blancos envia false. Backend mantiene validacion de email, envio tras commit y ausencia de token en respuesta. No cambia API, migraciones, backend ni opt-in del formulario de interes; privacidad LOPDP sigue obligatoria. La regla anterior de DS-39 queda como historial; esta modificacion de interfaz se atribuye a Sebas, sin reescribir decision de Pablo ni asignar DS nuevo.

Ayuda visual de celular: convencion del proyecto `09XXXXXXXX` (ocho X), no norma internacional ni mascara de entrada. Guias consultadas no prescriben X mayuscula/minuscula/asterisco: ONS https://service-manual.ons.gov.uk/design-system/patterns/phone-numbers y GOV.UK https://design-system.service.gov.uk/components/text-input/ recomiendan tipo de telefono explicito y ayuda visible. Se agrega texto permanente de diez digitos/prefijo 09; internacional +5939XXXXXXXX solo donde ya se acepta. Registro de usuarios conserva su entrada local de diez digitos. Fix HU-44/URB-02 y ayudas de contacto/oportunidad/visita, sin cambiar validadores.

Archivos: PropertyActions.tsx, WhatsAppContactButton.tsx, VisitRequestForm.tsx, InterestForm.tsx, app/visits/[token]/PublicVisitView.tsx, app/dashboard/users/page.tsx, app/dashboard/opportunities/new/page.tsx, lib/propertyDetail.ts y propertyDetail.test.mjs. Sin dependencias nuevas. Pruebas frontend 47/47; tipos/lint/build exit 0, aviso previo SiteNav. Validacion humana Pendiente: orden WhatsApp/formulario y numero, visita con/sin correo, enlace de asesores valido/invalido y ayudas en movil. Envios reales No verificado. HU-11 permanece en Pruebas; sin commit/push/PR. evidence conserva seis PNG anteriores; no se generaron archivos adicionales ni bases.


### HU-11: mapa de ficha y estadisticas operativas - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama `feat/URB-14-HU-11-ficha-detalle`. Fase 0 y ok explicito: mapa publico con punto exacto guardado, estadisticas solo admin. HU-11/URB-14: `PropertyLocationMap.tsx` entre descripcion y similares, Leaflet/OSM existente, marcador azul propio, contenedor redondeado, zoom con rueda desactivado, carga al acercarse a viewport, sin SSR de Leaflet y enlace Abrir en Google Maps. No se cambia proveedor/estilo de calles ni se usan mapas de Google; estetica propia en controles/marcador/contenedor. Coordenadas finitas y dentro de rango; faltantes/invalidas muestran mensaje y no inicializan mapa. No se agrega mapa al catalogo (ampliacion HU-10/URB-16 pendiente) ni se ocultan coordenadas del dashboard en esta etapa.

Trabajo transversal adicional, no criterio original HU-11: modulo `backend/apps/telemetry/` (apps.py, models.py, views.py, urls.py, tests.py, __init__.py, migrations/0001_initial.py y migrations/__init__.py), settings.py y urls.py compartidos. Una tabla DailyMapLoads en la MISMA BD, agregados por dia local/pantalla/proveedor, incremento F atomico y clave unica. Solo detail/leaflet instrumentado. POST /api/telemetry/map-loads/ anonimo con CSRF obligatorio, payload cerrado de valores admitidos, propiedad publica existente y throttle 30/min/IP. No guarda IP, property_id ni datos personales en tabla; throttle DRF usa IP transitoriamente en cache. Cache limitadora actual por proceso: no proteccion global distribuida. Contador susceptible de reportes perdidos/repetidos/falsificados, bots y bloqueo de cookies/JS; no sirve para garantizar ausencia de cobros ni visitantes unicos. Reporte best effort, no reintenta ni bloquea mapa; cookie CSRF debe ser accesible en despliegue conforme configuracion compartida frontend/backend.

GET /api/dev/stats/ requiere usuario activo con role admin, no is_staff, Cache-Control private,no-store. Incluye periodo mes actual hasta hoy en zona configurada, total/serie diaria, referencias de fotos locales/cloudinary, versiones actuales/totales y suma file_size_bytes de TODAS las versiones documentales. Tamano de fotos, trafico, transformaciones y cobro oficial son null/no medidos; no se escanea disco ni se consulta Cloudinary. Documento usa private_storage local existente; traslado a almacenamiento privado remoto es HU-38, no implementado. Inventario no verifica existencia fisica ni archivos huerfanos. Correos, tamano BD, hosting y facturacion oficial declarados unmeasured, sin inventar ceros ni umbral de Google. Referencias de costos: Cloudinary storage/bandwidth/transformations (https://cloudinary.com/documentation/developer_onboarding_faq_track_credits), Supabase compute/disk/egress (https://supabase.com/docs/guides/platform/billing-on-supabase).

Migracion nueva telemetry.0001 aplicada solo SQLite backend/db.sqlite3 tras assert de motor y ruta; no nuevas bases, no Supabase, no alteraciones a usuarios/propiedades ni migraciones existentes. Comprobacion APIClient local: stats anonimo 401, admin 200; 7 fotos locales, 0 cloudinary, 7 versiones/7 vigentes, 1351 bytes declarados documentales, 0 cargas; propiedades 7, usuarios 3. Sin contenido de .env ni claves expuestas. Sin dependencias nuevas, Google key ni cambio automatico de proveedor. Seis pruebas de permisos, agregacion, mes, CSRF/throttle, propiedad privada y valores invalidos e inventario. Frontend nueva prueba de coordenadas (incluye cero y limites).

Validacion humana Pendiente: revisar Ubicacion en escritorio/movil, scroll sin zoom accidental, marcador y popup, abrir Google, galeria/formularios sobre mapa y endpoint admin con sesion real. Revisar contador antes/despues de abrir mapa; APIClient y suite no sustituyen navegador ni facturacion oficial. HU-11 en Pruebas, sin nueva V aprobada ni puntos; Anexo 2 POR CONFIRMAR. Sin commit/push/PR; evidence solo seis PNG anteriores, sin capturas nuevas ni scripts/bases auxiliares.

Uso del endpoint: backend /api/dev/stats/ no es una pagina frontend /dev; requiere Authorization Bearer del acceso de un administrador, igual que otras API internas. No poner token en URL ni compartirlo. GET no modifica contadores. Cargas instrumentadas solo al inicializar el mapa cercano a viewport, no por marcador, imagen de mosaico o gesto de zoom. La medicion empieza con este despliegue; no reconstruye meses anteriores.


### Acceso visual a estadisticas operativas - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Solicitud expresa de Sebas: no depender de consola para consultar estadisticas. Trabajo transversal adicional a HU-11: nueva pantalla `frontend/app/dashboard/dev/page.tsx` en /dashboard/dev, contrato `frontend/types/telemetry.ts`, enlace Estadisticas solo admin junto a Administrar usuarios en `frontend/app/dashboard/page.tsx` (archivo compartido), grupo de botones con flex-wrap para movil. No se toca SiteNav. Usa authFetch y sesion existente, renovacion de token habitual y respuesta 401/403 controlada; no muestra token ni lo pone en URL. Suscripcion a cambios de sesion y cancelacion logica de respuestas obsoletas evitan mostrar datos anteriores a cambio/cierre de sesion. Backend conserva autorizacion admin real; ocultar enlace no es permiso de seguridad.

Pantalla con estados de sesion, carga, error/reintento y sin actividad; Actualizar manual sin polling, tarjetas de mapas/fotos/versiones, peso documental registrado y tabla diaria desplazable en movil. Indica ausencia de medicion de costos/trafico/transformaciones/correos, inventario vs archivos reales y estimaciones vs factura. No incluye comparacion con cupos gratuitos ni API de facturacion externa. Sin cambios backend/BD/migraciones ni dependencias. Atribucion: pantalla de consumo transversal y enlace en panel, no nuevo criterio HU-11; HU-11 permanece en Pruebas. Sin ID nuevo ni V aprobada.

Comprobaciones: linea base y final npm test 48/48; tsc y eslint exit 0 con aviso previo SiteNav; backend focal telemetry 6 OK en 0.085s. Resultado build en registro de Estandares. Validacion humana Pendiente: administrador ve boton y datos, Actualizar, sin actividad/error y telefono; asesor no ve enlace y no consulta endpoint. API autorizacion cubierta por pruebas, GUI no verificada en navegador. Sin commit/push/PR ni archivos nuevos en evidence. Siguiente paso: Sebas entra como administrador a Panel del agente > Estadisticas.


### HU-11: prueba de fondos CARTO - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Continuacion del cambio de fondo autorizado por Sebas; segun Sebas ya obtuvo API key, no entregada ni leida por agente. `PropertyLocationMap.tsx` lee NEXT_PUBLIC_CARTO_BASEMAP_API_KEY: con valor no vacio inicia Voyager, sin clave mantiene OSM sin peticiones anonimas a CARTO. En NODE_ENV development, con clave presente muestra selector OSM/Voyager/Positron. Cambia solo TileLayer, mantiene MapContainer, marcador, zoom y contador de inicializaciones; selector no se muestra en build de produccion. No atribuir a la prueba de build comparacion visual de estilos: no clave configurada ni pruebas reales de CARTO por agente. tileerror muestra aviso generico sin imprimir URL/key; no se agrega fallback automatico de proveedor. Ayuda y controles existentes conservados.

`lib/propertyDetail.ts` agrega mapTileSource y MapStyle, prueba nueva en propertyDetail.test.mjs para fallback sin clave, rutas voyager/positron, encodeURIComponent de valor ficticio y atribucion OSM+CARTO. No dependencias nuevas ni cambio backend/API/BD. Flujo de configuracion: Sebas crea/edita frontend/.env.local con NEXT_PUBLIC_CARTO_BASEMAP_API_KEY=<valor local>, sin compartir clave; reinicia npm run dev. En produccion variables NEXT_PUBLIC se fijan al compilar, requiere rebuild/redeploy al cambiarlas. Archivo ignorado por .gitignore, no escrito por agente. Clave browser-delivered visible en solicitudes: restringir dominios autorizados en CARTO, no afirmar que .env la oculta al navegador. No modificar backend/.env.

Fuente oficial de estilos/rutas/atribucion y consumo: https://carto.com/basemaps/ y https://carto.com/basemaps/apikey/; condiciones https://carto.com/legal/basemap-terms/. Solicitudes de mosaicos no equivalen a inicializaciones del contador actual; mover/zoom/cambiar fondo puede consumir mas mosaicos. Sin medicion de velocidad ni uso facturado. Validacion humana Pendiente: configurar clave, comparar Quito en tres fondos, atribucion, errores, telefono y controles inferiores; uso real de CARTO No verificado. Sin V aprobada ni puntos; HU-11 en Pruebas. Sin commit/push/PR, sin nuevos archivos evidence. Siguiente paso: Sebas configura variable local y revisa selector en ficha.


### 2026-11-18 - Codex con Sebas - retirar prueba CARTO y diagnostico de consistencia

Ultima actualizacion: 2026-11-18. Rama feat/URB-14-HU-11-ficha-detalle. Sebas solicita mantener solo Leaflet y evitar consumo CARTO. Se retira lectura de clave, selector desarrollo, URLs/atribucion CARTO, helper y prueba especifica; queda Leaflet + mosaicos OSM, zoom inferior derecho y aviso generico de error. Archivos de entorno intactos y clave ya no referenciada por codigo del mapa. Esta version no solicita CARTO; otras pestanas/despliegues anteriores deben recargarse/reemplazarse. No prometer ausencia de condiciones/capacidad limitada del servicio OSM.

Diagnostico pendiente de nuevo alcance: catalogo py-6 (24px), panel/oportunidades/disponibilidad/agenda py-10 (40px), enlaces Volver al panel agregan altura. Se propone componente PageLayout + guia de vistas, ajustar paginas y retirar enlaces redundantes de vistas principales tras confirmar alcance. Sesion access en sessionStorage y enlaces target blank con noopener no comparten acceso; cookie refresh HttpOnly existe pero frontend no restaura al iniciar pesta?a nueva. No se desactiva autenticacion ni se comparte token con localStorage. Pregunta a Sebas pendiente: molestia en desarrollo se refiere a perdida de sesion o mensaje Browser Use. No cambio de sesiones, plantillas ni margenes en esta etapa.

Resultados: linea base 49/49 frontend; tras retirar caso exclusivo CARTO quedan 48/48, tsc y eslint exit 0 (aviso previo SiteNav), build exit 0 16/16 paginas, sin mostrar valores .env. Backend sin cambios, suite no repetida; referencia previa sqlite 406 OK/check sin cambios. Validacion humana Pendiente, HU-11 en Pruebas, PostgreSQL No ejecutado DT-68. Sin commit/push/PR ni evidencia auxiliar. Siguiente paso: confirmar alcance de plantilla/espacios y aclarar problema de desarrollo.


### Fix HU-10/URB-16: navegacion de tarjetas durante desarrollo - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Sebas aclara que la molestia es acumular pestanas al probar; solicita mantener nueva pestana al publicar sin depender de recordar un cambio. PropertyCard.tsx usa NODE_ENV production: solo entonces target blank, rel noopener noreferrer y anuncio accesible de nueva pestana. npm run dev y test navegan misma pestana; npm run build/npm start y despliegues produccion abren nueva. Aplica a catalogo y similares porque reutilizan tarjeta. Sin flag extra, credenciales ni bypass de autenticacion. CTRL/cmd+clic del navegador sigue disponible.

Sesion: navegar en misma pestana conserva sessionStorage en desarrollo, pero NO implementa restauracion en pestanas nuevas de produccion. Cookie refresh existe, bootstrap de sesion pendiente de alcance separado; no prometer solucion ni cambiar seguridad/localStorage. No se modifica Browser Use (aclarado que no era la molestia). Ajustes de PageLayout/espacios y enlaces principales siguen pendientes del ok de alcance visual anterior. Sin backend/BD/migraciones/dependencias nuevos. HU-11 sigue en Pruebas; GUI y prueba humana de admin Pendiente.

Resultado: frontend48/48, tipos/lint/build exit0, aviso previo SiteNav. Lectura HTML local /properties: 7 enlaces de tarjeta, 0 target blank y 0 anuncios de pesta?a nueva. Eso verifica atributos servidos, no validacion humana ni restauracion real de sesion. Sin commit/push/PR ni archivos evidence. Siguiente paso: Sebas prueba misma pestana y confirma alcance de plantilla visual.


### Respaldo de trabajo para retomar - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama `feat/URB-14-HU-11-ficha-detalle`. Sebas autoriza expresamente commits y push para conservar avance en GitHub y retomar en dos dias (2026-11-20); NO solicita abrir PR ni integrar develop. Ajuste final pedido: ficha reduce direccion de text-lg/mt-2 a text-base/mt-1, espacio hasta precio y cuadro de mt-6 a mt-4, titulo Caracteristicas principales centrado. Implementado en `frontend/app/properties/[id]/page.tsx`; revision visual humana Pendiente.

Estado de continuidad: 16 commits de codigo por capa guardados desde b75e227 hasta 3d5552a; contratos serializer+Property juntos conforme GPS y archivos compartidos con commits dedicados. Documentacion se guarda despues de registrar resultados. git fetch origin ejecutado; origin/develop sigue 6e0caca, misma base (comparacion previa HEAD...origin/develop 0/0), sin cambios que integrar. No se abre PR ni se declara Apto para PR; auditoria obligatoria en chat nuevo sigue pendiente antes del futuro PR. Esta subida es respaldo de trabajo, HU-11 sigue en Pruebas y validaciones humanas Pendiente.

Comprobacion final nueva: con PIPENV_DONT_LOAD_ENV=1, DB_ENGINE=sqlite, EMAIL_PROVIDER=console, MEDIA_PROVIDER=local, suite completa incluyendo telemetry 406 OK en 164.451s, SUITE_EXIT=0; makemigrations --check --dry-run No changes detected, MIGRATIONS_EXIT=0. Frontend48/48, tsc/ESLint/build exit0 y aviso previo SiteNav; build16/16. Sin PostgreSQL (No ejecutado DT-68, Nivel1), sin capturas nuevas. No se versionan archivos .env, DB, media/private_media o evidence; fotos antiguas ya rastreadas en develop no cambiaron y no se incluyeron en estos commits.

Al retomar: abrir esta rama y leer esta nota primero; comprobar git status y referencias remotas. Base local habitual backend/db.sqlite3 conserva siete propiedades y tres usuarios; no se sube, ni se suben sus fotos/documentos locales. Otras maquinas deben configurar su propio entorno, aplicar migraciones solo contra BD local comprobada y recrear datos demo si corresponde. Migraciones nuevas: users.0010 y telemetry.0001; no editar aplicadas ni migrar Supabase desde rama. CARTO retirado, clave local sin uso; mapa Leaflet/OSM. Desarrollo navega fichas en misma pestana y produccion en nueva.

Pendientes para continuar: recuperacion de sesion al iniciar nueva pestana en produccion (sin bypass ni localStorage), validacion humana movil/desktop y envios de formularios, criterios Anexo2 POR CONFIRMAR, auditoria de solo lectura antes de PR y documentar cualquier hallazgo. No mapa de catalogo ni medicion de facturacion oficial implementados. Plantilla visual PageLayout y guia PLANTILLA_VISTA disponibles; panel/oportunidades/disponibilidad/agenda usan standard y24px arriba. Estadisticas en Panel > Estadisticas, solo admin. Explicacion de backend/frontend y fixes por HU permanece en notas anteriores/GPS. Push se confirma por hash remoto al terminar, no se presume exito en esta nota.


### Contacto: WhatsApp y correo opcional sin novedades - 2026-11-19

Ultima actualizacion: 2026-11-19. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Sebas reporta WhatsApp ausente, pide ayuda celular solo ante error y retirar casilla de novedades; posteriormente pregunta finalidad del correo segun contexto maestro. RF-03 lineas72-73 contempla correo opcional y opt-in novedades, no obliga correo para interes. HU-20/URB-24 confirma visitas en flujo distinto. Lectura de servicios confirma register_web_interest no envia email; correo se muestra al asesor en oportunidades/[id]/page.tsx:239. Se propone mantener correo opcional como canal para consulta, no se implementa confirmacion automatica ni campana, pendiente decision de alcance futura. Retirar casilla es solicitud explicita de Sebas; no se reescribe RF-03 ni DS-50 historicos.

Diagnostico WhatsApp comprobado sin mostrar numeros: GET de las7propiedades200 y whatsapp_phone ausente; SQLite modo solo lectura confirma asesores activos sin celular registrado en las7asignaciones. No es problema del enlace: falta dato de asesor. No se inventa numero ni se modifica usuario; configurar desde Administrar usuarios > editar asesor > Telefono. WhatsAppContactButton.tsx mantiene reglas de backend, muestra estado de carga/no disponible/error en lugar de desaparecer sin explicacion, Reintentar ante fallo; numero valido produce wa.me existente. Ningun numero real leido en salida ni clave expuesta.

InterestForm.tsx y VisitRequestForm.tsx retiran ayuda permanente de celular, agregan validacion contactPhoneError al salir del campo/enviar y mensaje accesible solo ante error. Helper acepta formatos DS-28 (local09 o +5939, separadores permitidos). InterestForm retira casilla novedades/validacion asociada y envia email_opt_in=false; correo sigue opcional, LOPDP obligatorio. No implica alta publicitaria ni modifica consentimientos previos de contactos existentes: DS-28 conserva datos de contacto reutilizado. Sin backend, migraciones o dependencias nuevas. Fix HU-15/URB-21, HU-16/URB-20 y presentacion celular HU-19/URB-23.

Pruebas:55/55 frontend, tipos/lint/build exit0, build16/16. Helper nuevo cubre formatos validos, faltante, corto/largo y extranjero. Navegador real datos demo: aviso no disponible, una sola casilla LOPDP, ayuda no aparece inicialmente, teclado real invalido+blur muestra error y corregir lo retira. Primera prueba con eventos sinteticos fallo; repetida con Input de CDP verifico validacion. Pruebas mock iniciales de reintento fallaron por asumir una sola consulta al montar: StrictMode hace dos y el mock daba exito en la segunda. Mock corregido para mantener fallo hasta Reintentar -> WHATSAPP_RETRY_OK,3GET simulados, enlace visible con numero sintetico, nunca abierto. No contactos/visitas enviados, correos, cambios en usuarios ni archivos evidence; navegadores cerrados. Revision visual/telefono humano Pendiente, HU-11 en Pruebas, sin aprobacion V, commit/push/PR. Siguiente paso: Sebas registra celular de trabajo en asesor y decide si quiere confirmacion transaccional como funcion nueva. Suite backend no repetida; PostgreSQL No ejecutado DT-68.
