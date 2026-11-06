# Urbanex — Checklist TO-BE: ¿el sistema sigue el proceso de la empresa?

| Campo | Valor |
|---|---|
| Propósito | Comparar, paso a paso, los procesos TO-BE de la empresa con lo que el sistema ya hace. Responde a la observación del tutor (4-nov): "solo veo un CRUD; no veo que siga el proceso" |
| Fecha | 2026-11-04 |
| Fuente de los procesos | `URBANEX_PROCESOS_EMPRESA.md` (extra?do de DatosCaptsone, 2026-10-24) |
| Fuente del estado del código | `URBANEX_USM_TRAZABILIDAD.md` §4 (3-nov, contra `develop`) + PR #14 (HU-12) y PR #15 (HU-27/34) fusionados el 4-nov |
| Para la próxima reunión | Miércoles 11-nov: mostrar cada paso junto a la pantalla o la regla que lo cumple |

**Leyenda:** ✅ lo hace el sistema · 🟡 parcial · ⬜ no implementado · 🔨 en curso (lote 2) · 🧍 actividad fuera del sistema (la hace una persona, no hay nada que programar)

---

## 0. Los 8 procesos oficiales y su relación con los PROC del repositorio

Los códigos PROC-01..08 del repo los inventó el equipo (USM §3: "la tesis no los numera"). Pero `DatosCaptsone` **sí** los numera y los nombra distinto. **Desde ahora se usa la numeración de `DatosCaptsone` (T1..T8)** y los PROC quedan como referencia interna.

| T | Proceso oficial (DatosCaptsone) | Tipo | PROC del repo que lo cubren | En el compromiso del 14-nov |
|---|---|---|---|---|
| T1 | Captación de propiedades | Core | PROC-01 | Sí |
| T2 | Marketing y generación de oportunidades | Core | PROC-02, parte de PROC-03 | Sí |
| T3 | Seguimiento y trazabilidad de contactos y oportunidades | Core | PROC-03, PROC-04, PROC-05 | Sí |
| T4 | Venta de propiedades | Core | PROC-05 (negociación), PROC-06, PROC-07 | No |
| T5 | Arriendo de propiedades | Core | PROC-05 (negociación), PROC-06, PROC-07 | No |
| T6 | Avalúo comercial | Core | PROC-01 (pasos de avalúo) | Sí |
| T7 | Gestión documental | Soporte | PROC-01 (documentos iniciales), PROC-06 | **Solo si se agrega HU-37** (ver §6) |
| T8 | Gestión administrativa de cartera | Soporte | PROC-08 | No |

> EP-1 (usuarios, sesión, desbloqueo) no es un proceso de la empresa: es la base técnica de todos.

---

## 1. T1 · Captación de propiedades (2.1)

| # | Paso TO-BE | HU | Estado | Dónde se ve / qué falta |
|---|---|---|---|---|
| 1 | El propietario entrega la información y el asesor verifica que la documentación esté al día | — | 🧍 | Fuera del sistema |
| 2 | El asesor registra la propiedad; queda **En captación**, sin exhibirse, y él como captador y responsable | HU-01, HU-02 | 🟡 | I-10. **Regla de proceso:** toda propiedad nueva nace En captación (✅). Falta: un `cliente` autenticado aún la ve (DT-39); captador y responsable son un solo campo (DT-17) |
| 3 | Carga la documentación inicial en el expediente | HU-03 | ✅ | Pestaña Expediente, con versiones y vigencia (V-03) |
| 4 | Realiza el avalúo con el motor paramétrico | HU-04, 06, 08 | ✅ | I-11 / I-12 (ver T6) |
| 5 | Presenta el avalúo al propietario y negocian; si no hay acuerdo, termina | — | 🧍 | Fuera del sistema. ⚠️ El sistema no registra "captación rechazada": la propiedad se queda En captación |
| 6 | Se formaliza y carga el **contrato de corretaje** | HU-03 | ✅ | Documento tipo corretaje en el expediente |
| 7 | Con avalúo y corretaje, el asesor publica → **Disponible** y aparece en el catálogo | HU-53 | ✅ | **Regla de proceso:** el sistema **impide** publicar sin avalúo aprobado y corretaje (V-02, V-11, V-12). Mostrar esto el miércoles |

**Lectura:** T1 ya sigue el proceso. Los pasos 3, 6 y 7 son reglas que el sistema hace cumplir, no un CRUD.

---

## 2. T6 · Avalúo comercial (2.6)

| # | Paso TO-BE | HU | Estado | Dónde se ve / qué falta |
|---|---|---|---|---|
| 1 | Registrar las características físicas y técnicas | HU-05 | 🟡 | Campos básicos y mapa. Faltan campos de RF-01 (DT-19). El motor **bloquea** el cálculo sin superficie ni coordenadas |
| 2 | Consultar indicadores estadísticos del sector (tareas programadas) | — | ⬜ | **Sin HU en el backlog.** Decidir: ¿se agrega o se declara fuera de alcance? |
| 3 | Seleccionar entre 3 y 5 comparables | HU-04 | ✅ | I-11; el servidor rechaza más de 5 y menos de 3 pasa a manual (C-02) |
| 4 | El motor aplica factores ponderados y calcula el valor sugerido | HU-06 | ✅ | I-12 (V-21, V-22) |
| 5 | Borrador de justificación con IA (opcional en el TO-BE) | HU-07 | ⬜ | Fuera del compromiso; el TO-BE lo marca como opcional |
| 6 | El asesor revisa, calibra y aprueba (Human-in-the-Loop) | HU-08 | ✅ | I-12 (V-05..V-09) |
| 7 | Guardar de forma inmutable el cálculo, el valor aprobado y la diferencia | HU-06, HU-08 | ✅ | Aprobado = solo lectura; reevaluar crea otro folio (V-09) |

**Lectura:** T6 es el proceso más completo. Solo falta el paso 2, que no tiene HU.

---

## 3. T2 · Marketing y generación de oportunidades (2.2)

| # | Paso TO-BE | HU | Estado | Dónde se ve / qué falta |
|---|---|---|---|---|
| 1 | Ficha digital centralizada con multimedia y descripción estructurada | HU-01, HU-11 | ✅ | P-03 |
| 2 | Al pasar a Disponible, aparece **automáticamente** en el catálogo | HU-53, HU-10 | 🟡 | Automático ✅ (solo Disponible/Reservado son públicos). Faltan los filtros de HU-10 |
| 3 | Publicar en Marketplace con un **enlace directo a la ficha** | HU-12 | ✅ | URL con metaetiquetas (PR #14). La publicación en Facebook es 🧍 |
| 4 | Promoción pagada hacia el portal | — | 🧍 | Fuera del sistema |
| 5 | Contenido en redes hacia el portal | — | 🧍 | Fuera del sistema |
| 6 | Recibir manifestaciones de interés (formulario o mensajería) | HU-16, HU-17 | ⬜ | HU-16 en el compromiso; HU-17 (Messenger) fuera |

---

## 4. T3 · Seguimiento y trazabilidad de contactos y oportunidades (2.3)

| # | Paso TO-BE | HU | Estado | Dónde se ve / qué falta |
|---|---|---|---|---|
| 1 | **Captación manual:** el asesor registra un contacto y se abre la oportunidad | HU-27 | ✅ | I-07 (PR #15, V-26..V-32) |
| 2 | **Captación digital:** interés desde el portal o webhook de redes | HU-15, 16, 17 | ⬜ | HU-15 y 16 en el compromiso; HU-17 fuera |
| 3 | Messenger: Conversación Inicial y respuesta automática pidiendo el número | HU-17, HU-26 | ⬜ | Fuera del compromiso |
| 4 | Si la propiedad está **Reservada**, se ocultan los botones y aparece "Registrar interés" | HU-13 | ⬜ | Meta extendida |
| 5 | Ese formulario crea contacto y oportunidad en **Lista de Interesados** | HU-13 | ⬜ | Meta extendida |
| 6 | Fuera de WhatsApp, se exige un **teléfono válido** | HU-15, HU-16 | ⬜ | Compromiso |
| 7 | Se crea contacto + oportunidad asignada y **se notifica** al asesor | HU-15, 16 (+ HU-32) | ⬜ | Compromiso (la notificación de HU-32 está fuera) |
| 8 | WhatsApp Business envía un mensaje de bienvenida con el enlace a la ficha | HU-15 | ⬜ | ⚠️ Revisar alcance: ¿API de WhatsApp Business o solo redirección? |
| 9 | Agendamiento → la oportunidad pasa a **Visita Programada** | HU-22, 18, 19, 20 | 🔨 | Lote 2 (HU-22, 18, 24); HU-19 hace el cambio de estado |
| 10 | El asesor atiende y negocia (botón de WhatsApp desde el portal interno) | HU-30 | ⬜ | Compromiso |
| 11 | Visita presencial | — | 🧍 | Fuera del sistema |
| 12 | Registrar el resultado de la visita (realizada, no asistida, cancelada) | HU-25 | ⬜ | Compromiso |
| 13 | Sin interés → registrar el motivo de cierre · Con interés → avanzar a venta o arriendo | HU-31, HU-29 | ⬜ | HU-29 en el compromiso. ⚠️ **HU-31 (Perdida con motivo, 2 pts) está fuera** y es la salida "sin interés" del proceso |
| — | Ver la cartera de oportunidades con filtros | HU-34 | ✅ | I-06 (PR #15) |

**Lectura:** T3 es donde está casi todo el trabajo pendiente. Es el proceso que más "flujo" muestra (estados que cambian solos), así que es el que más convence al tutor cuando funcione.

---

## 5. T7 · Gestión documental (2.7)

| # | Paso TO-BE | HU | Estado | Dónde se ve / qué falta |
|---|---|---|---|---|
| 1 | El asesor carga los archivos en el expediente | HU-03, HU-36 | 🟡 | Propiedad ✅ con versiones; oportunidad ⬜ (HU-36) |
| 2 | **El administrador verifica autenticidad y vigencia y marca Aprobado/Rechazado** | HU-37 | 🟡 | Solo el modelo (`Document.validate_document`); falta endpoint y pantalla. **Esta es la respuesta a la pregunta del tutor sobre el PDF "real"** |
| 3 | Almacenar en la nube y clasificar automáticamente en el expediente | HU-03 | 🟡 | Clasificación por tipo y asociación ✅; almacenamiento en la nube POR CONFIRMAR |
| 4 | Consulta y descarga con **URL firmada** según rol | HU-38 | 🟡 | Descarga protegida provisional; sin URL firmada |
| 5 | Detectar documentos faltantes o vencidos, alertar y **bloquear el avance** | HU-39 (+ HU-53) | 🟡 | Bloqueo de publicación sin corretaje ✅ (HU-53); aviso "vence pronto" en el modelo; faltan alertas y bloqueo en la oportunidad |

---

## 6. Qué cambiaría en el compromiso

Medido contra los **8 procesos oficiales**, el compromiso actual cubre **T1, T2, T3 y T6** (4 de 8) y deja T7 a medias. Para mantener **5 de 8 (62,5 %)** con la numeración oficial:

| Agregar | Pts | Prioridad | Por qué |
|---|---|---|---|
| **HU-37** Aprobar/Rechazar documento | 3 | Alta | Completa el paso clave de T7 y responde la observación del tutor |
| HU-39 Alertas de faltantes/vencidos | 3 | Media | Completa el paso 5 de T7 (opcional si no alcanza el tiempo) |
| HU-31 Marcar Perdida con motivo | 2 | Media | Cierra la salida "sin interés" de T3 |

Con HU-37: compromiso = 90 pts (54 %) y 5 de 8 procesos oficiales. Con las tres: 95 pts.

**Pendiente de decidir:** el paso 2 de T6 (indicadores del sector) no tiene HU.

---

## 7. Para la reunión del miércoles 11-nov

Mostrar tres reglas que el sistema ya hace cumplir (no son CRUD):
1. **T1-7:** no se puede publicar sin avalúo aprobado y contrato de corretaje.
2. **T6-3/6:** el motor rechaza comparables inválidos y el avalúo aprobado no se puede modificar.
3. **T3-1 / T1-2:** toda propiedad nace En captación; toda oportunidad nueva nace en Contacto Inicial y queda asignada.

Y una cuarta, si se alcanza: **T3-9**, solicitar una visita cambia sola la oportunidad a Visita Programada (HU-19).

## 8. Mantenimiento

Al cerrar una HU, cambiar su ícono aquí. Este archivo se puede copiar a `docs/handoff/` y enlazar desde el USM §3; la numeración T1..T8 debería registrarse como decisión (DS).
