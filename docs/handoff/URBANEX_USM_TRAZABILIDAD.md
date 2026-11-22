# Urbanex — User Story Mapping, procesos y trazabilidad

Ultima actualizacion de continuidad: 2026-11-18 - respaldo de rama autorizado; HU-11 en Pruebas.

| Campo | Valor |
|---|---|
| Última actualización HU-10 · correcciones PR #27 | 2026-11-13 · Decisión de Pablo: Anexo 2 POR CONFIRMAR; DT-121..123; HU-10 en Pruebas sin sumar puntos; correcciones solo documentales sobre 43b1e18 |
| Última actualización HU-10 · integración comprobada | 2026-11-13 · develop c420e56 integrado; SQLite 372 OK, frontend 41/41 y check sin cambios; DT-92 Resuelto; sin push |
| Última actualización HU-10 · integración de develop | 2026-11-13 · Integración de c420e56, conflictos documentales conservados y pruebas de HU-09 adaptadas a results; suite integrada en ejecución |
| Última actualización HU-10 · preparación de integración | 2026-11-13 · DT-92 corregido con storage callable y migración de estado; commits e integración autorizados por Sebas |
| Última actualización HU-10 · distribución | 2026-11-13 · Filtrar, grupos uniformes y orden junto al conteo; V-46 humana Pendiente |
| Última actualización HU-10 · orden y simplificación | 2026-11-13 · PROC-02 registra ordenado e interacción numérica; no cambia RF/modelos/corte |
| Última actualización HU-10 · preferencias | 2026-11-12 · Evolución de filtros existentes; parqueaderos exactos/3+; sin cambios de modelo o corte |
| Última actualización HU-10 · slider e histograma | 2026-11-12 · PROC-02 agrega distribución de precios y parqueaderos; RF/modelos/corte sin cambios |
| Última actualización HU-10 · barra superior | 2026-11-11 · PROC-02 agrega evolución de P-02; sin cambiar procesos, RF o corte del 60 % |
| Última actualización HU-10 · usabilidad | 2026-11-11 · PROC-02 agrega componentes de filtros y herramienta de datos locales; no cambia procesos ni corte |
| Última actualización HU-10 | 2026-11-11 · Fila aditiva de Código en PROC-02; corte del 60 % sin cambio |
| Última actualización · HU-46 con DS-35 | 2026-11-13 · Pablo (con Claude Code) · rama `docs/DT-157-estados-hu-listo`: nota en PROC-08, criterio "solo usuarios activos" de HU-46 cubierto por su prueba automática (DS-35) |
| Última actualización · HU-12 Listo | 2026-11-12 · Pablo (con Claude Code) · rama `docs/DT-157-estados-hu-listo`: nota en PROC-02, HU-12 en **Listo**; V-63 No aplicable hasta el despliegue (DT-110) |
| Última actualización · HU-45 Listo | 2026-11-12 · Pablo (con Claude Code) · rama `docs/DT-157-estados-hu-listo`: nota aditiva en PROC-08, HU-45 en **Listo** (según Pablo, confirmado por Sebas) |
| Última actualización · HU-46 Listo | 2026-11-12 · Pablo (con Claude Code) · rama `docs/DT-157-estados-hu-listo`: nota aditiva en PROC-08, HU-46 en **Listo** (decisión de Pablo) |
| Última actualización lote 4 · merge PR #22 | 2026-11-12 · Pablo (con Claude Code) · rama `docs/DT-157-estados-hu-listo`: notas aditivas en PROC-03 y PROC-05: HU-15, HU-16, HU-29 y HU-30 en **Listo** (PR #22 auditado (§11: apta según el comentario de Pablo en el PR #22, "Auditoría §11: apta, 12-nov", publicado el 2026-11-13) y fusionado, `c64b41a`) |
| Última actualización lote 4 · Ronda 8 | 2026-11-12 · Pablo (con Claude Code) · notas aditivas en PROC-03 y PROC-05: validación visual de HU-15, HU-16, HU-29 y HU-30 aprobada por Pablo (V-86 a V-95) |
| Última actualización lote 3 · merge PR #21 | 2026-11-11 · Pablo (con Claude Code) · nota aditiva en PROC-04: HU-19, HU-20 y HU-25 en **Listo** (PR #21 auditado y fusionado, `5ed0e3b`) |
| Última actualización lote 3 · Ronda 7 | 2026-11-11 · Pablo (con Claude Code) · nota aditiva en PROC-04: validación visual de HU-19, HU-20 y HU-25 aprobada por Pablo (V-78 a V-85) |
| Última actualización · cierre HU-46 | 2026-11-11 · Pablo (con Claude Code) · rama `docs/HU-46-cierre`: nota aditiva en PROC-08 con el registro humano de V-44 |
| Última actualización aditiva HU-09 | 2026-11-11 · V-45 aprobada por Sebas el 2026-11-10; HU-09 con 2/2 criterios validados en la rama |
| Última actualización aditiva HU-46 | 2026-11-06 · PROC-08 registra I-02 y la sesión D-05; V-44 Pendiente |
| Propósito | Ver en un solo lugar **qué proceso de la empresa** cubre cada historia, con su épica, RF, RNF y pantalla, y **definir nuestro 60 %** para la entrega del 14 de noviembre de 2026 |
| Fecha | 2026-10-31 |
| Última actualización | 2026-11-09 (noche) · Pablo (con Claude Code) · rama `feat/URB-20-21-35-36-HU-15-HU-16-HU-29-HU-30-contactos-crm` (lote 4): §4, columna **Código** de PROC-03 (HU-15, HU-16) y PROC-05 (HU-29, HU-30), con el texto anterior tachado; rama sin fusionar. Antes: 2026-11-08 (noche) · Pablo (con Claude Code) · rama `docs/post-merge-pr15` (PR #18): §2, **plan de reparto** (PLAN, sin avance). Antes: 2026-11-06 · rama `docs/post-merge-pr15`: merge de `origin/develop` conservando filas del mapa y la traza de HU-45. Se mantiene la nota del PR #15 (HU-27 y HU-34 ya no son "Rama sin fusionar"), se actualiza HU-12 en §4 (PR #14 ya está en `develop`) y se aclara la nota de PROC-08/HU-45 de la rama `origin/develop`. Antes: 2026-11-05 · Sebas (con Copilot) · PROC-08/HU-45: se aclara que la fila inicial sobre el desbloqueo es histórica y que la actualización del 2026-11-04 describe el flujo implementado; notificación pendiente referida a DT-120. Antes: 2026-11-04 (tras el merge del PR #15) · Pablo (con Claude Code) · rama `docs/post-merge-pr15`: §4, HU-27 (PROC-03 paso 5) y HU-34 (PROC-05 paso 1) ya no son "Rama sin fusionar" (fusionadas en `develop`, `043cfb5`, DS-32) y su columna Estado enlaza a Estado de procesos. Antes: 2026-11-03 · Pablo (con Claude Code) · §4: columna **Código** completada contra `develop` (`d71c7f2`, con el PR #9 de HU-44 fusionado) y contra las ramas sin fusionar de HU-12, HU-27 y HU-34; anclas `#hu-xx` verificadas contra los encabezados de Estado de procesos (las de HU-27 y HU-34 no existían); §6 fila 7: C-08 confirmada (DS-30). El corte del 60 % (§2) y el resto del §6 siguen como **PROPUESTA** |
| Actualización aditiva HU-45 | 2026-11-03 · Se agrega la fila de implementación del desbloqueo en PROC-08; no se modifican las filas ya existentes |
| Actualización HU-45 y V-43 | 2026-11-04 · Se agrega una fila vigente para los dos criterios validados por Sebas en V-43; no se modifican las filas anteriores |
| Fuentes | User Story Mapping de Miro (exportado el 2026-10-31); tesis `ProyectoCapstoneV4 (3).md` (RF-01 a RF-16, Anexo 2); [Contexto maestro](URBANEX_MASTER_CONTEXT.md) (§4 RF/RNF, pantallas, §10 backlog) |
| Rama | `docs/user-story-mapping` (PR #13, borrador) |
| Regla | **Este documento no copia estados.** El avance vive en [Estado de procesos](URBANEX_ESTADO_PROCESOS.md) y [Avance de épicas](URBANEX_AVANCE_EPICAS.md); la evidencia (V-xx), en [`Project_Progress.md`](../../Project_Progress.md); los archivos y su riesgo, en el [GPS](URBANEX_GPS_ARCHIVOS.md). Aquí solo se enlazan |

**Leyenda de roles (colores del mapa):** 🟩 Asesor/Admin · 🟦 Asesor · 🟪 Administrador · 🟨 Cliente (sin cuenta).
**Marcas:** **[PROPUESTA]** = interpretación del equipo, no está en la tesis · **[CORRECCIÓN]** = cambio respecto del Miro o de un borrador.

---

## 1. El mapa (6 etapas del flujo de valor)

Cada columna es una etapa del User Story Mapping (Anexo 2). Entre paréntesis, los puntos de historia. Las historias en **negrita** entran en el corte propuesto del 60 % (§2).

| A1 · Captación, publicación y avalúo | A2 · Exploración del portafolio | A3 · Contacto y agendamiento | A4 · Seguimiento de oportunidades | A5 · Negociación y documentación | A6 · Cierre, administración y supervisión |
|---|---|---|---|---|---|
| 🟩 **HU-01** Registrar propiedad (5) | 🟨 **HU-10** Explorar catálogo con filtros (5) | 🟨 **HU-15** Contacto por WhatsApp (3) | 🟦 HU-26 Conversaciones pendientes (3) | 🟦 HU-35 Abono de reserva (3) | 🟪 HU-40 Confirmar cierre (5) |
| 🟩 **HU-02** Captador y responsable inicial (2) | 🟨 **HU-11** Ficha de detalle (3) | 🟨 **HU-16** Interés por formulario (2) | 🟩 **HU-27** Abrir contacto y oportunidad (3) | 🟩 HU-36 Cargar y reemplazar documentación (3) | 🟪 HU-41 Acuerdo de comisión (3) |
| 🟩 **HU-03** Documentación inicial (2) | 🟨 **HU-12** Compartir ficha por URL (2) | 🟨 **HU-17** Contacto por Messenger (5) | 🟪 HU-28 Asignar/reasignar asesor (3) | 🟪 HU-37 Aprobar/Rechazar documento (3) | 🟪 HU-42 Revertir reserva caída (3) |
| 🟩 **HU-05** Características del inmueble (3) **[CORRECCIÓN]** | 🟨 **HU-13** Interés en reservada (3) | 🟨 **HU-18** Disponibilidad del asesor (3) | 🟦 **HU-29** Avanzar estado (5) | 🟩 HU-38 Consultar documentación (2) | 🟪 HU-43 Reabrir oportunidad cerrada (3) |
| 🟩 **HU-04** Seleccionar comparables (3) | 🟨 **HU-14** Aviso si se libera la reserva (2) | 🟨 **HU-19** Solicitar visita (5) | 🟦 **HU-30** Interacciones y negociación (5) | 🟩 HU-39 Alertas documentales (3) | 🟪 **HU-44** Usuarios internos (3) |
| 🟩 **HU-06** Valor sugerido del motor (5) | | 🟨 **HU-20** Confirmación de visita (3) | 🟦 HU-31 Marcar Perdida (2) | | 🟪 **HU-45** Desbloquear cuenta (2) |
| 🟩 **HU-07** Borrador de justificación (3) | | 🟨 **HU-21** Cancelar visita (3) | 🟦 HU-32 Recordatorios (5) | | 🟩 **HU-46** Sesión y recuperar contraseña (3) |
| 🟩 **HU-08** Calibrar y aprobar avalúo (5) | | 🟦 **HU-22** Definir disponibilidad (3) | 🟩 HU-33 Consultar oportunidad (3) | | 🟪 HU-47 Reasignar propiedades (3) |
| 🟩 **HU-53** Publicar propiedad (3) | | 🟦 **HU-23** Registrar/reprogramar visita (3) | 🟩 HU-34 Buscar con filtros (3) | | 🟪 HU-48 Asignaciones anteriores (2) |
| 🟩 **HU-09** Actualizar propiedad publicada (2) | | 🟦 **HU-24** Agenda de visitas (2) | | | 🟪 HU-49 Registro de auditoría (3) |
| | | 🟦 **HU-25** Resultado de la visita (2) | | | 🟪 HU-50 Avalúos anteriores (2) |
| | | | | | 🟪 HU-51 Inventario y carga (3) |
| | | | | | 🟪 HU-52 Cierres y conversión (3) |
| **33 pts · 10 HU** | **15 pts · 5 HU** | **34 pts · 11 HU** | **32 pts · 9 HU** | **14 pts · 5 HU** | **38 pts · 13 HU** |

Total: **53 HU · 166 pts** (EP-1 8 + EP-2 33 + EP-3 15 + EP-4 34 + EP-5 32 + EP-6 44). HU-44 a HU-46 (EP-1) están en la columna A6 del mapa, pero se planificaron en el Sprint 1.

**[CORRECCIÓN] HU-05:** el mapa de Miro tenía 52 tarjetas; faltaba "Registrar las características del inmueble" (HU-05, 3 pts, RF-11). Se agrega en A1, antes de "Seleccionar comparables", porque los datos estructurados alimentan el motor. **Pendiente:** agregar la tarjeta también en Miro.

---

## 2. Nuestro 60 % — criterio y corte **[PROPUESTA]**

**Criterio:** por **puntos de historia** del backlog, siguiendo el orden del flujo (columnas del mapa) y la **prioridad** de cada HU. La línea que trazó el profesor en la reunión (hasta "Seguimiento de oportunidades") fue un cálculo aproximado; este es el cálculo del equipo.

**Meta:** 60 % de 166 pts = **99,6 → 100 pts**.

**Corte propuesto (103 pts = 62,0 %):**

| Bloque | HU | Pts |
|---|---|---|
| EP-1 Acceso y usuarios (base de todo el sistema) | HU-44, 45, 46 | 8 |
| A1 completa (captación, avalúo, publicación) | HU-01 a 09, HU-53 | 33 |
| A2 completa (exploración del portafolio) | HU-10 a 14 | 15 |
| A3 completa (contacto y agendamiento) | HU-15 a 25 | 34 |
| A4, solo prioridad **Alta** (núcleo del seguimiento) | HU-27, 29, 30 | 13 |
| **Total** | **31 HU** | **103 (62,0 %)** |

Por qué este corte: cubre de punta a punta el recorrido del cliente hasta que el asesor toma la oportunidad y la hace avanzar (PROC-01 a PROC-04 completos y el núcleo de PROC-05). Lo que queda fuera (A5, A6 salvo EP-1, y lo Media de A4) depende de que exista el ciclo de estados de la oportunidad.

Alternativas consideradas:
- **Solo prioridad Alta en todo el backlog:** 92 pts (55,4 %), no llega.
- **Cambiar HU-07 (borrador IA, Media, 3) por HU-34 (filtros de oportunidades, Media, 3, ya implementada):** mismo total, 103. Útil si el servicio de IA no se integra a tiempo.

**Cómo se mide el avance hacia el 60 %:** una HU cuenta solo cuando está **completa** según la regla de [Avance de épicas](URBANEX_AVANCE_EPICAS.md) (todos sus criterios implementados, verificados y validados por una persona). El porcentaje actual se calcula allí; este documento no lo copia.

**Pendiente de decidir:** aprobación de Pablo y Sebas, y comunicarlo al tutor Eddy (está en sus preguntas).

**Plan de reparto (2026-11-08, decisión de Pablo) [PLAN, sin avance]:** Sebas → HU-09 (2 pts) y luego HU-10 (5 pts); Pablo → lote 3: HU-19, HU-20 y HU-25 (10 pts, PROC-04), y lote 4: HU-15, HU-16, HU-29 y HU-30 (15 pts, PROC-03 y PROC-05). Todas están dentro del corte propuesto. No cambia el porcentaje: se cuenta en [Avance de épicas §8](URBANEX_AVANCE_EPICAS.md#8-plan-de-reparto-2026-11-08-plan) cuando cada HU esté completa.

---

## 3. Procesos de la empresa **[PROPUESTA]**

Los procesos oficiales están aquí: [URBANEX_PROCESOS_EMPRESA.md](URBANEX_PROCESOS_EMPRESA.md) y [URBANEX_CHECKLIST_TOBE.md](URBANEX_CHECKLIST_TOBE.md).

La tesis describe los procesos, pero no los numera. Los códigos son nuestros. Se usa **PROC-xx** (no "PR-xx") para no confundirlos con los pull requests.

### 3.1 Cómo trabaja hoy la empresa (AS-IS) y qué necesidad ataca el sistema

| AS-IS | Proceso actual | Dolor (fuente: M. Peñaherrera, abril 2026) | Necesidad | PROC |
|---|---|---|---|---|
| AS-1 | Captación de inmuebles: el asesor levanta y fotografía la ficha | — | E1, E5 | PROC-01 |
| AS-2 | Promoción en Facebook Marketplace | Información técnica incompleta | E1 Exposición del portafolio | PROC-02 |
| AS-3 | Consultas por Messenger y luego WhatsApp | Respuesta de 1 a 4 h | E2, E3 | PROC-03 |
| AS-4 | Agendamiento manual por WhatsApp | 5 a 12 mensajes por visita | E2 Contacto y agendamiento | PROC-04 |
| AS-5 | Seguimiento sin registro centralizado | 2 a 3 h diarias por asesor; contactos perdidos | E3 Trazabilidad | PROC-05, PROC-06 |
| AS-6 | Documentos en físico o carpetas locales | 2 a 4 h por transacción | E4 Control documental | PROC-06 |
| AS-7 | Avalúo empírico | Variabilidad entre asesores | E5 Evaluación comercial | PROC-01 |
| AS-8 | Cierre y co-intermediación manual | Sin registro de comisión ni carga por asesor | E3 | PROC-07, PROC-08 |

### 3.2 Procesos con el sistema (TO-BE)

| PROC | Proceso | Etapa USM | Épica | RF | RNF | Estado del proceso |
|---|---|---|---|---|---|---|
| PROC-01 | Captación, avalúo y publicación de la propiedad | A1 | EP-2 | RF-01, 08, 10, 11 | RNF-03, 04, 07 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-02 | Exploración del portafolio | A2 | EP-3 | RF-01, 03, 07 | RNF-01, 02, 03, 06 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-03 | Captación multicanal de contactos | A3, A4 | EP-4, EP-5 | RF-02, 03, 05 | RNF-02, 04, 07 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-04 | Agendamiento y gestión de visitas | A3 | EP-4 | RF-04, 09 | RNF-02 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-05 | Seguimiento de la oportunidad comercial | A4 | EP-5 | RF-05, 06, 08, 16 | RNF-04 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-06 | Reserva y documentación de la transacción | A5 | EP-6 | RF-06, 10 | RNF-04 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-07 | Cierre, co-intermediación, reversión y reapertura | A6 | EP-6 | RF-07 | RNF-04 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |
| PROC-08 | Administración, supervisión y auditoría | A6 | EP-1, EP-6 | RF-08, 11, 12, 13, 14, 15 | RNF-04, 05 | → [Estado](URBANEX_ESTADO_PROCESOS.md) |

RNF-05 (mantenibilidad) y RNF-06 (disponibilidad) son transversales: se comprueban en el despliegue (URB-55), no por proceso.

---

## 4. Cada proceso, paso a paso (¿el software refleja el proceso?)

Para cada paso: qué HU lo cubre, en qué pantalla y en qué código vive. **El estado se mira en el enlace**; si un paso no tiene HU implementada, es un **hueco** del proceso.

La columna **Código** la completa Claude Code leyendo el repositorio (archivos y endpoints, **sin números de línea**, porque cambian con cada commit). El detalle de cada archivo está en el [GPS](URBANEX_GPS_ARCHIVOS.md).

**Cómo leer la columna Código (revisada el 2026-11-03 contra `develop`, `d71c7f2`):**
- Las rutas de backend son relativas a `backend/apps/` y las de frontend, a `frontend/`. Los endpoints cuelgan de `/api/`.
- **Parcial:** existe código, pero falta una parte del paso; se cita el DT o el motivo ya documentado.
- **Rama sin fusionar:** el código existe solo en la rama indicada, no en `develop`.
- **No implementado:** no hay código en `develop` ni en las ramas remotas revisadas.
- En **Estado**, "—" significa que la HU todavía no tiene sección en Estado de procesos ni en Avance de épicas (este último cubre solo EP-1 y EP-2).

### PROC-01 · Captación, avalúo y publicación

| # | Paso del proceso | HU | Pantalla | Código (archivos / endpoint) | Estado |
|---|---|---|---|---|---|
| 1 | El asesor registra la propiedad (queda En captación) | HU-01 | I-10 | `users/models.py` (`Property`, `PropertyImage`), `users/serializers.py` (`PropertySerializer`), `users/views.py` (`PropertyListCreateView`, `MyPropertiesView`, `PropertyDetailView`, `PropertyImageViewSet`) · `POST auth/properties/`, `GET auth/properties/mine/`, `auth/property-images/` · `app/dashboard/page.tsx` (modal I-10), `types/property.ts` | [HU-01](URBANEX_ESTADO_PROCESOS.md#hu-01) |
| 2 | Queda como captador y responsable inicial | HU-02 | I-10 | **Parcial:** `users/views.py` (`PropertyListCreateView.perform_create` asigna `agent` al asesor autenticado), `users/models.py` (`Property.agent`). Un solo campo hace de captador y de responsable (DT-17); desactivar al asesor lo borra (DT-115) | [HU-02](URBANEX_ESTADO_PROCESOS.md#hu-02) |
| 3 | Carga la documentación inicial (corretaje, catastro) | HU-03 | I-10 (pestaña Expediente), I-13 | `documents/models.py` (`Document`, `upload_new_version`), `documents/serializers.py`, `documents/views.py` (`DocumentViewSet`) · `GET/POST documents/` · `app/dashboard/page.tsx` (pestaña Expediente) | [HU-03](URBANEX_ESTADO_PROCESOS.md#hu-03) |
| 4 | Registra las características estructuradas | HU-05 | I-10 / I-11 | **Parcial:** `users/models.py` (`property_type`, `area_m2`, `bedrooms`, `bathrooms`, `parking_spaces`, `latitude`, `longitude`), `appraisals/services.py` (`subject_blocker`) · `app/dashboard/page.tsx` (pestañas General y Ubicación), `components/MapPicker.tsx`. Faltan campos de RF-01 (DT-19) | [HU-05](URBANEX_ESTADO_PROCESOS.md#hu-05) |
| 5 | Selecciona 3 a 5 comparables (o registro manual) | HU-04 | I-11 | `appraisals/services.py` (`find_candidates`), `appraisals/views.py` (`candidates`), `appraisals/serializers.py` (`comparables`) · `GET appraisals/candidates/` · `app/dashboard/properties/[id]/appraisal/comparables/page.tsx` | [HU-04](URBANEX_ESTADO_PROCESOS.md#hu-04) |
| 6 | El motor calcula el valor sugerido y la confianza | HU-06 | I-12 | `appraisals/engine/` (`calculator.py`, `factors.py`, `theta.py`), `appraisals/models.py` (`EngineParameters`, `Appraisal.create_draft`), `appraisals/admin.py` (θ) · `POST appraisals/` · `app/dashboard/properties/[id]/appraisal/page.tsx`, `types/appraisal.ts` | [HU-06](URBANEX_ESTADO_PROCESOS.md#hu-06) |
| 7 | La IA redacta el borrador de justificación | HU-07 | I-12 | **No implementado.** Solo existe el campo `ai_draft_justification` en `appraisals/models.py`; no hay servicio de IA | [Avance](URBANEX_AVANCE_EPICAS.md) |
| 8 | El asesor calibra y aprueba (inmutable) | HU-08 | I-12 | `appraisals/models.py` (`Appraisal.calibrate`, `approve`, `MUTABLE_FIELDS`), `appraisals/serializers.py`, `appraisals/views.py` (`AppraisalViewSet`) · `PATCH appraisals/<id>/`, `POST appraisals/<id>/approve/` · `app/dashboard/properties/[id]/appraisal/page.tsx` | [HU-08](URBANEX_ESTADO_PROCESOS.md#hu-08) |
| 9 | Publica (avalúo + corretaje) → Disponible | HU-53 | I-10B | `users/views.py` (`get_missing_publication_requirements`, `PropertyPublishView`, `PropertyPublicationRequirementsView`) · `POST auth/properties/<id>/publish/`, `GET auth/properties/<id>/publication-requirements/` · `app/dashboard/page.tsx` (`handlePublish`), `components/Dialog.tsx` | [HU-53](URBANEX_ESTADO_PROCESOS.md#hu-53) |
| 10 | Actualiza precio/estado; No disponible con motivo | HU-09 | I-05, I-10 | **Parcial:** `PATCH auth/properties/<id>/` (`PropertyDetailView`) actualiza los datos; `PropertySerializer` tiene `unavailability_reason`, pero `status` es de solo lectura y no existe la acción para cambiar el estado (DT-44) | [HU-09](URBANEX_ESTADO_PROCESOS.md#hu-09) |

### PROC-02 · Exploración del portafolio

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | El cliente filtra el catálogo (solo Disponible/Reservado) | HU-10 | P-01, P-02 | **Parcial:** `users/views.py` (`PropertyListCreateView` con `PUBLIC_STATUSES` para anónimos) · `GET auth/properties/` · `app/properties/page.tsx`, `components/PropertyCard.tsx`, `lib/api.ts` (`getProperties`). Sin filtros | — |
| 1 (actualización 2026-11-11, DS-16) | El cliente combina filtros y recorre el catálogo paginado | HU-10 | P-02 | **Rama sin fusionar** `feat/URB-16-HU-10-catalogo-filtros`: `users/views.py` (`PropertyCatalogQuerySerializer`, `PropertyCatalogPagination`, `PropertyListCreateView`) · `GET auth/properties/` devuelve `count/next/previous/results`; filtros por campos existentes. `app/properties/page.tsx`, `components/PropertyCard.tsx`, `lib/api.ts` (`getProperties`), `types/property.ts`. La fila inicial queda como antecedente | [HU-10](URBANEX_ESTADO_PROCESOS.md#hu-10) |
| 1 (ampliación de usabilidad 2026-11-11) | Ajusta la búsqueda desde celular o escritorio | HU-10 | P-02 | Misma rama sin fusionar: `components/CatalogFilters.tsx` (panel móvil/lateral), `lib/catalogFilters.ts` y `catalogFilters.test.mjs` (decimales); `users/management/commands/setup_catalog_demo.py` prepara ejemplos locales y publica mediante HU-53 sin cambiar usuarios | [HU-10](URBANEX_ESTADO_PROCESOS.md#hu-10) |
| 1 (rediseño de barra superior 2026-11-11) | Aplica, cancela y elimina filtros desde la barra superior | HU-10 | P-02 | Misma rama: `CatalogFilters.tsx` sustituye el lateral por barra adherente, paneles y diálogo móvil; `catalogFilters.ts` combina query y valida borradores/rango, `PropertyCard.tsx` compacta tarjetas. Conserva API, DS-16 y páginas de 20. Las filas previas son antecedentes | [HU-10](URBANEX_ESTADO_PROCESOS.md#hu-10) |
| 1 (slider e histograma 2026-11-12) | Ajusta el rango con una pista de dos controles y consulta concentración de precios; filtra parqueaderos | HU-10 | P-02 | `users/views.py` (`catalog_price_distribution`, catálogo) agrega conteos agregados antes de precio y mínimo `parking_spaces`; `CatalogFilters.tsx`, `lib/catalogFilters.ts`, `types/property.ts`, `app/properties/page.tsx` conectan histograma, controles y URL. Misma rama sin fusionar; sin campos nuevos | [HU-10](URBANEX_ESTADO_PROCESOS.md#hu-10) |
| 1 (preferencias 2026-11-12) | Elige sin restricción o cantidad de habitaciones/baños/parqueaderos | HU-10 | P-02 | `CatalogFilters.tsx`, `lib/catalogFilters.ts` y `users/views.py` evolucionan la selección: habitaciones/baños mínimos; parqueaderos 0/1/2 exactos, 3+; Sin preferencia elimina el parámetro. Misma rama sin fusionar, sin modelo nuevo | [HU-10](URBANEX_ESTADO_PROCESOS.md#hu-10) |
| 1 (orden y simplificación 2026-11-13) | Ordena por precio o recientes, confirma mínimos o los desmarca | HU-10 | P-02 | `users/views.py` agrega sort validado/estable sobre todas las coincidencias; `CatalogFilters.tsx`, `lib/catalogFilters.ts`, `types/property.ts`, `app/properties/page.tsx` conservan orden/filtros en URL, muestran importe del slider y eliminan explicaciones visibles. Parqueaderos vuelve a mínimos positivos por decisión posterior de Sebas, sin cero en UI | [HU-10](URBANEX_ESTADO_PROCESOS.md#hu-10) |
| 2 | Consulta la ficha (precio referencial) | HU-11 | P-03 | `users/views.py` (`PropertyDetailView`, `PUBLIC_STATUSES`) · `GET auth/properties/<id>/` · `app/properties/[id]/page.tsx`, `lib/api.ts` (`getPropertyById`) | — |
| 3 | Comparte la URL con metaetiquetas | HU-12 | P-03 | ~~**Rama sin fusionar** (`feat/URB-17-HU-12-compartir-ficha`):~~ (2026-11-06: fusionada en `develop` por el PR #14) `lib/propertyMetadata.ts` (`buildPropertyMetadata`), `app/properties/[id]/page.tsx` (`generateMetadata`) | — |
| 4 | Si está Reservada, deja su interés (Lista de Interesados) | HU-13 | P-04, P-06 | No implementado | — |
| 5 | Recibe aviso si la reserva se libera | HU-14 | (notificación) | No implementado | — |

**Nota (2026-11-12, decisión de Pablo, DT-157):** el paso 3 (HU-12) pasa a **Listo**: PR #14 fusionado (`18c150d`), V-60 a V-62 y V-64 aprobadas; V-63 **No aplicable hasta el despliegue (DT-110)**.

### PROC-03 · Captación multicanal de contactos

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | Contacto por WhatsApp (nombre y teléfono antes de redirigir) | HU-15 | P-03, P-05 | ~~No implementado~~ (2026-11-09) `opportunities/services.py` (`agent_whatsapp_number`), `GET /api/opportunities/public/properties/<id>/whatsapp/`; `frontend/components/WhatsAppContactButton.tsx` en P-07 (rama sin fusionar, lote 4). Sin registro previo a la redirección (simplificación, DS-50) | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-15) |
| 2 | Interés por formulario (con LOPDP) | HU-16 | P-05 | ~~No implementado~~ (2026-11-09) `register_web_interest`, `POST /api/opportunities/public/properties/<id>/interest/`; `frontend/components/InterestForm.tsx` en P-07 (rama sin fusionar, lote 4) | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-16) |
| 3 | Messenger: respuesta automática que pide el número | HU-17 | (webhook), I-04 | No implementado | — |
| 4 | El asesor atiende conversaciones sin número | HU-26 | I-04, I-04A | No implementado | — |
| 5 | El asesor abre contacto y oportunidad a mano | HU-27 | I-07 | ~~**Rama sin fusionar** (`feat/URB-30-34-HU-27-HU-34-oportunidades`):~~ (2026-11-04: fusionada en `develop` por el PR #15, `043cfb5`, DS-32) `opportunities/models.py`, `opportunities/services.py`, `opportunities/validators.py`, `opportunities/serializers.py`, `opportunities/views.py` (`OpportunityViewSet.create`, `eligible_properties`, `agents`) · `POST opportunities/`, `GET opportunities/eligible-properties/`, `GET opportunities/agents/` · `app/dashboard/opportunities/new/page.tsx`, `lib/opportunities.ts`, `types/opportunity.ts` | [HU-27](URBANEX_ESTADO_PROCESOS.md#hu-27) |

**Nota (2026-11-12, Ronda 8):** pasos 1 y 2 (HU-15 y HU-16) con validación visual aprobada por Pablo (V-86 a V-90, `Project_Progress.md`). Siguen en **Pruebas** y en la rama sin fusionar hasta la auditoría (§11) y el merge del PR #22.

**Nota (2026-11-12, merge del PR #22, DT-157):** los pasos 1 y 2 (HU-15 y HU-16) pasan a **Listo**: PR #22 auditado (§11: apta según el comentario de Pablo en el PR #22, "Auditoría §11: apta, 12-nov", publicado el 2026-11-13) y fusionado en `develop` (`c64b41a`). Donde las celdas dicen "rama sin fusionar, lote 4", ese código ya está en `develop`.

### PROC-04 · Agendamiento y visitas

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | El asesor define su disponibilidad y excepciones | HU-22 | I-09 | No implementado | — |
| 2 | El cliente ve los horarios libres | HU-18 | P-07 | No implementado | — |
| 3 | Solicita la visita → oportunidad en Visita Programada | HU-19 | P-07 | `backend/apps/visits/services.py` (`request_visit`), `POST /api/visits/properties/<id>/request/`; `frontend/components/FreeSlotsPicker.tsx`, `VisitRequestForm.tsx` (rama sin fusionar, PR #21) | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-19) |
| 4 | Recibe la confirmación (correo o WhatsApp) | HU-20 | P-08 | `send_visit_notifications`, `GET /api/visits/public/<token>/`; `frontend/app/visits/[token]/` (rama sin fusionar, PR #21) | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-20) |
| 5 | Puede cancelar antes de la hora | HU-21 | P-08 | No implementado | — |
| 6 | El asesor registra o reprograma visitas coordinadas | HU-23 | I-08 | No implementado | — |
| 7 | Consulta su agenda | HU-24 | I-08 | No implementado | — |
| 8 | Registra el resultado (realizada habilita el avance) | HU-25 | I-08 | `record_outcome`, `POST /api/visits/<id>/outcome/`; modal en `frontend/app/dashboard/agenda/page.tsx` (rama sin fusionar, PR #21). El avance a En Negociación es de HU-29 | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-25) |

**Nota (2026-11-11, Ronda 7):** pasos 3, 4 y 8 (HU-19, HU-20 y HU-25) con validación visual aprobada por Pablo (V-78 a V-85, `Project_Progress.md`). Siguen en **Pruebas** y en la rama sin fusionar hasta la auditoría (§11) y el merge del PR #21.

**Nota (2026-11-11, merge del PR #21):** los pasos 3, 4 y 8 (HU-19, HU-20 y HU-25) pasan a **Listo**: PR #21 auditado y fusionado en `develop` (`5ed0e3b`, por Pablo). Donde las celdas dicen "rama sin fusionar, PR #21", ese código ya está en `develop`.

### PROC-05 · Seguimiento de la oportunidad

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | El asesor ve su cartera (admin: todas) con filtros | HU-34 | I-06 | ~~**Rama sin fusionar** (`feat/URB-30-34-HU-27-HU-34-oportunidades`):~~ (2026-11-04: fusionada en `develop` por el PR #15, `043cfb5`, DS-32) `opportunities/views.py` (`OpportunityViewSet.get_queryset`, `filter_opportunities`, `OpportunityPagination`), `opportunities/serializers.py` · `GET opportunities/` · `app/dashboard/opportunities/page.tsx`, `lib/opportunities.ts` | [HU-34](URBANEX_ESTADO_PROCESOS.md#hu-34) |
| 2 | Consulta una oportunidad y su historial | HU-33 | I-06A | No implementado | — |
| 3 | Avanza el estado hasta Pendiente de Cierre (precio final) | HU-29 | I-06A | ~~No implementado~~ (2026-11-09) `advance_status`, `POST /api/opportunities/<id>/status/`; `frontend/app/dashboard/opportunities/[id]/page.tsx` (rama sin fusionar, lote 4). Corte sin Reservada ni Evaluación documental (C-09) | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-29) |
| 4 | Registra interacciones y negociación (no cambia el precio público) | HU-30 | I-06A | ~~No implementado~~ (2026-11-09) `OpportunityInteraction` (`opportunities.0003`), `add_interaction`, `GET`/`POST /api/opportunities/<id>/interactions/`; I-06A (rama sin fusionar, lote 4) | [Estado](URBANEX_ESTADO_PROCESOS.md#hu-30) |
| 5 | Marca Perdida con motivo | HU-31 | I-06A | No implementado | — |
| 6 | Recibe recordatorios (inactividad, visita, documento, asignación) | HU-32 | I-03 | No implementado | — |
| 7 | El admin asigna o reasigna con motivo | HU-28 | A-02 | No implementado | — |

**Nota (2026-11-12, Ronda 8):** pasos 3 y 4 (HU-29 y HU-30) con validación visual aprobada por Pablo (V-91 a V-95, `Project_Progress.md`). Siguen en **Pruebas** y en la rama sin fusionar hasta la auditoría (§11) y el merge del PR #22.

**Nota (2026-11-12, merge del PR #22, DT-157):** los pasos 3 y 4 (HU-29 y HU-30) pasan a **Listo**: PR #22 auditado (§11: apta según el comentario de Pablo en el PR #22, "Auditoría §11: apta, 12-nov", publicado el 2026-11-13) y fusionado en `develop` (`c64b41a`). Donde las celdas dicen "rama sin fusionar, lote 4", ese código ya está en `develop`.

### PROC-06 · Reserva y documentación

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | Registra el abono → inmueble Reservado | HU-35 | I-06A | No implementado | — |
| 2 | Carga y reemplaza documentos (versionados) | HU-36 | I-13 | **Parcial:** se reutiliza el versionado de HU-03, `documents/models.py` (`Document.upload_new_version`) · `POST documents/`; sin vínculo con la oportunidad | — |
| 3 | El admin aprueba o rechaza (bloquea el avance) | HU-37 | I-13 | **Parcial:** solo el modelo, `documents/models.py` (`Document.validate_document`); sin endpoint ni pantalla | [HU-37](URBANEX_ESTADO_PROCESOS.md#hu-37) |
| 4 | Consulta documentos por tipo (URL firmada) | HU-38 | I-13 | **Parcial:** descarga protegida provisional, `documents/views.py` (`DocumentViewSet.file`) · `GET documents/<id>/file/`; sin URL firmada | — |
| 5 | Recibe alertas de faltantes o por vencer (≤ 30 días) | HU-39 | I-13, I-03 | **Parcial:** `documents/models.py` (`EXPIRATION_ALERT_DAYS`, `expiring_soon`, `is_expiring_soon`); sin alertas ni pantalla | — |

### PROC-07 · Cierre, comisión, reversión y reapertura

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | El admin confirma el cierre y el precio final | HU-40 | A-03 | No implementado | — |
| 2 | Si hay co-intermediación, registra la comisión | HU-41 | A-03 | No implementado | — |
| 3 | Revierte una reserva caída y avisa a interesados | HU-42 | A-03 | No implementado | — |
| 4 | Reabre una oportunidad cerrada | HU-43 | A-03 | No implementado | — |

### PROC-08 · Administración, supervisión y auditoría

| # | Paso | HU | Pantalla | Código | Estado |
|---|---|---|---|---|---|
| 1 | Inicia sesión y recupera contraseña | HU-46 | I-01, I-02 | **Parcial:** `users/views.py` (`LoginView`) · `POST auth/login/` · `app/(auth)/login/page.tsx`, `lib/auth-session.ts`, `lib/api.ts` (`authFetch`), `components/SiteNav.tsx` (cierre de sesión). La recuperación de contraseña (I-02) no está implementada | [HU-46](URBANEX_ESTADO_PROCESOS.md#hu-46) |
| 1 (actualización 2026-11-06) | Inicia sesión y recupera contraseña | HU-46 | I-01, I-02 | `User.password_changed_at`, `PasswordResetToken`, autenticación JWT con invalidación por cambio de contraseña, endpoints de solicitud/confirmación, refresh HttpOnly con CSRF, `forgot-password/page.tsx`, `reset-password/page.tsx`, `lib/api.ts` y `SiteNav.tsx` | Implementación y suite automática verificadas en SQLite; validación funcional/visual V-44 Pendiente | [HU-46](URBANEX_ESTADO_PROCESOS.md#hu-46) |
| 2 | Gestiona usuarios internos | HU-44 | A-01 | `users/models.py` (`User`, `UserActivationToken`), `users/serializers.py` (`ManagedUserSerializer`), `users/views.py` (`UserListCreateView`, `UserDetailView`, `UserDeactivateView`, `UserResendActivationView`, `UserActivationView`) · `GET/POST auth/users/`, `GET/PATCH auth/users/<id>/`, `POST auth/users/<id>/deactivate/`, `POST auth/users/<id>/resend-activation/`, `POST auth/users/activate/` · `app/dashboard/users/page.tsx`, `app/activate/page.tsx`, `types/user.ts` | [HU-44](URBANEX_ESTADO_PROCESOS.md#hu-44) |
| 3 | Desbloquea cuentas | HU-45 | A-01 | **Parcial:** `users/views.py` (`LoginView` bloquea tras 5 intentos con `failed_attempts` e `is_locked`). El desbloqueo por el admin no está implementado | [HU-45](URBANEX_ESTADO_PROCESOS.md#hu-45) |
| 3 (actualización 2026-11-03) | Desbloquea cuentas | HU-45 | A-01 | `users/views.py` (`LoginView`, `UserUnlockView`) · `POST auth/users/<id>/unlock/` · `users/urls.py` · `app/dashboard/users/page.tsx` | [HU-45](URBANEX_ESTADO_PROCESOS.md#hu-45) |
| 3 (actualización 2026-11-04) | Bloquea y desbloquea cuentas | HU-45 | A-01, I-01 | `LoginView` bloquea tras cinco intentos; `UserUnlockView` permite desbloqueo solo al admin · mensajes de login neutrales y limpieza de contraseña tras 401 · ambos criterios comprobados por Sebas en V-43 | [HU-45](URBANEX_ESTADO_PROCESOS.md#hu-45) |
| 4 | Reasigna propiedades | HU-47 | A-02 | No implementado | — |
| 5 | Consulta asignaciones anteriores | HU-48 | A-02 | No implementado | — |
| 6 | Consulta la auditoría | HU-49 | A-04 | No implementado | — |
| 7 | Compara avalúos (motor vs calibrado) | HU-50 | A-05 | No implementado (solo el admin de Django de solo lectura, `appraisals/admin.py`; no es la pantalla A-05) | — |
| 8 | Ve inventario y carga por asesor | HU-51 | A-06 | No implementado | — |
| 9 | Analiza cierres y conversión digital | HU-52 | A-06 | No implementado | — |

**Aclaración aditiva HU-45 (2026-11-05):** la fila inicial de PROC-08 registra el estado previo a implementar el desbloqueo por admin y queda supersedida por las actualizaciones del 2026-11-03 y 2026-11-04, que documentan `UserUnlockView`, `POST auth/users/<id>/unlock/` y la acción en A-01. La actualización del 2026-11-04 también registra el comportamiento neutral del login.

**Actualización aditiva HU-46 (2026-11-11):** la fila "1 (actualización 2026-11-06)" dice "V-44 Pendiente"; ya no es así. Sebas registró V-44 en `Project_Progress.md` como Aprobado en tres filas: 2026-11-07, 16:19, los cinco pasos originales (`evidence/HU-46/Screenshot 2026-11-07 161628.png`); 2026-11-09, 15:13:56, recuperación con desbloqueo y contador en cero (`evidence/ResetPasswordUsuarioBloqueado.png`); y 2026-11-09, 16:13:56, invalidación de la sesión anterior tras recuperar la contraseña (`evidence/HU-46/ResetPasswordUsuarioBloqueado.png`). Es la transcripción de su registro, no una validación nueva del agente.

**Actualización aditiva HU-46 (2026-11-12, decisión de Pablo, DT-157):** HU-46 pasa a **Listo**. Respaldo: auditoría §11 del PR #20 (con la corrección posterior de precisión de JWT registrada el 2026-11-09), V-44 aprobada por Sebas (filas del 2026-11-07 y del 2026-11-09 en `Project_Progress.md`), PR #20 fusionado en `develop` (`47d09ed`) y PR #23 con su cierre documental (`97f0e0c`). No se modifican las filas anteriores de Sebas.

**Nota (2026-11-13, decisión de Pablo, DS-35):** el criterio "solo los usuarios activos inician sesión" de HU-46 queda cubierto por la salida de `apps.users.tests.UserManagementApiTests.test_inactive_users_cannot_log_in` (`backend/apps/users/tests.py:1361`; "Ran 1 test … OK", exit 0, SQLite, 2026-11-13). EP-1 pasa a 2/3 HU · 5/8 pts (Avance de épicas §3).

**Actualización aditiva HU-45 (2026-11-12, DT-157):** HU-45 pasa a **Listo**. Según Pablo (2026-11-12), Sebas confirmó que está terminada: V-43 aprobada por Sebas (2026-11-04 y 2026-11-06) y PR #17 fusionado en `develop` (`94843c7`). DT-120 (notificación persistente al administrador) queda abierto aparte.

---

## 5. Matriz por épica (HU → RF, prioridad, puntos)

| Épica | HU | Pts | Prioridad | RF | PROC |
|---|---|---|---|---|---|
| EP-1 Acceso y usuarios (8) | HU-44 | 3 | Alta | RF-12 | PROC-08 |
| | HU-45 | 2 | Alta | RF-13 | PROC-08 |
| | HU-46 | 3 | Alta | RF-13 | PROC-08 |
| EP-2 Propiedades y avalúos (33) | HU-01 | 5 | Alta | RF-01, RF-08 | PROC-01 |
| | HU-02 | 2 | Alta | RF-01, RF-08 | PROC-01 |
| | HU-03 | 2 | Alta | RF-10 | PROC-01 |
| | HU-04 | 3 | Alta | RF-11 | PROC-01 |
| | HU-05 | 3 | Alta | RF-11 | PROC-01 |
| | HU-06 | 5 | Alta | RF-11 | PROC-01 |
| | HU-07 | 3 | Media | RF-11 | PROC-01 |
| | HU-08 | 5 | Alta | RF-11 | PROC-01 |
| | HU-09 | 2 | Alta | RF-01 | PROC-01 |
| | HU-53 | 3 | Alta | RF-01, RF-10, RF-11 | PROC-01 |
| EP-3 Exploración (15) | HU-10 | 5 | Alta | RF-01 | PROC-02 |
| | HU-11 | 3 | Alta | RF-01 | PROC-02 |
| | HU-12 | 2 | Media | RF-01 (RNF-03) | PROC-02 |
| | HU-13 | 3 | Media | RF-03 | PROC-02 |
| | HU-14 | 2 | Media | RF-07 | PROC-02 |
| EP-4 Contacto y agendamiento (34) | HU-15 | 3 | Alta | RF-02 | PROC-03 |
| | HU-16 | 2 | Alta | RF-03 | PROC-03 |
| | HU-17 | 5 | Media | RF-05 | PROC-03 |
| | HU-18 | 3 | Alta | RF-09 | PROC-04 |
| | HU-19 | 5 | Alta | RF-04 | PROC-04 |
| | HU-20 | 3 | Alta | RF-04 | PROC-04 |
| | HU-21 | 3 | Media | RF-04 | PROC-04 |
| | HU-22 | 3 | Alta | RF-09 | PROC-04 |
| | HU-23 | 3 | Media | RF-04 | PROC-04 |
| | HU-24 | 2 | Media | RF-04 | PROC-04 |
| | HU-25 | 2 | Media | RF-04 | PROC-04 |
| EP-5 Seguimiento de oportunidades (32) | HU-26 | 3 | Media | RF-05 | PROC-03 |
| | HU-27 | 3 | Alta | RF-05 | PROC-03 |
| | HU-28 | 3 | Media | RF-08 | PROC-05 |
| | HU-29 | 5 | Alta | RF-06 | PROC-05 |
| | HU-30 | 5 | Alta | RF-06 | PROC-05 |
| | HU-31 | 2 | Media | RF-06 | PROC-05 |
| | HU-32 | 5 | Media | RF-16 | PROC-05 |
| | HU-33 | 3 | Media | RF-06 | PROC-05 |
| | HU-34 | 3 | Media | RF-06 | PROC-05 |
| EP-6 Negociación, cierre y supervisión (44) | HU-35 | 3 | Alta | RF-06 | PROC-06 |
| | HU-36 | 3 | Alta | RF-10 | PROC-06 |
| | HU-37 | 3 | Alta | RF-10 | PROC-06 |
| | HU-38 | 2 | Media | RF-10 | PROC-06 |
| | HU-39 | 3 | Media | RF-10 | PROC-06 |
| | HU-40 | 5 | Alta | RF-07 | PROC-07 |
| | HU-41 | 3 | Media | RF-07 | PROC-07 |
| | HU-42 | 3 | Media | RF-07 | PROC-07 |
| | HU-43 | 3 | Media | RF-07, RF-01 | PROC-07 |
| | HU-47 | 3 | Media | RF-08 | PROC-08 |
| | HU-48 | 2 | Baja | RF-08 | PROC-08 |
| | HU-49 | 3 | Media | RF-14 | PROC-08 |
| | HU-50 | 2 | Baja | RF-11 | PROC-08 |
| | HU-51 | 3 | Media | RF-15 | PROC-08 |
| | HU-52 | 3 | Media | RF-15 | PROC-08 |

RF sin HU propia: **RF-14** (auditoría) se alimenta de RF-01, 05, 06, 07, 08, 10, 11 y 12; su consulta es HU-49. El texto completo de cada RF y RNF está en el [Contexto maestro](URBANEX_MASTER_CONTEXT.md) §4; aquí no se repite.

---

## 6. Correcciones e inconsistencias detectadas (2026-10-31)

| # | Qué | Dónde | Decisión / estado |
|---|---|---|---|
| 1 | Faltaba la tarjeta de HU-05 en el mapa | Miro | **Corregido aquí**; falta agregarla en Miro |
| 2 | El borrador de contexto usaba "PR-01…PR-08" para los procesos | `urbanex-contexto-requerimientos.md` (borrador) | Renombrado a **PROC-01…PROC-08** |
| 3 | El borrador nombraba I-07 a I-10 como "registro de propiedades" | Borrador §8.2 | Se usan los del contexto maestro: I-07 apertura manual, I-08 agenda, I-09 disponibilidad, I-10 registro de propiedad |
| 4 | El borrador decía que en la reapertura "el inmueble queda Reservado" | Borrador §9.1 y §12.1 | **Error del borrador.** RF-01 y RF-07 dicen que el inmueble vuelve a **Disponible**. Queda abierta la pregunta de negocio: la oportunidad vuelve a Reservada mientras el inmueble está Disponible. Pregunta para el equipo y el tutor |
| 5 | El borrador decía que la reapertura "no notifica" a la Lista de Interesados | Borrador §12.2 | **Error del borrador.** RF-07 (reglas) dice que la reversión **y** la reapertura notifican; el proceso no lo contradice |
| 6 | Número de comparables (HU-04 3–5 vs RF-11 pocos o ninguno) | Tesis | Resuelto provisionalmente: **C-02 y DS-21** ([Deuda](URBANEX_DEUDA_TECNICA.md)) |
| 7 | Rol `cliente` en el sistema | Tesis vs código | **C-08**, confirmada por Pablo (DS-30) |
| 8 | Sin valores definidos: intentos de Messenger (RF-05), umbrales de inactividad (RF-16), duración de sesión (RF-13), lista de documentos críticos (RF-10) | Tesis | Abiertos (D-05 y preguntas a la empresa) |
| 9 | "Devolver al asesor" (RF-07) no dice a qué estado vuelve la oportunidad | Tesis | Abierto |
| 10 | El alcance de EP-5 menciona "reserva", pero HU-35 está en EP-6 | Tesis, tabla de épicas | Se sigue la tabla de HU: HU-35 en EP-6 |

---

## 7. Cómo mantener este documento

- **Al cerrar una HU:** no se toca este archivo (el estado está en los enlaces). Solo se actualiza si cambia el mapa, el corte del 60 % o un proceso.
- **Al implementar un paso:** completar la columna **Código** de §4 con los archivos y el endpoint (sin números de línea).
- **Si se decide algo del §6:** registrar la decisión en [Deuda técnica](URBANEX_DEUDA_TECNICA.md) (DS-xx) y enlazarla aquí.


### HU-10 — distribución de controles (2026-11-13)

Fase 0 aprobada por Sebas para tres archivos frontend y siete documentos. `CatalogFilters.tsx` distribuye botones de igual ancho: habitaciones/baños en cuatro columnas, parqueaderos en tres y tipos en dos con Todos en fila completa. El único botón de acción del panel es **Filtrar**; se elimina Cancelar visible y se conservan X, Escape y cierre exterior que descartan el borrador, con retorno del foco. **Limpiar filtros** es global junto a las etiquetas activas, que permiten eliminación individual; no se repite dentro de los paneles y conserva el orden.

El nuevo `CatalogResultsHeader.tsx` muestra conteo a la izquierda y **Ordenar por** a la derecha, fuera de la barra, con ajuste de filas en móvil. `app/properties/page.tsx` conecta conteo, filtros y errores; sin respuesta válida muestra Resultados sin inventar cero coincidencias. Opciones: Más recientes, Precio: menor a mayor y Precio: mayor a menor. No cambia la API. Sin modelos, migraciones, datos, dependencias, SiteNav o layout modificados en esta ampliación.

UX: [Baymard, filtros aplicados](https://baymard.com/research-articles/how-to-design-applied-filters) respalda visibilidad y eliminación de filtros; ubicar el borrado global junto a etiquetas es una aplicación al catálogo, no un requisito literal. [W3C APG, diálogo modal](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) contempla cierre visible, Escape y retorno del foco; la X permite quitar Cancelar. Referencias consultadas el 2026-11-13.

Edge automático: orden fuera de barra, sin Cancelar y con Filtrar; tipos con Todos de 366 px y otras opciones de 179 px. A 320 px, documento de 320 px, botones de habitaciones/baños de 57.5 px y parqueaderos de aproximadamente 79.33 px. Escape cierra y devuelve el foco a Filtros. Capturas locales `evidence/HU-10/distribucion-*-20261113.png`, ignoradas por Git. Los primeros envíos de Escape por CDP no cerraron; activar pestaña y enviar código virtual 27 permitió comprobar el cierre. No se atribuye ese fallo del arnés al producto.

HU-10 sigue **Pruebas**, V-46 humana **Pendiente**. Pasos humanos adicionales: revisar alineación y grupos en escritorio/móvil; Filtrar aplica; X/Escape/exterior descartan; foco retorna al disparador; cada etiqueta quita su filtro; Limpiar filtros elimina todos conservando orden; ordenar conserva filtros y reinicia página. Cotejo literal Anexo 2, Reservado humano y auditoría en chat nuevo pendientes. No se cambian porcentajes ni aprobaciones.


### HU-10 — DT-92 y preparación de integración (2026-11-13)

Sebas autorizó corregir DT-92, crear commits por grupos e incorporar develop; no autorizó push ni PR. `backend/apps/documents/models.py` cambia private_storage de instancia con ruta absoluta a función que resuelve BASE_DIR/private_media en el equipo actual; FileField conserva su contrato y serializa la función. `backend/apps/documents/migrations/0002_alter_document_file.py` usa SeparateDatabaseAndState con database_operations vacío: actualiza el estado de migraciones sin reconstruir tablas, mover archivos o reescribir rutas guardadas. No se modifica documents.0001 ni se aplica migrate a la SQLite de trabajo o Supabase. `backend/apps/documents/tests.py` agrega tres casos de serialización sin ruta de equipo, traslado de carpeta y lectura/escritura privada fuera de MEDIA_ROOT. Sin dependencias nuevas.

DT-92: corrección implementada; resultado técnico y criterio de cierre en Estándares §4. Historial previo de exit 1 se conserva. Seguridad: N/A, mantiene ubicación privada y permisos; no cambia exposición pública. V-46 mantiene las nueve aprobaciones humanas de Sebas, con el alcance y limitaciones escritos por él; Reservado humano permanece Pendiente y HU-10 en Pruebas. La decisión de Sebas de no usar Anexo 2 para esta entrega consta en V-46; no se reescriben reglas generales ni registros anteriores.

Archivos compartidos de HU-10: users/views.py, frontend/types/property.ts y frontend/lib/api.ts se preparan en commits propios. Incorporar origin/develop traerá también los cambios ajenos ya fusionados (incluido HU-09), sin atribuirlos a HU-10. Los conflictos se resolverán conservando ambas aportaciones; si requieren nuevos cambios funcionales fuera de alcance, se consultará. Auditoría de solo lectura en chat nuevo sigue Pendiente.

### Actualización aditiva PROC-01 / HU-09 — 2026-11-09

La fila histórica de PROC-01 paso 10 es anterior a esta implementación. HU-09 añade edición y acciones de retirada/reactivación en `users/serializers.py`, `users/views.py`, `users/urls.py`, `users/tests.py` y `frontend/app/dashboard/page.tsx`. Rutas: `POST auth/properties/<id>/withdraw/` (motivo obligatorio), `POST auth/properties/<id>/reactivate/` (solo a captación); para volver a Disponible se usa la publicación HU-53 existente. No cambia el corte del 60 % ni su reparto. Estado y validación se consultan en [HU-09](URBANEX_ESTADO_PROCESOS.md#hu-09); V-45 fue aprobada por Sebas el 2026-11-10 y está registrada en `Project_Progress.md`.


### HU-10 — integración de develop c420e56 (2026-11-13)

`git pull --no-rebase --no-commit origin develop` incorporó `c420e56` (PR #24, incluye HU-09 y lotes anteriores). Hubo conflictos solo en los siete documentos de seguimiento. Resolución aditiva: conserva todas las líneas de develop y todas las adiciones de HU-10 respecto de la base común; comprobación por conteos de líneas → ALL_HU10_ADDITIONS_AND_ALL_DEVELOP_LINES_PRESERVED. El primer control que comparaba también líneas históricas de HEAD señaló metadatos modificados legítimamente en develop; se ajustó el control a adiciones de HU-10 frente a base común y contenido completo de develop. No se descartaron aportaciones ajenas. AGENTS incorpora únicamente el cambio entrante de rango DS-50..69 de Pablo.

Las pruebas de retirada/privacidad de HU-09 necesitaban leer results del catálogo paginado. `users/tests.py` adapta cuatro lecturas, conservando las aserciones de ausencia del motivo público y visibilidad interna; /properties/mine/ mantiene array. Primer intento focal: 10 pruebas, 1 error por una lectura heredada adicional; corregida → 10 OK (2.539s), exit 0. No se cambia el serializer ni la implementación de HU-09. La primera suite integrada se interrumpió voluntariamente al detectar la incompatibilidad para corregirla; no cuenta como ejecución completa.

La SQLite de trabajo no se migró: showmigrations devuelve pendientes documents.0002, visits.0003 y opportunities.0002/0003. Las suites usan base de prueba independiente y aplican allí las migraciones. Antes de usar en navegador las funcionalidades entrantes, coordinar respaldo y aplicación local de las migraciones pendientes; no se atribuye la suite a esa SQLite. PostgreSQL No ejecutado (DT-68). Las aprobaciones humanas previas se conservan, Reservado humano y auditoría permanecen Pendiente. Sin push ni PR.


**Resultado final de integración HU-10 (2026-11-13):** suite integrada SQLite 372 OK (443.805s), exit 0; migraciones No changes detected, exit 0; frontend 41/41, TypeScript/ESLint/build exit 0, un aviso previo. DT-92 Resuelto por su criterio técnico; sqlmigrate de documents.0002 no-op. Se conserva develop c420e56 y el alcance de HU-10; controles documentales 7/7 y nueve aprobaciones humanas conservadas. Sin push, PR ni migrate en la base de trabajo. PostgreSQL No ejecutado (DT-68). Las notas previas de integración/suite en curso son historial y quedan sustituidas por este resultado. HU-10 en Pruebas; Reservado humano y auditoría Pendiente. Las migraciones locales pendientes indicadas arriba requieren respaldo y aplicación coordinada antes de usar los flujos entrantes en la SQLite de trabajo.


### HU-10 — correcciones documentales PR #27 (2026-11-13)

PROC-02 / HU-10 conserva implementación y endpoints anteriores. Esta corrección solo documenta la primera parte de HU-10 y no incorpora HU-35 ni cambia el corte del 60 %. Estado Pruebas, sin puntos completados nuevos. Contexto maestro/DS-16/ampliaciones aceptados por Pablo para este PR; cotejo Anexo 2 POR CONFIRMAR. DT-121..123 y comprobación humana de Reservado con HU-35 permanecen abiertos.
# Actualización aditiva HU-11 — 2026-11-16

Última actualización HU-11: 2026-11-16. PROC-02, paso 2: la ficha existente se amplía en `frontend/app/properties/[id]/page.tsx` y `frontend/components/PropertyGallery.tsx` (galería, datos, estado y precio referencial). Endpoint sin cambios: `GET /api/auth/properties/<id>/`. Regresiones en `backend/apps/users/tests.py`. Estado en [HU-11](URBANEX_ESTADO_PROCESOS.md#hu-11); evidencia pendiente en Project_Progress. Criterios literales Anexo 2 **POR CONFIRMAR**. No cambia el corte del 60 % ni otros procesos.
# Ampliación aditiva HU-11 · imágenes — 2026-11-16

Última actualización de esta ampliación: 2026-11-16. PROC-02 paso 2 conserva API y frontend; las URLs de fotos pueden ser locales o Cloudinary. `backend/config/settings.py` y `backend/config/media_storage.py` seleccionan proveedor para nuevas subidas existentes de `POST /api/auth/property-images/`. No se cambian las condiciones de publicación HU-53 ni los documentos privados. Estado en HU-11; DT-69 abierto y prueba real Pendiente. No cambia el corte ni la aceptación de otras HU.
# Fixes aditivos HU-11 · PROC-02 — 2026-11-16

Última actualización de estos fixes: 2026-11-16. Paso 2: foto del catálogo abre ficha, galería permite ampliar y ficha usa solo nav global. Gestión interna de fotos en Multimedia del dashboard → `DELETE /api/auth/property-images/<id>/`, owner/admin y protección última foto publicada en views/serializers. No cambia el corte ni los criterios originales; validación humana Pendiente y Anexo 2 POR CONFIRMAR.
**Actualización aditiva HU-11 / PROC-02 (2026-11-16, tarjeta completa):** el acceso del catálogo a la ficha usa toda la tarjeta como un único enlace en `frontend/components/PropertyCard.tsx`. Estado en HU-11, validación humana Pendiente; sin cambios de procesos o corte.
**Última actualización aditiva HU-11 / PROC-02 (2026-11-17):** desde catálogo, tarjeta completa abre ficha en otra pestaña. Paso 2 reorganiza resumen/galería y cambia ampliación a collage blanco con scroll, con badge y miniaturas mayores; código en PropertyCard, PropertyGallery y properties/[id]/page. Backend/endpoints, proceso, criterios y corte sin cambios. HU-11 en Pruebas; validación humana Pendiente.
**Última actualización aditiva HU-11 / PROC-02 (2026-11-17, proporciones/navegación):** ficha con galería izquierda y datos derecha; navegación de principal por miniaturas/flechas/gesto y apertura de collage sin leyendas ni recorte. Catálogo/nueva pestaña sin cambios. Código en página pública de detalle y PropertyGallery. Proceso/corte sin cambios; validación humana móvil Pendiente.
**Última actualización aditiva HU-11 / PROC-02 (2026-11-17, formato final):** PropertyGallery distingue formato uniforme de ficha y proporción natural de collage con separación pequeña. Backend, catálogo, proceso/corte sin cambios; validación humana Pendiente.
**Última actualización aditiva HU-11 / PROC-02 (2026-11-17, principal completa):** ficha muestra foto principal completa dentro del marco; galería/collage y proceso sin cambios. Código en PropertyGallery; validación humana Pendiente.
**Última actualización aditiva HU-11 / PROC-01/02 (2026-11-17, operación/terrenos/muestra):** alta incorpora operación explícita; catálogo filtra Venta/Alquiler mensual y muestra precios/contexto correctos, terreno sin habitaciones/baños. Comparables HU-04 separados por operación y snapshot del motor registra la nueva dimensión sin alterar históricos. users.0010 solo probada en copia; muestra separada de siete publicada mediante requisitos existentes de HU-53. Backend/endpoints conservan rutas. HU-11 en Pruebas, validación humana Pendiente; sin cambiar corte ni declarar completadas otras HU.
**Última actualización aditiva (2026-11-17, fixes de otras historias en rama HU-11):** por indicación de Sebas, distinguir HU-11/URB-14 (ficha) de fixes relacionados: PROC-01 HU-01/URB-05 alta/operación, HU-05/URB-08 terrenos, HU-09/URB-09 edición, HU-04/URB-10 comparables y HU-06/URB-11 motor; PROC-02 HU-10/URB-16 filtros/tarjetas y HU-12/URB-17 metadatos. Soporte DT-69/DT-14 no cuenta como HU completa. HU-53/URB-15 sin nuevo chequeo independiente de operación; contrato válido vía alta/constraint. Sin cambios de corte, puntos o validaciones humanas; detalle en Deuda/GPS.
**Última actualización aditiva (2026-11-17, entorno de prueba):** muestra de siete ahora activa en db.sqlite3 por autorización de Sebas, conservando cuentas y backup del conjunto de 28. Soporte DT-14 para revisar HU-11/fixes asociados; sin cambio de procesos/corte ni validaciones humanas nuevas.
**Última actualización aditiva (2026-11-17, barra/acciones/similares):** PROC-02/HU-11/URB-14 incorpora barra y filas de similares/principales. PROC-03 reubica acceso a WhatsApp HU-15/URB-21 y consulta HU-16/URB-20; PROC-04 reubica horarios HU-18/URB-18 y solicitud HU-19/URB-23 bajo demanda, con borrador personal reutilizado y consentimientos separados. Fixes UX sin modificar APIs/procesos/corte. Validación humana Pendiente; no se declara otra HU completa.


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


### HU-11: posicion del zoom - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Solicitud de Sebas dentro del alcance del mapa: PropertyLocationMap.tsx desactiva zoomControl por defecto y agrega ZoomControl bottomright, titulos Acercar/Alejar. Sin cambio de proveedor, mosaicos, marcador, telemetria, dependencias ni backend. Iconos de lugares estan integrados en mosaicos raster OSM y no se ocultaron; estilo base mas limpio requiere evaluar proveedor/estilo, pendiente de decision. Revision visual desktop/movil y convivencia con atribucion Pendiente; HU-11 sigue en Pruebas. Frontend 48/48, tipos/lint/build exit 0, aviso previo SiteNav; sin commit/push/PR ni nuevas capturas.


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


### Fixes visuales: plantilla comun de paginas - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Alcance visual confirmado por Sebas: nuevo `frontend/components/PageLayout.tsx` (PageLayout y PageHeader) y `docs/handoff/PLANTILLA_VISTA.md`; adopcion en `frontend/app/properties/page.tsx`, `frontend/app/dashboard/page.tsx`, `frontend/app/dashboard/opportunities/page.tsx`, `frontend/app/dashboard/availability/page.tsx`, `frontend/app/dashboard/agenda/page.tsx`. Archivo dashboard compartido avisado antes. Separacion principal py-6=24px con configuracion actual, gutters px-4/sm:px-6/lg:px-8, ancho conservado catalogo1600/standard6xl/narrow5xl. Antetitulo/titulo/descripcion y acciones responsivas uniformes. PageHeader mb-6; carga de panel/disponibilidad/agenda tambien usa contenedor comun. SiteNav raiz intacto, sin duplicarlo.

Se retira Volver al panel de listas principales oportunidades/disponibilidad/agenda, conservando navegacion superior. Sin retirar regresos contextuales de detalles/formularios fuera de alcance. Sin cambios de autenticacion, pesta?as, backend, DB, migraciones, reglas de negocio, dependencias ni proveedor de mapas. Sesion entre pesta?as nuevas de produccion sigue pendiente, misma pesta?a en desarrollo ya implementada antes. No se agrega template a login, ficha o estadisticas porque no forman parte de esta adopcion.

Trazabilidad: ajuste catalogo fix HU-10/URB-16; panel plantilla compartida transversal; oportunidades fix HU-34/URB-34; disponibilidad fix HU-22/URB-19; agenda fix HU-24/URB-27. No son nuevos criterios HU-11 ni se cambian estados de otras HU. Sin IDs nuevos. Guia documenta ejemplo de nueva vista, anchos, espaciado, acciones, carga, limites y que autorizacion sigue en API. Seguridad sin cambio de riesgos.

Comprobaciones: linea base y final frontend48/48, tsc/ESLint/build exit0 (aviso previo SiteNav), build16/16. No se crean pruebas que solo repliquen clases visuales. Sin backend nuevo: referencia anterior sqlite406 OK/check sin cambios, no repetidos. PostgreSQL No ejecutado DT-68. Validacion humana Pendiente: comparar los cinco antetitulos a24px bajo la misma navegacion en escritorio/movil, acciones sin overflow, pantallas de carga, ausencia de enlaces redundantes y funcionalidad de filtros/formularios/agenda. No hay captura nueva ni V aprobada. HU-11 sigue en Pruebas sin puntos adicionales; sin commit/push/PR. Siguiente paso: Sebas revisa las cinco vistas y la guia.


### Correccion de ancho agenda/disponibilidad - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Sebas reporta diferencia de ancho tras plantilla. Causa confirmada: availability y agenda usaban width narrow=max-w-5xl, a diferencia de panel/oportunidades standard=max-w-6xl. Se corrigen ambos estados carga/contenido a standard en las dos paginas; PLANTILLA_VISTA.md actualiza standard para cuatro vistas internas y reserva narrow para futuros casos justificados. Correccion sustituye indicacion anterior de conservar5xl en esas dos vistas; historial previo conservado. Fix HU-22/URB-19 y HU-24/URB-27, sin logica/auth/backend/BD/dependencias nuevos. Frontend48/48, tsc/lint/build exit0, aviso previo SiteNav. Validacion visual humana Pendiente; HU-11 sigue en Pruebas. Sin commit/push/PR ni capturas nuevas; siguiente paso comparar anchos en escritorio y movil.


### Respaldo de trabajo para retomar - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama `feat/URB-14-HU-11-ficha-detalle`. Sebas autoriza expresamente commits y push para conservar avance en GitHub y retomar en dos dias (2026-11-20); NO solicita abrir PR ni integrar develop. Ajuste final pedido: ficha reduce direccion de text-lg/mt-2 a text-base/mt-1, espacio hasta precio y cuadro de mt-6 a mt-4, titulo Caracteristicas principales centrado. Implementado en `frontend/app/properties/[id]/page.tsx`; revision visual humana Pendiente.

Estado de continuidad: 16 commits de codigo por capa guardados desde b75e227 hasta 3d5552a; contratos serializer+Property juntos conforme GPS y archivos compartidos con commits dedicados. Documentacion se guarda despues de registrar resultados. git fetch origin ejecutado; origin/develop sigue 6e0caca, misma base (comparacion previa HEAD...origin/develop 0/0), sin cambios que integrar. No se abre PR ni se declara Apto para PR; auditoria obligatoria en chat nuevo sigue pendiente antes del futuro PR. Esta subida es respaldo de trabajo, HU-11 sigue en Pruebas y validaciones humanas Pendiente.

Comprobacion final nueva: con PIPENV_DONT_LOAD_ENV=1, DB_ENGINE=sqlite, EMAIL_PROVIDER=console, MEDIA_PROVIDER=local, suite completa incluyendo telemetry 406 OK en 164.451s, SUITE_EXIT=0; makemigrations --check --dry-run No changes detected, MIGRATIONS_EXIT=0. Frontend48/48, tsc/ESLint/build exit0 y aviso previo SiteNav; build16/16. Sin PostgreSQL (No ejecutado DT-68, Nivel1), sin capturas nuevas. No se versionan archivos .env, DB, media/private_media o evidence; fotos antiguas ya rastreadas en develop no cambiaron y no se incluyeron en estos commits.

Al retomar: abrir esta rama y leer esta nota primero; comprobar git status y referencias remotas. Base local habitual backend/db.sqlite3 conserva siete propiedades y tres usuarios; no se sube, ni se suben sus fotos/documentos locales. Otras maquinas deben configurar su propio entorno, aplicar migraciones solo contra BD local comprobada y recrear datos demo si corresponde. Migraciones nuevas: users.0010 y telemetry.0001; no editar aplicadas ni migrar Supabase desde rama. CARTO retirado, clave local sin uso; mapa Leaflet/OSM. Desarrollo navega fichas en misma pestana y produccion en nueva.

Pendientes para continuar: recuperacion de sesion al iniciar nueva pestana en produccion (sin bypass ni localStorage), validacion humana movil/desktop y envios de formularios, criterios Anexo2 POR CONFIRMAR, auditoria de solo lectura antes de PR y documentar cualquier hallazgo. No mapa de catalogo ni medicion de facturacion oficial implementados. Plantilla visual PageLayout y guia PLANTILLA_VISTA disponibles; panel/oportunidades/disponibilidad/agenda usan standard y24px arriba. Estadisticas en Panel > Estadisticas, solo admin. Explicacion de backend/frontend y fixes por HU permanece en notas anteriores/GPS. Push se confirma por hash remoto al terminar, no se presume exito en esta nota.


### HU-11: distinguir tarjetas de caracteristicas - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Tras respaldo remoto cebd44f, Sebas solicita distinguir cuadritos de area/banos/etc. Ficha [id]/page.tsx: fondo general slate-100 en vez de slate-50; tarjetas blancas con borde slate-200/70 y shadow-sm, titulo centrado conservado. Solo presentacion, sin reglas/backend/BD/dependencias nuevos. Frontend48/48, tsc/lint/build exit0, aviso previo SiteNav. Revision visual humana Pendiente; HU-11 en Pruebas. Cambio local sin commit ni push nuevos; no se presume que el respaldo remoto ya lo incluye. Sin capturas nuevas. Siguiente paso: Sebas revisa contraste y autoriza guardar este ajuste si corresponde.


### Buscador inicial y catalogo por operacion - 2026-11-18

Ultima actualizacion: 2026-11-18. Entrada publica a HU-10/URB-16: HomePage -> HomeSearch (GET /properties con operation_type, property_type/location opcionales) -> withCatalogOperation (venta si falta operacion) -> API catalogo existente -> filtros confirmables y tarjetas. No nuevas historias, estados ni puntos; extension UX aprobada por Sebas. PropertyCard compacta compartida por similares HU-11. Validacion humana Pendiente, referencias tecnicas en GPS y Estandares. Sin cambios de API/modelos.


### Ajuste HU-10: nombres fijos y operacion eliminable - 2026-11-18

Ultima actualizacion: 2026-11-18. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Sebas solicita retirar CTA Acceso Portal Asesores de portada, mantener nombre de filtros aunque se seleccione opcion, evitar repeticion Venta o alquiler y permitir limpiar operacion. Tras preguntar sobre limpieza, Sebas aclara que quiere nombre fijo y sin opcion por defecto; se comunica interpretacion aplicada: catalogo directo sin operacion muestra ventas y alquileres, eleccion desde portada se conserva. Esto sustituye el anterior default venta/no mezclar en UI; API no cambia. Boton fijo propuesto Comprar o alquilar y Tipo de inmueble; azul solo con filtro aplicado, opciones elegidas en chips eliminables. Limpiar filtros elimina operacion y conserva orden; quitar chip de operacion limpia tambien precios para no arrastrar rangos de otra modalidad. Repetir opcion de operacion permite desmarcarla. Panel desktop tiene un solo titulo; movil tiene leyenda dentro de filtros. HomeSearch conserva sus radios de entrada Venta/Alquiler y no pierde la eleccion al buscar. CTA asesores eliminado solo de portada, navegacion raiz intacta.

Archivos: app/page.tsx, app/properties/page.tsx, components/CatalogFilters.tsx, lib/catalogFilters.ts y test. No nuevo backend, modelo, dependencia, datos ni claves. Pruebas51/51, tsc/lint/build exit0. Prueba Edge aislada por stdin: desktop1440x1000, portada sin CTA duplicado, catalogo7 sin operacion, venta4 y chip elimina operacion/precio a7, alquiler3 y tipoCasa1 con nombres invariables, titulo panel una vez, limpiar restaura7. Movil375x812 elimina chip Alquiler a7 y sin overflow. No formularios contacto/visita ni archivos evidence, navegador cerrado. Validacion humana Pendiente sobre etiqueta Comprar o alquilar y revision visual; observacion automatizada no aprueba V. Fix/ampliacion HU-10/URB-16, HU-11 permanece en Pruebas sin puntos. Sin commit/push/PR. Cambios previos de ficha y tarjetas conservados. Siguiente paso: Sebas revisa nombres y confirma UX.


### Busqueda opcional y filtros compatibles - 2026-11-19

Ultima actualizacion: 2026-11-19. HU-10/URB-16, flujo publico: HomeSearch Comprar/Alquilar opcional -> /properties -> normalizacion de terreno y filtros -> API existente -> resultados. Limpieza por panel solo borrador hasta Filtrar; seleccion Terreno excluye habitaciones/banos con aviso y controles deshabilitados. API, modelos y estados de HU no cambian. Sin nuevos puntos/IDs; evidencia automatica en Estandares, validacion humana Pendiente.


### Fix HU-10: resaltado de grupos aplicados - 2026-11-19

Ultima actualizacion: 2026-11-19. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Reporte de Sebas confirmado: CatalogFilters solo resaltaba tipo/operacion. Ahora usa panelKeys para precio, habitaciones/banos, tipo y mas filtros; grupo azul si tiene algun campo aplicado, no por borrador sin confirmar. Boton movil Filtros tambien azul cuando hay filtros activos. Precio0 cuenta como filtro; desmarcar precio deja otros grupos azules. Solo CatalogFilters.tsx y docs, sin backend/BD/dependencias nuevos. npm test54/54, tsc/lint/build exit0; lectura HTTP+HTMLParser de3URLs verifica estados precio/rooms/more [false,false,false], [true,true,true], [false,true,true]. Validacion visual humana Pendiente. HU-11 en Pruebas, sin nuevos commits/push ni evidence. Siguiente paso: Sebas revisa resaltado al aplicar/quitar filtros.


### Contacto: WhatsApp y correo opcional sin novedades - 2026-11-19

Ultima actualizacion: 2026-11-19. Codex con Sebas, rama feat/URB-14-HU-11-ficha-detalle. Sebas reporta WhatsApp ausente, pide ayuda celular solo ante error y retirar casilla de novedades; posteriormente pregunta finalidad del correo segun contexto maestro. RF-03 lineas72-73 contempla correo opcional y opt-in novedades, no obliga correo para interes. HU-20/URB-24 confirma visitas en flujo distinto. Lectura de servicios confirma register_web_interest no envia email; correo se muestra al asesor en oportunidades/[id]/page.tsx:239. Se propone mantener correo opcional como canal para consulta, no se implementa confirmacion automatica ni campana, pendiente decision de alcance futura. Retirar casilla es solicitud explicita de Sebas; no se reescribe RF-03 ni DS-50 historicos.

Diagnostico WhatsApp comprobado sin mostrar numeros: GET de las7propiedades200 y whatsapp_phone ausente; SQLite modo solo lectura confirma asesores activos sin celular registrado en las7asignaciones. No es problema del enlace: falta dato de asesor. No se inventa numero ni se modifica usuario; configurar desde Administrar usuarios > editar asesor > Telefono. WhatsAppContactButton.tsx mantiene reglas de backend, muestra estado de carga/no disponible/error en lugar de desaparecer sin explicacion, Reintentar ante fallo; numero valido produce wa.me existente. Ningun numero real leido en salida ni clave expuesta.

InterestForm.tsx y VisitRequestForm.tsx retiran ayuda permanente de celular, agregan validacion contactPhoneError al salir del campo/enviar y mensaje accesible solo ante error. Helper acepta formatos DS-28 (local09 o +5939, separadores permitidos). InterestForm retira casilla novedades/validacion asociada y envia email_opt_in=false; correo sigue opcional, LOPDP obligatorio. No implica alta publicitaria ni modifica consentimientos previos de contactos existentes: DS-28 conserva datos de contacto reutilizado. Sin backend, migraciones o dependencias nuevas. Fix HU-15/URB-21, HU-16/URB-20 y presentacion celular HU-19/URB-23.

Pruebas:55/55 frontend, tipos/lint/build exit0, build16/16. Helper nuevo cubre formatos validos, faltante, corto/largo y extranjero. Navegador real datos demo: aviso no disponible, una sola casilla LOPDP, ayuda no aparece inicialmente, teclado real invalido+blur muestra error y corregir lo retira. Primera prueba con eventos sinteticos fallo; repetida con Input de CDP verifico validacion. Pruebas mock iniciales de reintento fallaron por asumir una sola consulta al montar: StrictMode hace dos y el mock daba exito en la segunda. Mock corregido para mantener fallo hasta Reintentar -> WHATSAPP_RETRY_OK,3GET simulados, enlace visible con numero sintetico, nunca abierto. No contactos/visitas enviados, correos, cambios en usuarios ni archivos evidence; navegadores cerrados. Revision visual/telefono humano Pendiente, HU-11 en Pruebas, sin aprobacion V, commit/push/PR. Siguiente paso: Sebas registra celular de trabajo en asesor y decide si quiere confirmacion transaccional como funcion nueva. Suite backend no repetida; PostgreSQL No ejecutado DT-68.
