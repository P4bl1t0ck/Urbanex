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
   `origin/develop`: **90/90 OK** (FX-18, 2026-10-30). Tras integrar HU-44 y la validación del teléfono: **116/116 OK** con SQLite y correo de consola; ver "Estado actual". Si la sesión toca el frontend, también `npx tsc --noEmit -p .` (desde `frontend/`).

### Reglas
- **No inventar decisiones pendientes** (D-04 fórmula del motor, C-02, N-02, N-03, etc.). Si una HU depende de una, se usa un placeholder documentado y se pregunta.
- **Si el código y el handoff se contradicen, se detiene el trabajo** y se pregunta al responsable; se corrige el que esté mal y se registra.
- **Archivos compartidos** (`backend/apps/users/models.py`, `users/migrations/`, `backend/config/settings.py`, `frontend/types/property.ts`, `frontend/app/dashboard/page.tsx`): avisar antes de tocarlos (GPS §3).
- **Las transiciones de estado no son un PATCH genérico**: cada una es una acción explícita con sus precondiciones verificadas en el servidor (contexto maestro §11).
- **Un cambio no está terminado** hasta que, en el mismo PR/commit, se actualicen Estado de procesos, Deuda técnica, GPS, Avance de épicas y este archivo, con evidencia (comando + resultado).
- Estándares de código y checklist DoD: [`URBANEX_ESTANDARES_DOD.md`](docs/handoff/URBANEX_ESTANDARES_DOD.md). Requisitos: [`URBANEX_MASTER_CONTEXT.md`](docs/handoff/URBANEX_MASTER_CONTEXT.md) (la copia de `docs/handoff/` es la de referencia).

---

## 🧭 Pendiente ahora (2026-10-30)

> - ~~**🧪 Ronda 3 (motor DS-21):** validaciones V-20 a V-25~~ **Hechas el 2026-10-29 y el 2026-10-30: las 6 aprobadas**. V-25 pasó tras la corrección FX-18. **Siguiente:** la PR de `feat/URB-10-11-motor-avaluos` a `develop`.
> - **HU-44 (Fase B):** rama reconstruida sobre `origin/develop`; 116/116 pruebas backend aprobadas en SQLite. Sebas confirmó V-26 a V-32, incluido el 403 de la API, la invalidación del enlace anterior al reenviar y los ajustes de usabilidad del teléfono. Commits publicados; PR pendiente de autenticación en GitKraken.
> - **POR CONFIRMAR (Pablo / tutor):** si HU-04, HU-06 y HU-08 cuentan como completas (C-02 y θ v1 siguen provisionales). Pregunta para la empresa: N-05 (¿el avalúo aprobado actualiza el precio?), ampliada el 2026-10-30.
> - **DT-65:** falta la copia de Sebas.
> - Los pendientes del 2026-10-28 ya resueltos están archivados en [Historial](#historial).

---

## D-04 — FÓRMULA DEL MOTOR DE AVALÚOS: PLAN B ACTIVADO (2026-10-28)

> **Registro del 2026-10-28.** El plazo (08:00) **venció sin respuesta** del compañero responsable. **Pablo activó el plan B** y decidió la arquitectura: y = f(x; θ) en tres capas.
> - **Estructura:** método comparativo de mercado, de 3 a 5 comparables del mismo tipo y zona, combinados con pesos y con una confianza que depende de la cantidad y la dispersión de los comparables. Es determinista.
> - **Factores:** piezas intercambiables, registradas por nombre y cada una con su referencia.
> - **Parámetros θ:** versionados y editables por un admin; cada avalúo guarda la versión que usó. Quedan EN OBSERVACIÓN.
>
> La propuesta, con las fuentes (COOTAD arts. 495–496, Superintendencia de Bancos SB-2020-0573, Código Municipal del DMQ Libro III.5, Ordenanza Metropolitana 108-2025 y la Norma Técnica de Valoración DMQ 2025), está en [`URBANEX_DS-21_MOTOR_AVALUOS.md`](docs/handoff/URBANEX_DS-21_MOTOR_AVALUOS.md).
>
> **✅ Aprobada por Pablo el 2026-10-28, con carácter provisional. D-04 queda resuelta provisionalmente con DS-21.**
> - C-02: manual con 1–2 comparables, hasta que lo confirme el tutor.
> - `zone`: lista controlada como destino y radio entre coordenadas como provisional.
> - Comparables: `disponible`, `reservador` y `vendido`.
> - θ v1: EN OBSERVACIÓN.
> - F4 y F5: las confirma Pablo.
>
> Ajustes de Pablo: factores por tipo de propiedad, comparables sintéticos antes de I-11 y valor mostrado redondeado a cientos. DS-02 (registro manual) sigue vigente cuando no hay comparables suficientes.
>
> El texto de abajo es la directiva original, que se conserva como historial.

### Directiva original (2026-10-27)

> **¡ATENCIÓN! EL MOTOR DE CÁLCULO ES PARTE VITAL DEL CORE DE URBANEX (RF-11, HU-04, HU-06, HU-08).**
>
> - **Situación (2026-10-27):** Pablo pidió la fórmula al compañero responsable el **jueves 2026-10-22** y **aún no hay respuesta**.
> - **PLAZO: MIÉRCOLES 2026-10-28, 08:00 (hora de Ecuador).**
> - **Si llega la respuesta:** se registra como decisión de D-04 (fórmula, factores ponderados, umbrales de confianza) en Deuda técnica §4 y en el contexto maestro, y se implementa tal cual.
> - **SI NO LLEGA:** Pablo pedirá a la IA **diseñar el motor de cálculo a partir de las fórmulas de valoración del municipio (Quito) y de la normativa de Ecuador**. Aun así, **no se programa nada sin antes documentar las fuentes** (ordenanza o norma, artículo y fecha) y sin que Pablo apruebe la fórmula propuesta como decisión DS-xx.
> - **HASTA ENTONCES:** HU-08 se queda como **POR CONFIRMAR** respecto a si cuenta como completa (sus 2 criterios están validados con el registro manual, DS-02). **¡No inventar la fórmula ni valores sugeridos!**

---

## 🧪 Validaciones pendientes de Pablo

> **Resultado de la ronda del 2026-10-27:** Pablo, con `asesor.demo@urbanex.test` y los datos de `setup_demo_data` (propiedades #32 Cumbayá, #33 La Carolina, #35 Tumbaco). **Las 12 pruebas quedaron aprobadas** (V-03 en el segundo intento). **DT-40 se cerró** con V-11 y V-12. Los 8 hallazgos de la ronda están registrados en [Deuda técnica](docs/handoff/URBANEX_DEUDA_TECNICA.md): DT-25 (actualizado), DT-55 a DT-60 y la pregunta de negocio N-05.
>
> **Por qué existe esta sección:** el DoD del equipo exige que cada flujo se compruebe **en la interfaz** ("no basta con Postman"). Estas pruebas se acumularon desde el 2026-10-22 sin hacerse. Mientras sigan en **Pendiente**, DT-40 no se cierra y HU-01, HU-03, HU-05, HU-08 y HU-53 no pueden marcarse como validadas en la parte funcional ni en la visual.
>
> **Cómo usarla:** sigue los pasos de cada prueba y responde la pregunta del resultado esperado. Después llena la fila: **quién** la hizo, **cuándo** (fecha y hora), **qué viste** (textos, estados, capturas si las hay) y el resultado (**Aprobado** / **Fallido**). Si algo falla, anota exactamente qué apareció; con eso se abre o actualiza el DT correspondiente. Ninguna fila se marca como Aprobada por inferencia.
>
> **HU-44:** implementación, pruebas automatizadas y validación manual aprobadas. Sebas confirmó V-26 a V-32, incluido el rechazo del enlace anterior al reenviar, el HTTP 403 para asesores y los ajustes de usabilidad del teléfono en A-01.

**Preparación (antes de empezar):**
1. Desde `backend/`: `pipenv run python manage.py migrate` y luego `pipenv run python manage.py runserver`.
2. Desde `frontend/`: `npm run dev` y abrir `http://localhost:3000`.
3. Carga los datos demo (DT-14, FX-15). Agrega a `backend/.env` (no se versiona) la línea `DEMO_PASSWORD=<una contraseña de 8+ caracteres, no solo números>` y ejecuta desde `backend/`: `pipenv run python manage.py setup_demo_data`. El comando imprime el id de cada propiedad y lo que le falta para publicar. Se puede repetir sin duplicar nada.
   - Inicia sesión como **`asesor.demo@urbanex.test`** con esa contraseña (el admin es `admin.demo@urbanex.test`).
   - `[DEMO] Terreno en Tumbaco - sin requisitos` → **V-02** (faltan los 3 requisitos). En **V-01** registra una propiedad nueva, como dicen sus pasos; el terreno sirve de alternativa (tampoco debe verse sin sesión).
   - `[DEMO] Departamento en La Carolina - sin avalúo` (tiene foto y corretaje) → **V-05 a V-11** (iniciar, calibrar y aprobar en I-12 y después publicar) y **V-12**.
   - `[DEMO] Local en La Mariscal - sin corretaje` → **V-03** (sube ahí el corretaje v1 y v2).
   - `[DEMO] Casa en Cumbayá - lista para publicar` → atajo de **V-11/V-12** si quieres probar la publicación sin pasar por I-12.
   - **Ojo:** los avalúos y documentos demo son inmutables y **no se pueden borrar** de tu BD local. Tu `db.sqlite3` cambiará: **no la incluyas en ningún commit** (DT-02).
4. Para V-03 ten a mano un PDF cualquiera; para V-04, ninguna preparación extra.

**Pruebas que cierran DT-40:** V-11 y V-12 (requieren antes V-05 a V-08).

### V-01 · HU-01 / DT-07 — Una propiedad en captación no es pública
1. Inicia sesión como asesor y registra una propiedad nueva con "+ Registrar propiedad" (título: `Prueba V-01`). Anota su id (aparece en la URL al pulsar "Avalúo").
2. Cierra sesión, o abre una ventana privada.
3. Abre `http://localhost:3000/properties`.
4. Abre `http://localhost:3000/properties/<id>`.

**Resultado esperado:** ¿`Prueba V-01` **no** aparece en el catálogo y su ficha **no** se abre? Hoy la ficha muestra "No se pudo cargar esta propiedad" con el aviso "Verifica la conexión con el servidor", aunque el servidor sí responde (404). Ese mensaje engañoso está registrado como DT-52: para esta prueba cuenta como **Aprobado** si no ves los datos de la propiedad.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | Al registrar la propiedad nueva, el formulario no dejó guardarla sin foto (la foto es la única exigencia del formulario, DT-34; el corretaje no lo exige). Sin sesión, la propiedad en captación no aparece en `/properties` y su ficha no muestra datos | **Aprobado** |

### V-02 · HU-53 — Publicar sin requisitos muestra lo que falta
1. Como asesor, en el dashboard, busca una propiedad **En captación** sin fotos, sin corretaje y sin avalúo (por ejemplo `Prueba V-01`).
2. Pulsa "Publicar" y acepta la confirmación.

**Resultado esperado:** ¿aparece sobre la tabla un aviso rojo con el texto `"<título>": No se puede publicar todavía. Falta:` y la lista de los 3 requisitos (foto, contrato de corretaje y avalúo), el del avalúo con el enlace "Ir al avalúo", y la propiedad **sigue En captación**?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | Se usó `#35 [DEMO] Terreno en Tumbaco - sin requisitos`, porque la propiedad de V-01 ya tenía foto. Aviso: `"[DEMO] Terreno en Tumbaco - sin requisitos": No se puede publicar todavía. Falta:` con foto, contrato de corretaje y avalúo (resumen de Pablo en la conversación; su nota escrita a mano copiaba solo las dos primeras líneas). La propiedad sigue "En captación" | **Aprobado** |

### V-03 · HU-03 — El expediente versiona el contrato de corretaje
1. En el dashboard, pulsa "Editar" en una propiedad tuya y ve a la pestaña **Expediente**.
2. Sube un PDF como contrato de corretaje con fechas de emisión y de vigencia (vigencia posterior a hoy) y pulsa Guardar.
3. Vuelve a abrir "Editar" → Expediente.
4. Sube otro PDF como contrato de corretaje y guarda. Vuelve a abrir.

**Resultado esperado:** ¿tras el paso 3 el contrato aparece como **v1**, estado "Pendiente" y **sin** opción de borrar? ¿Tras el paso 4 ves **v2** como vigente, y la v1 ya no figura como vigente?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27, 1.er intento | Subió un segundo PDF y solo seguía la v1. Causa: eligió el archivo y pulsó "Guardar cambios" **sin** pulsar "+ Agregar al expediente"; el archivo se descartó sin aviso (registrado como DT-60) | (repetido) |
| Pablo (`asesor.demo`) | 2026-10-27, 2.º intento | En `#32 [DEMO] Casa en Cumbayá`, pulsando "+ Agregar al expediente": aparece la **v2** como vigente (hasta 2026-10-31, con el aviso "vence pronto") y la v1 ya no figura como vigente | **Aprobado** |

### V-04 · HU-05 — La ubicación del mapa se guarda
1. "Editar" en una propiedad → pestaña **Ubicación**.
2. Busca un sector en el buscador (por ejemplo, `Cumbayá`) y haz clic en un punto del mapa.
3. Guarda, cierra el modal y vuelve a abrir "Editar" → Ubicación.

**Resultado esperado:** ¿el marcador aparece en el **mismo punto** que elegiste (y no en el centro por defecto de Quito)?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | Al volver a abrir Ubicación, el marcador está en el punto elegido | **Aprobado** |

### V-05 · HU-08 (I-12, paso 1) — Iniciar el avalúo es una acción explícita
1. En el dashboard, pulsa "Avalúo" en una propiedad en captación que nunca tuvo avalúo.

**Resultado esperado:** ¿ves el **"Precio actual de publicación"** en un campo gris que no se puede editar, el botón **"Iniciar avalúo"** y **ningún** avalúo creado todavía? Al pulsar "Iniciar avalúo", ¿aparece un folio con el formato `AV-AAAAMMDD-XXXXXX` y el formulario de calibración?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | En `#33 [DEMO] Departamento en La Carolina`: precio en el campo gris y botón "Iniciar avalúo"; al pulsarlo aparecen el folio y el formulario. La fecha del folio sale en UTC (registrado como DT-55) | **Aprobado** |

### V-06 · HU-08 (I-12, paso 2) — No se aprueba sin guardar
1. En el borrador recién iniciado, no escribas nada todavía.
2. Escribe un valor y una justificación, pero **no** pulses "Guardar borrador".

**Resultado esperado:** ¿"Aprobar avalúo" está **desactivado** en los dos casos y solo se activa después de "Guardar borrador" con un valor y una justificación?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | "Aprobar avalúo" desactivado con el borrador vacío y con cambios sin guardar | **Aprobado** |

### V-07 · HU-08 (I-12, paso 3) — Validación del valor calibrado
1. Escribe `0` como valor calibrado y pulsa "Guardar borrador".
2. Escribe `12,5` y pulsa "Guardar borrador".
3. Escribe `150000.50` y una justificación, y pulsa "Guardar borrador". Recarga la página.

**Resultado esperado:** ¿en los pasos 1 y 2 aparece bajo el campo el mensaje "Ingresa un valor mayor a 0, con máximo 2 decimales y sin separadores de miles."? ¿Tras el paso 3, al recargar, siguen el valor `150000.50` y la justificación?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | `0` y `12,5` muestran el error del campo; un valor válido se guarda. Observación: la UI muestra los montos como `$148.000,00` pero el campo exige `148000.00` (registrado como DT-56) | **Aprobado** |

### V-08 · HU-08 (I-12, paso 4) — La aprobación es irreversible
1. Pulsa "Aprobar avalúo".
2. Lee la confirmación y acéptala. Recarga la página.

**Resultado esperado:** ¿la confirmación dice que la acción es **irreversible**? Tras aceptar, ¿desaparece el formulario, queda una vista de **solo lectura** y el avalúo aparece en "Historial de avalúos aprobados", también después de recargar?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | Confirmación de irreversibilidad; después, vista de solo lectura y avalúo en el historial | **Aprobado** |

### V-09 · HU-08 (I-12, paso 5) — Reevaluar no borra el aprobado
1. En la misma pantalla, pulsa "Crear reevaluación".

**Resultado esperado:** ¿aparece un borrador **nuevo con otro folio**, y el avalúo aprobado de V-08 **sigue** en el historial?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | Borrador nuevo con otro folio; el historial conserva el aprobado | **Aprobado** |

### V-10 · HU-08 / HU-53 (I-12, paso 6) — El expediente refleja el avalúo
1. Vuelve al dashboard, pulsa "Editar" en esa propiedad y ve a la pestaña **Expediente**.

**Resultado esperado:** ¿la fila "Avalúo aprobado" dice **"Aprobado"** en verde y tiene el enlace "Abrir avalúo", que lleva a I-12?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | Fila "Avalúo aprobado" en verde con "Abrir avalúo" | **Aprobado** |

### V-11 · HU-53 / DT-46 — Publicar con todos los requisitos (cierra DT-40, parte 1)
1. Con la propiedad de V-05 a V-10: en "Editar", sube al menos **una foto** (Multimedia) y un **contrato de corretaje vigente** (Expediente, como en V-03). Guarda.
2. En el dashboard, pulsa "Publicar" y acepta la confirmación.

**Resultado esperado:** ¿aparece el aviso verde `"<título>" se publicó y ya está disponible en el catálogo.`, el estado pasa a **"Disponible"** y el botón "Publicar" **desaparece** de esa fila?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-27 | `#33` se publicó: aviso verde, estado "Disponible" y sin botón "Publicar". Observación: la tabla necesita scroll horizontal y "Publicar" queda cortado (registrado como DT-58) | **Aprobado** |

### V-12 · HU-53 / HU-01 — La propiedad publicada es pública (cierra DT-40, parte 2)
1. Cierra sesión, o abre una ventana privada.
2. Abre `http://localhost:3000/properties` y luego la ficha de la propiedad de V-11.

**Resultado esperado:** ¿la propiedad de V-11 **aparece** en el catálogo y su ficha **se abre** sin sesión?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (sin sesión) | 2026-10-27 | `#33` aparece en `/properties` y su ficha se abre. Observaciones: barra de navegación duplicada en la ficha (DT-25) y la etiqueta del catálogo dice "disponible" en minúscula (DT-57) | **Aprobado** |

### Ronda 2 — Tarea 3: modales y requisitos (rama `feat/URB-15-HU-53-modales-requisitos`)

> **Resultado de la ronda del 2026-10-28 (aprox. 15:30–16:05, hora de Ecuador):** Pablo, con `asesor.demo`. **Las 6 pruebas quedaron aprobadas**; V-14 y V-15 con datos distintos de los previstos y V-15 con un desvío (ver abajo). **DT-58 y DT-60 se cierran** con V-18 y V-17. Hallazgos nuevos: **DT-72** (el seeder no restaura el estado de las propiedades demo) y **DT-73** (se aprueban avalúos con valores no plausibles); N-05 suma evidencia. Queda una comprobación corta, **V-19**, para los mensajes que esta ronda no pudo ver.
>
> **Corrección del estado esperado (escrito el 2026-10-27 sin consultar la BD).** La consulta de solo lectura a `backend/db.sqlite3` del 2026-10-28 muestra que la ronda 1 ya había cambiado más datos de lo anotado:
> - `#34 La Mariscal` recibió el corretaje v1 (20:34 del 27-10, vigente hasta el 2026-11-29) y **se publicó a las 21:10 del 27-10**.
> - `#35 Tumbaco` tiene **2 avalúos aprobados**, creados a mano en I-12 por `asesor.demo` (20:47 y 21:26 del 27-10; $12,50 y $111,00). No vienen de `setup_demo_data`, que nunca da avalúo a Tumbaco.
> - `#32 Cumbayá` tiene, además del avalúo del seeder ($285.000), uno aprobado a las 21:23 del 27-10 por $123,99.
>
> Las horas de la BD están en UTC (DT-01) y aquí se pasan a la hora de Ecuador (UTC−5).

Preparación: la misma de arriba (`setup_demo_data` ya ejecutado; sesión como `asesor.demo`). Estado esperado de las propiedades demo tras la ronda 1 (tal como se escribió el 2026-10-27; ver la corrección de arriba): `#32 Cumbayá` en captación con todo; `#33 La Carolina` disponible; `#34 La Mariscal` sin corretaje; `#35 Tumbaco` sin requisitos.

### V-13 · HU-53 / DS-15 — Publicar pide confirmación en un modal
1. En el dashboard, pulsa "Publicar" en `#35 Tumbaco`.
2. Pulsa "Cancelar". Vuelve a pulsar "Publicar" y esta vez pulsa la tecla **Escape**.

**Resultado esperado:** ¿aparece un modal (no la ventana gris del navegador) titulado "¿Publicar esta propiedad?", que explica que pasará a Disponible y será pública? ¿"Cancelar" y Escape lo cierran **sin** publicar?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-28, aprox. 15:30–16:05 | Modal "¿Publicar esta propiedad?", no la ventana del navegador. "Cancelar" y Escape lo cierran sin publicar | **Aprobado** |

### V-14 · HU-53 / DS-15 — Lo que falta se explica en un modal con enlaces
1. Pulsa "Publicar" en `#35 Tumbaco` y confirma con "Publicar".
2. En el modal, pulsa "Abrir Multimedia".

**Resultado esperado:** ¿aparece el modal "No se puede publicar todavía" con los 3 requisitos (foto, corretaje, avalúo), cada uno con su enlace ("Abrir Multimedia", "Abrir Expediente", "Ir al avalúo")? ¿"Abrir Multimedia" abre la ficha de Tumbaco **directamente en la pestaña Multimedia**? ¿La propiedad sigue "En captación"?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-28, aprox. 15:30–16:05 | Modal "No se puede publicar todavía" con **2** requisitos, no 3: foto y corretaje, con "Abrir Multimedia" y "Abrir Expediente". El avalúo ya estaba cumplido por los 2 avalúos aprobados a mano en la ronda 1 (ver la corrección de arriba), así que el enlace "Ir al avalúo" del modal **no se vio** (queda en V-19). "Abrir Multimedia" abrió la ficha en la pestaña Multimedia (confirmado por Pablo en la conversación). Tumbaco sigue "En captación" (BD) | **Aprobado** (con datos distintos) |

### V-15 · HU-53 / DS-15 — El Expediente muestra los requisitos del servidor
1. "Editar" en `#34 La Mariscal` → pestaña Expediente.
2. "Editar" en `#32 Cumbayá` → pestaña Expediente.
3. "Editar" en `#33 La Carolina` → pestaña Expediente.

**Resultado esperado:** en el paso 1, ¿la fila "Contrato de corretaje" dice "Falta el contrato de corretaje." y el resumen dice "Según el servidor faltan 1 requisito(s)…"? En el paso 2, ¿el resumen en verde dice "Según el servidor está lista para publicar"? En el paso 3, ¿dice "Esta propiedad ya no está en captación (Disponible)"?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-28, aprox. 15:30–16:05 | **Paso 1 (La Mariscal):** "Esta propiedad ya no está en captación (Disponible)". Pablo lo anotó primero como "bloqueada por falta del contrato de corretaje" y lo corrigió en la conversación tras ver la consulta a la BD: `#34` está publicada desde el 27-10. Es el comportamiento correcto para una propiedad disponible, pero el mensaje "Según el servidor faltan N requisito(s)…" **no se vio** (queda en V-19). **Paso 2 (Cumbayá):** todos los requisitos en verde, "lista para publicar". **Paso 3 (La Carolina):** "ya no está en captación (Disponible)" | **Aprobado** (paso 1 con otros datos) |

> **⚠️ Desvío de V-15:** después de la prueba, Pablo **publicó `#32 Cumbayá`**, aunque la indicación era no hacerlo. Pasó a Disponible sin problemas (BD: `updated_at` 16:01 del 28-10). Con eso **ya no queda ninguna propiedad demo "lista para publicar" en captación**, y `setup_demo_data` **no la restaura**: registrado como **DT-72**. Cumbayá se publicó con un avalúo aprobado de $123,99 frente a un precio de $285.000: más evidencia para **N-05** y **DT-73**.

### V-16 · DS-15 — Los errores al guardar no cierran el modal
1. "Editar" en cualquier propiedad; en Datos generales, pega un **título de más de 200 caracteres** y pulsa "Guardar cambios".
2. Corrige el título (corto) y vuelve a guardar.

**Resultado esperado:** en el paso 1, ¿aparece **dentro del modal** un recuadro rojo "No se pudo guardar la propiedad:" con el mensaje del servidor sobre el título, y el modal sigue abierto con tus datos? En el paso 2, ¿se cierra el modal y aparece sobre la tabla un aviso verde `"<título>" se actualizó.`, sin ventanas del navegador?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-28, aprox. 15:30–16:05 | Con un título de 220 caracteres: recuadro rojo de error en "Datos generales" y el modal sigue abierto. Al restaurar el título: guarda, cierra y aparece el aviso verde | **Aprobado** |

### V-17 · DT-60 — Un archivo no agregado ya no se pierde en silencio
1. "Editar" en `#34 La Mariscal` → Expediente; elige un PDF en "Archivo" pero **no** pulses "+ Agregar al expediente".
2. Pulsa "Guardar cambios".
3. Pulsa "Quitar archivo".

**Resultado esperado:** en el paso 2, ¿el guardado se detiene en la pestaña Expediente con el mensaje `Elegiste "<archivo>" pero no lo agregaste…`? En el paso 3, ¿desaparecen el archivo elegido y el mensaje?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-28, aprox. 15:30–16:05 | Con el PDF elegido y sin agregar, el guardado se detiene con el aviso de agregarlo primero. "Quitar archivo" borra el archivo y el aviso. No pide confirmación; Pablo lo da por bueno porque el cambio se ve | **Aprobado** → **DT-60 cerrado** |

### V-18 · DT-58 — La tabla cabe sin scroll horizontal
1. Abre el dashboard en tu portátil, con la ventana del navegador maximizada. Anota el ancho aproximado de la pantalla.

**Resultado esperado:** ¿se ven los botones "Editar", "Avalúo" y "Publicar" completos **sin** scroll horizontal? (Si la pantalla es más estrecha que unos 1280 px, la columna "Asesor a cargo" se oculta a propósito.)

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-28, aprox. 15:30–16:05 | Navegador maximizado, viewport de **1868×884 px** (DevTools): "Editar", "Avalúo" y "Publicar" completos, sin scroll horizontal. **Solo se probó a ese tamaño**: no se vio la tabla por debajo de 1280 px, donde se oculta "Asesor a cargo" | **Aprobado** → **DT-58 cerrado** (a 1868 px) |

### V-19 · HU-53 / DS-15 — Mensajes que la ronda 2 no pudo ver (pendiente, corta)
Depende de **DT-72**: hoy ninguna propiedad demo en captación tiene foto y le falta solo un requisito, y ninguna está sin avalúo. Con lo que hay:
1. "Editar" en `#35 Tumbaco` → pestaña Expediente.

**Resultado esperado:** ¿el resumen dice "Según el servidor faltan 2 requisito(s) para publicar…" (foto y corretaje)?

El enlace "Ir al avalúo" **dentro del modal** de requisitos y el caso "falta solo el corretaje" se prueban cuando se resuelva DT-72 (una propiedad nueva en captación sin avalúo). Opcional: repetir V-18 con la ventana a menos de 1280 px de ancho.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| | | | Pendiente |

### Ronda 3 — Motor de avalúos DS-21 (rama `feat/URB-10-11-motor-avaluos`; validada el 2026-10-29 y el 2026-10-30)

> **Resultado:** las 6 aprobadas (V-25, tras FX-18). Hallazgos de la ronda: V-25 falló en el primer intento (corregido con **FX-18**); **DT-80** (I-12 identifica los comparables solo por id), **DT-81** (el registro manual tarda unos 3,5 s), **DT-82** (un admin creado desde A-01 no podrá entrar al admin de Django para gestionar θ), **N-05 ampliada** (¿el avalúo aprobado actualiza el precio? Ahora también es pregunta para la empresa), DT-01 con evidencia nueva (fechas del admin en UTC) y DT-74 con evidencia nueva (un borrador previo impidió repetir V-21).

**Preparación (en este orden, desde `backend/`):**
> **Hecho el 2026-10-28 en la copia de Pablo:** las migraciones ya estaban aplicadas y `setup_comparables_demo` creó los 11 comparables (La Carolina 1–6 = #40–#45; casas de Cumbayá = #46–#48). Verificado por consola contra la BD: V-21 da $143.861,35 (≈ $143.900, ALTO, CV 1,63 %), V-22 da MEDIO (CV 21,27 %), La Mariscal tiene 2 candidatos y Tumbaco 0, y #32 a #35 no tienen borradores abiertos. Puedes saltar los pasos 1 y 2.

1. `pipenv run python manage.py migrate`: aplica `appraisals.0002` y `0003` (θ v1). Tu `db.sqlite3` cambia: **no la incluyas en ningún commit** (DT-02).
2. `pipenv run python manage.py setup_comparables_demo`: crea 11 comparables sintéticos en "Vendido" (no salen en el catálogo ni en "Mis propiedades").
3. Reinicia `runserver` y `npm run dev`. Inicia sesión como `asesor.demo`.

Todas las propiedades demo ya tienen avalúos aprobados y ninguna tiene borrador, así que se entra por **"Avalúo" → "Crear reevaluación"** (DS-06), que ahora lleva a la pantalla I-11. Ojo: cada prueba deja un borrador que no se puede descartar (DT-74).

### V-20 · HU-04 — I-11 propone comparables del mismo tipo y zona
1. Dashboard → "Avalúo" en `#33 La Carolina` → "Crear reevaluación".
2. Desmarca "La Carolina 2" y marca y desmarca otros, hasta tener 2 y luego 6.

**Resultado esperado:** ¿aparecen **7** departamentos con su precio, m², USD/m² y distancia: los 6 "[COMP-SINT]" y, **al final**, tu `#36 [DEMO] Departamento de 2 pisos - Carolina Norte` (Disponible, 37 m², a 0,41 km)? ¿Vienen **5 marcados**: todos los "[COMP-SINT]" menos el de 120 m² ("La Carolina 3"), y el #36 sin marcar? (El #36 sale porque es un departamento de la misma zona; queda último por su superficie, muy distinta. Verificado contra la BD el 2026-10-28.) ¿Con 2 o con 6 marcados, "Calcular y crear borrador" queda **desactivado** y el contador lo indica?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-30 | En I-11 de `#33` (tras aprobar el borrador previo `AV-20261028-965538` y crear la reevaluación) aparecen **7 filas**, con la `#36 [DEMO] Departamento de 2 pisos - Carolina Norte` al final. Con 6 marcadas, "Calcular y crear borrador" se bloquea; con 5 se habilita; con menos de 3 tampoco deja calcular. En el primer intento (2026-10-29) se contaron 6 y se vio un borrador previo de `#33`, creado el 2026-10-28 a las 18:26 hora de Ecuador, que bloqueaba la reevaluación (DT-74) | **Aprobado** |

### V-21 · HU-06 — El motor calcula, redondea a cientos y explica
1. En la misma pantalla, marca exactamente "La Carolina 1, 2, 3, 4 y 5 (atípico)" (desmarca la 6).
2. "Calcular y crear borrador" → confirma en el modal.

**Resultado esperado:** ¿en I-12 el "Valor sugerido" muestra **≈ $143.900,00** y debajo "Exacto: $143.861,35"? ¿La confianza es **Alto**, con "Dispersión (CV): 1,63 %", y el origen "Motor paramétrico · parámetros v1"? ¿En la tabla, la fila de "La Carolina 5" aparece **en gris como atípico descartado**? (Son los números del ejemplo de DS-21 §8: la propiedad #33 tiene 95 m², como el ejemplo.)

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-30 | Primero se aprobó el borrador previo `AV-20261028-965538` en $144.000. Ese borrador se había calculado con la preselección de I-11 (`#40`, `#41`, `#43`, `#44`, `#45`: exacto $144.113,10, CV 1,05 %, `#44` en gris), lo que coincide con el motor para esa selección. Después, en una reevaluación con La Carolina 1 a 5: valor sugerido **$143.900**, exacto **$143.861,35**, CV **1,63 %**, confianza **Alto**; `#40` a `#43` usados y `#44` en gris ("vendido, atípico, descartado"). Son los números del ejemplo de DS-21 §8 | **Aprobado** |

### V-22 · HU-06 — Dispersión alta da confianza media
1. "Avalúo" en `#32 Cumbayá` → "Crear reevaluación" → con las 3 casas marcadas, "Calcular y crear borrador".

**Resultado esperado:** ¿la confianza es **Medio**, con un CV mayor que 15 %?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-29 | `#32` Cumbayá con las 3 casas sugeridas: confianza **Medio**, CV **21,27 %** (> 15 %); se ven el valor sugerido y el exacto | **Aprobado** |

### V-23 · HU-04 / C-02 — Con 2 comparables no se calcula
1. "Avalúo" en `#34 La Mariscal` → "Crear reevaluación".
2. Con los 2 locales marcados, pulsa "Registrar avalúo manual" y confirma.

**Resultado esperado:** en el paso 1, ¿aparece el aviso "Hay 2 comparable(s)… se necesitan 3. Registra el avalúo manual (C-02)" y "Calcular" queda desactivado? En el paso 2, ¿I-12 muestra "No disponible (registro manual)", confianza **Bajo** y el motivo "Menos de 3 comparables", con los 2 locales en la tabla como referencia?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-29 | `#34` La Mariscal con 2 comparables: "Registrar avalúo manual" (tardó unos 3,5 s, DT-81). En I-12, el valor sugerido dice "No disponible", la confianza es **Bajo** y las columnas factor, ajustado y peso salen vacías. Calibrado en $123.000 con justificación, guardado, aprobado y confirmado: quedó aprobado. No se anotó el texto del aviso de I-11 ni el motivo del registro manual | **Aprobado** |

### V-24 · HU-04 — Sin comparables
1. "Avalúo" en `#35 Tumbaco` → "Crear reevaluación".

**Resultado esperado:** ¿dice "No hay comparables del mismo tipo en la zona", con "Calcular" desactivado y "Registrar avalúo manual" activo? (No hace falta crear el avalúo.)

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`asesor.demo`) | 2026-10-29 | `#35` Tumbaco, sin comparables en la zona: "Calcular" desactivado y "Registrar avalúo manual" activo | **Aprobado** |

### V-25 · DS-21 capa 3 — θ versionado desde el admin
1. Abre `http://127.0.0.1:8000/admin/` como `admin.demo` → "Parámetros del motor (θ)".
2. "Agregar": el formulario viene precargado con la versión activa. Cambia `"alfa": "5"` por `"alfa": "0"`, escribe una nota y guarda.
3. Selecciona la versión 1 → acción "Activar la versión seleccionada".

**Resultado esperado:** ¿tras el paso 2 hay una **versión 2 activa** y la 1 sigue en la lista, ya inactiva? ¿Al abrir la versión 1, todos sus campos son de **solo lectura**? ¿Tras el paso 3 vuelve a estar **activa la 1**? (Déjala activa al terminar.)

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (`admin.demo`) | 2026-10-29 / 2026-10-30 | **Primer intento (2026-10-29): Fallido.** Django decía que `admin.demo` no tenía permiso para ver ni editar nada, y "Parámetros del motor" no aparecía. Causa: el admin de θ solo daba por rol el permiso de agregar (FX-18). **Tras FX-18 (2026-10-30):** `admin.demo` ve "Parámetros del motor" y creó la **v2** (`alfa` = 0), que quedó activa con `created_by = admin.demo`; la v1 se desactivó. Después reactivó la v1. Observación: el admin muestra las fechas en UTC (DT-01). No se anotó si la v1 se ve de solo lectura | **Aprobado** (tras FX-18) |

---

### Ronda 4 — HU-44 · Invitaciones y administración de usuarios (Pendiente)

> **Antes de empezar:** para que los enlaces de prueba no salgan a un proveedor externo, usa `EMAIL_PROVIDER=console` en la configuración local del backend y reinícialo. El enlace se imprime en la consola. No uses Resend para estas pruebas manuales.

### V-26 · HU-44 — Crear usuario y localizar el enlace de activación
1. Inicia sesión como administrador y abre `/dashboard/users`.
2. Crea un asesor con un correo nuevo de prueba.
3. Busca en la consola del backend el correo de activación y abre o copia su enlace.

**Resultado esperado:** ¿A-01 confirma la creación, muestra la cuenta pendiente/inactiva y la consola contiene el enlace `/activate#...` sin exponer una contraseña temporal?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | Creó un asesor desde A-01; se mostró el mensaje de éxito y el correo con el enlace de activación apareció en la consola local. No se envió desde Resend | **Aprobado** |

### V-27 · HU-44 — Activar la cuenta e iniciar sesión
1. Desde el enlace de V-26, establece una contraseña válida en la pantalla de activación.
2. Ve a `/login` e inicia sesión con el correo y la contraseña que acabas de establecer.
3. Cierra sesión, vuelve a iniciar sesión como administrador, abre A-01 y revisa el estado de la cuenta.

**Resultado esperado:** ¿la pantalla confirma la activación, el usuario puede iniciar sesión y A-01 lo muestra activo?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | Abrió el enlace, estableció la contraseña y pudo iniciar sesión con la cuenta activada | **Aprobado** |

### V-28 · HU-44 — Rechazar un enlace de activación usado
1. Crea otra invitación y activa la cuenta con su enlace.
2. Abre de nuevo el mismo enlace o intenta enviarlo una segunda vez.

**Resultado esperado:** ¿se rechaza el segundo uso con un mensaje de enlace inválido o vencido, sin cambiar la contraseña ya establecida? La expiración de 24 horas se cubre además en las pruebas automatizadas.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | Tras activar la cuenta, volvió a intentar el enlace usado y la activación fue rechazada | **Aprobado** |

### V-29 · HU-44 — Reenviar una invitación
1. Crea un asesor nuevo y conserva el primer enlace de activación de la consola.
2. Desde A-01, reenvía la invitación y localiza el nuevo enlace en la consola.
3. Intenta activar con el enlace anterior y luego con el nuevo.

**Resultado esperado:** ¿el enlace anterior se rechaza, el nuevo permite activar la cuenta y A-01 refleja el estado actualizado?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | El backend respondió 200 al reenvío desde A-01, imprimió un nuevo enlace en la consola y confirmó que, al existir dos enlaces, el antiguo ya no sirve | **Aprobado** |

### V-30 · HU-44 — Desactivar un asesor, impedir su acceso y liberar sus propiedades
1. Crea y activa un asesor de prueba; inicia sesión con él y registra una propiedad.
2. Cierra sesión, vuelve a entrar como administrador en A-01 y desactiva al asesor con un motivo.
3. Intenta iniciar sesión con el asesor desactivado y verifica en `GET /api/auth/properties/` o el admin de Django que la propiedad aún existe y tiene `agent: null`.

**Resultado esperado:** ¿A-01 conserva la cuenta como inactiva y muestra el motivo, el asesor no puede iniciar sesión y la propiedad sigue existiendo pero queda sin responsable?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | Desde A-01 desactivó una cuenta de asesor. El asesor no pudo iniciar sesión y sus propiedades permanecieron registradas, sin responsable asignado | **Aprobado** |

### V-31 · HU-44 — Restringir A-01 a administradores
1. Inicia sesión con un asesor.
2. Comprueba que la navegación no ofrece A-01 e intenta abrir directamente `/dashboard/users`.
3. Comprueba que `GET /api/auth/users/` responde 403 para ese asesor.

**Resultado esperado:** ¿el asesor no ve ni puede acceder a la lista o las acciones de A-01, incluso al usar la URL directa?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | Con sesión de asesor, no pudo ver A-01 y comprobó desde la consola del navegador que `GET /api/auth/users/` respondió 403 | **Aprobado** |

### V-32 · A-01 — Validar el celular ecuatoriano
1. En `/dashboard/users`, crea o edita una cuenta con un celular como `0991234567`; también prueba escribirlo con espacios, guiones o paréntesis.
2. Prueba un número que no empiece con `09`, uno con letras y uno internacional con `+593`.

**Resultado esperado:** el celular local de 10 dígitos se guarda normalizado como `09XXXXXXXX`; los valores inválidos se rechazan con un mensaje y no se acepta el formato internacional.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-10-30 | Confirmó que los cambios finales funcionan: solo se pueden ingresar hasta 10 dígitos, el teléfono se ve en la lista y el formulario aparece a la vista | **Aprobado** |

---

## Estado actual (2026-10-30)

- **Ronda 3 validada** (V-20 a V-25, Pablo, 2026-10-29 y 2026-10-30): las 6 aprobadas.
- **HU-44 (Fase B):** rama local reconstruida sobre `origin/develop` (`9801bc9`); se conserva el respaldo `respaldo/HU-44-antes-de-faseB`. **Suite backend: 116/116 OK** con SQLite y correo de consola (53/53 en `apps.users.tests`). Sebas confirmó V-26 a V-32, incluida la invalidación del enlace anterior, el 403 de la API y los ajustes finales de usabilidad del teléfono. La validación manual anterior se hizo el 2026-10-30 usando Supabase PostgreSQL según Sebas. Los commits se publicaron en la rama; la PR está pendiente del inicio de sesión de GitKraken.
- **Seguridad de pruebas (FX-19):** `UserManagementApiTests` fuerza el proveedor de consola y las dos pruebas específicas de Resend parchean el punto de uso en `apps.users.serializers`; así una `.env` local con Resend no dispara llamadas externas durante la suite.
- **Migraciones:** `users.0007` y `users.0008` aplicadas en la base PostgreSQL conectada. `showmigrations` aún muestra pendientes `appraisals.0002` y `appraisals.0003`; no se aplicaron durante esta tarea. `makemigrations --check --dry-run` propone únicamente `documents/0002_alter_document_file.py` (DT-77); no se generó el archivo.
- **Frontend:** `npm run build` y `npx tsc --noEmit -p .` aprobados; ESLint sin errores y con 2 warnings previos de `SiteNav` no usado.
- **FX-18 (2026-10-30):** el admin de θ da por rol admin, además de agregar, los permisos de ver la app y la lista (`backend/apps/appraisals/admin.py`), con 2 pruebas nuevas (`EngineParametersAdminTests`). Sin la corrección, la prueba falla igual que V-25. La suite base de `origin/develop` fue 90/90.
- **Hallazgos nuevos:** DT-80, DT-81 y DT-82; N-05 ampliada (pregunta también para la empresa); evidencia nueva en DT-01 y DT-74.
- **Siguiente:** PR a `develop`. HU-04, HU-06 y HU-08 completas: **POR CONFIRMAR** (C-02 y θ v1 provisionales, pendientes del tutor).

### Estado anterior (2026-10-28, noche)

- **PR #6 (tarea 3) fusionada** en `develop` (`44ccd2e`).
- **Rama `feat/URB-10-11-motor-avaluos`** (desde `develop`), en 7 commits:
  - `2368420`: docs (DS-21 aprobada, DS-22, DS-23);
  - `739f7a7`: fase 1, núcleo;
  - `0b158da`: fase 2, θ versionado;
  - `97bb755`: fase 3, comparables sintéticos;
  - `ca3542a`: fase 4, HU-04 y HU-06 en el backend;
  - `ba466b8`: fase 5, I-11 e I-12;
  - el commit del handoff y del ajuste de I-11.
- **Pruebas:** suite **88/88 OK**; `makemigrations --check` sin cambios; `tsc` y `next build` exit 0; `eslint`: **2 errores previos de DT-24, ninguno nuevo** (corregido el 2026-10-29: `npx eslint .` → 2 errores y 4 avisos en `login/page.tsx:49` y `dashboard/page.tsx:233`, que vienen de `28d117fd` y `2c8d4c45`, ambos anteriores a esta rama).
- **Validación visual pendiente:** V-20 a V-25. *(Hecha el 2026-10-29/30: ver "Estado actual".)*
- **DT-65:** resuelto en la copia de Pablo (DS-24). La propuesta para sacar la BD del repositorio está en [Seguridad §5.3](docs/handoff/URBANEX_SEGURIDAD_Y_DEUDA.md#53-dejar-de-versionar-dbsqlite3-y-media-inf-03-dt-70-dt-02-n-04) y **no se ejecutó** (N-04).
- **Hallazgos nuevos:** DT-74 (un borrador impide recalcular), DT-75 (la antigüedad del dato se mide con `updated_at`) y DT-76 (I-11 muestra datos de mercado de otros asesores).
- **Preguntas para el tutor:** C-02 frente a RF-11, la superficie en viviendas y el resto, en la conversación del 2026-10-28.
- **Avisar a Sebas:**
  - ejecutar `migrate` y `setup_comparables_demo`;
  - inutilizar las 3 cuentas publicadas en su copia (DT-65);
  - no se tocó ningún archivo compartido de GPS §3.

## Estado anterior (2026-10-27)

- **PR #2 (`feat/URB-15-HU-53-proceso-publicacion` → `develop`) fusionada el 2026-10-27 a las 13:19 (hora local, `ddf4223`).** Evidencia del PR: 52/52 pruebas automáticas y pruebas manuales por **Postman** (publicar sin avalúo → 400; borrador → calibrar → aprobar). **No hubo validación en la interfaz:** HU-08 y HU-53 siguen con la parte funcional y la visual **Pendientes** (ver la sección de validaciones de arriba).
- El último commit de ese PR (`ef43c52`) versionó `backend/db.sqlite3` y 3 `.pyc`: registrado en **DT-02**. No se ejecutó `git rm --cached` (depende de N-04).
- **Rama actual:** `feat/URB-13-HU-08-pantalla-avaluo`. Con URB-15 ya en `develop`, se integra ahora por PR (DS-09). La fusión de prueba con `origin/develop` no tiene conflictos (`git merge-tree` → exit 0; `develop` solo trae los 4 binarios de `ef43c52`, que esta rama no toca).
- **Línea base 2026-10-27:** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **52/52 OK**.
- **Respuestas de Pablo a las 7 preguntas del 2026-10-27:** registradas como DS-14 a DS-18 en [Deuda técnica §4](docs/handoff/URBANEX_DEUDA_TECNICA.md#4-decisiones-tomadas-sesión-2026-10-24-aprobadas-por-pablo).

### Seeder (2026-10-27, rama `chore/DT-14-seeder-datos-demo`)
- La PR #3 (URB-13) se fusionó en `develop` el 2026-10-27 a las 21:18 UTC (`45250ec`). La rama del seeder sale de ese `develop`.
- **`817da84` (FX-15):** comando `pipenv run python manage.py setup_demo_data` (`backend/apps/users/management/commands/setup_demo_data.py`) según DS-17. Uso y propiedades en la **Preparación** de la sección de validaciones.
- **Pruebas:** 6 nuevas (`SetupDemoDataCommandTests`): sin `DEMO_PASSWORD` falla; con `DEBUG=False` se niega; roles, `is_staff` y contraseña; las 4 propiedades en captación con los requisitos esperados (`get_missing_publication_requirements`) y sin valor sugerido; repetir no duplica y actualiza la contraseña; no aprueba un borrador abierto. `manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **58/58 OK**; `makemigrations --check` → sin cambios.
- **No ejecutado** sobre la BD local de Pablo: crea registros que no se pueden borrar y modifica `db.sqlite3` (rastreado, DT-02). Lo ejecuta Pablo al preparar la validación.
- Hallazgo nuevo: **DT-54** (Pillow no está en el `Pipfile`).

### Tarea 5: seguridad e infraestructura (2026-10-27, rama `docs/DT-42-seguridad-y-deuda`)
- **Solo documentación, sin cambios de código ni de configuración.** Nuevo [`URBANEX_SEGURIDAD_Y_DEUDA.md`](docs/handoff/URBANEX_SEGURIDAD_Y_DEUDA.md), **publicable**: sin pasos de explotación. Los detalles de reproducción se guardan en privado, fuera del repositorio.
- **Contenido:**
  - inventario SEC-01 a SEC-12 e INF-01 a INF-04, cada uno con categoría, componente, severidad, estado y plan;
  - control de acceso;
  - JWT (recomendación B para D-05, sin implementar);
  - entradas y archivos;
  - DT-42 (POR CONFIRMAR);
  - base de datos y almacenamiento (objetivo del contexto maestro §2; momento y proveedor POR CONFIRMAR);
  - dejar de versionar `db.sqlite3`/`media/`;
  - requisitos previos al despliegue.
- **⛔ Regla DS-20:** ningún despliegue, tampoco el de demostración, con riesgos Altos abiertos.
- **DS-19:** despliegue de demostración aprobado por el tutor (aprox. 2026-10-20), fuera de la infraestructura de la empresa. **✅ Servicios confirmados por Pablo: Vercel + Render + Supabase** (las del contexto maestro §2); el momento del despliegue sigue POR CONFIRMAR.
- **⚠️ ¡ACCIÓN PARA PABLO! (DT-65):** la `db.sqlite3` versionada en el repositorio público contiene credenciales cifradas de cuentas de desarrollo. Cambia esas contraseñas (y donde las reutilices).
- **Nuevos en Deuda técnica:** DT-61 a DT-71 (sección "Seguridad e infraestructura"), DS-19 y DS-20. **Ampliados:** DT-10, DT-20, DT-39 y DT-42.

### Orden acordado (2026-10-27)
1. ~~**PR de URB-13 → `develop`**~~ Fusionada (PR #3).
2. **Seeder** `setup_demo_data` (DT-14, DS-17): **hecho** en `chore/DT-14-seeder-datos-demo` (`817da84`). En la misma rama: Pillow declarado en `Pipfile`/`Pipfile.lock` (cierra DT-54) y registro de la validación. Falta la PR hacia `develop`.
3. ~~**Validación visual de Pablo**~~ **Hecha el 2026-10-27:** V-01 a V-12 aprobadas; **DT-40 cerrado**. Hallazgos: DT-25 (actualizado), DT-55 a DT-60 y N-05 (pregunta para el tutor). HU-08 completa: **POR CONFIRMAR** hasta el plazo de D-04 (2026-10-28, 08:00; ver arriba).
4. **Tarea 3:** modales/avisos con Tailwind en `dashboard/page.tsx` + `GET …/publication-requirements/` en el Expediente (DS-15). **Hecha el 2026-10-27** en `feat/URB-15-HU-53-modales-requisitos` (desde `develop` `7a43bad`), en 4 commits:
   - `5e68dce`, fase 1: endpoint + 6 pruebas + tipo TS;
   - `cf62881`, fase 2a: componente `Dialog`;
   - `3bda58f`, fase 2b: dashboard;
   - `a3a8f13`, fase 3: DT-60 y DT-58.

   Backend **64/64 OK**; `tsc` y `next build` OK; `eslint` solo con el error previo de DT-24. **Avisar a Sebas:** se tocaron `users/views.py`, `users/urls.py` y `dashboard/page.tsx`.

   **Validación visual hecha el 2026-10-28:** V-13 a V-18 aprobadas (Pablo, `asesor.demo`). Se cierran DT-58 y DT-60. Hallazgos: DT-72, DT-73 y evidencia nueva para N-05. Línea base antes de preparar la PR: `manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **64/64 OK** (2026-10-28). Siguiente paso: la PR hacia `develop`, que abre Pablo en GitHub (DT-53).
5. **Tarea 5:** `docs/handoff/URBANEX_SEGURIDAD_Y_DEUDA.md` (incluye las opciones de DT-42). **Hecha el 2026-10-27** en `docs/DT-42-seguridad-y-deuda` (desde `develop` `47b59ce`, tras fusionar la PR #4 del seeder); ver "Tarea 5" abajo.
6. **Motor de avalúos (DS-21, DS-22, 2026-10-28)**, en la rama `feat/URB-10-11-motor-avaluos`, por fases:
   1. núcleo puro;
   2. θ versionado (`EngineParameters`);
   3. comparables sintéticos (DS-23);
   4. backend de HU-04 y HU-06;
   5. pantalla I-11 y resultado en I-12.
7. **Tarea 4:** filtros del catálogo P-02 (HU-10 / URB-16, adelantada) solo con los campos existentes (DS-16). **Se pospone hasta después del motor (DS-22).**

Las tareas 4 a 6 empiezan después de fusionar la PR del seeder, cada una en su rama desde `develop` (DS-14).

---

## Sesión anterior (2026-10-25)

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
Las validaciones de esta sesión se movieron, con pasos y resultado esperado, a la sección **"Validaciones pendientes de Pablo"** al inicio de este archivo (V-01 a V-12). Al 2026-10-27 **seguían sin hacerse**: no se hicieron el 2026-10-26 porque no hay usuario asesor (DT-14).

### Próxima tarea (de esa sesión; la vigente está en "Estado actual")
1. ~~Fase 3 de DT-40~~ Hecha el 2026-10-25 (`3783919`).
2. Registrar el resultado de las validaciones de Pablo (quién, cuándo, qué se vio) y, si pasan, cerrar DT-40 y marcar como validados los criterios de HU-08 y HU-53 en Avance de épicas.
3. ~~Abrir las PR en orden: URB-15 → `develop`~~ (fusionada el 2026-10-27) y después URB-13 (DS-09). Tras fusionar, cada copia ejecuta `migrate`. **Avisar a Sebas** de que la fase 3 modificó `dashboard/page.tsx`.
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
Movidas a la sección **"Validaciones pendientes de Pablo"** al inicio de este archivo (V-01, V-02, V-11 y V-12).

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

### Pendientes del 2026-10-28 (pausa de Pablo el 2026-10-27 por la noche; archivado el 2026-10-29)
1. ~~**⏰ 08:00 — D-04:** ¿llegó la fórmula del motor?~~ **No llegó. Plan B activado por Pablo el 2026-10-28:** la propuesta [DS-21](docs/handoff/URBANEX_DS-21_MOTOR_AVALUOS.md) **se aprobó el mismo día con carácter provisional** (D-04 resuelta provisionalmente). El motor se implementa en `feat/URB-10-11-motor-avaluos`.
2. ~~**🧪 URGENTE — Validaciones V-13 a V-18**~~ **Hechas el 2026-10-28 (15:30–16:05): las 6 aprobadas**, registradas en "Ronda 2". Queda V-19 (corta).
3. ~~**🔑 DT-65:** cambiar las contraseñas de las cuentas de la `db.sqlite3` publicada~~ **Hecho en la copia de Pablo el 2026-10-28 (DS-24):** contraseñas inutilizables y sin superusuario. Falta la copia de Sebas.
4. ~~Abrir la PR de la tarea 3~~ **Fusionada el 2026-10-28 (PR #6).** **Nuevo orden (DS-22):** primero el motor (HU-04 y HU-06, con I-11) y después la tarea 4 (filtros P-02, DS-16).
5. **🧪 Ronda 3 (motor DS-21):** V-20 a V-25. Antes, `migrate` y `setup_comparables_demo`. *(Sigue pendiente al archivar: ver "Pendiente ahora".)*

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
