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
   `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → hoy **58 OK** (desde el seeder, 2026-10-27). Si la sesión toca el frontend, también `npx tsc --noEmit -p .` (desde `frontend/`).

### Reglas
- **No inventar decisiones pendientes** (D-04 fórmula del motor, C-02, N-02, N-03, etc.). Si una HU depende de una, se usa un placeholder documentado y se pregunta.
- **Si el código y el handoff se contradicen, se detiene el trabajo** y se pregunta al responsable; se corrige el que esté mal y se registra.
- **Archivos compartidos** (`backend/apps/users/models.py`, `users/migrations/`, `backend/config/settings.py`, `frontend/types/property.ts`, `frontend/app/dashboard/page.tsx`): avisar antes de tocarlos (GPS §3).
- **Las transiciones de estado no son un PATCH genérico**: cada una es una acción explícita con sus precondiciones verificadas en el servidor (contexto maestro §11).
- **Un cambio no está terminado** hasta que, en el mismo PR/commit, se actualicen Estado de procesos, Deuda técnica, GPS, Avance de épicas y este archivo, con evidencia (comando + resultado).
- Estándares de código y checklist DoD: [`URBANEX_ESTANDARES_DOD.md`](docs/handoff/URBANEX_ESTANDARES_DOD.md). Requisitos: [`URBANEX_MASTER_CONTEXT.md`](docs/handoff/URBANEX_MASTER_CONTEXT.md) (la copia de `docs/handoff/` es la de referencia).

---

## ⏰ ¡PLAZO ABIERTO! D-04 — FÓRMULA DEL MOTOR DE AVALÚOS

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

---

## Estado actual (2026-10-27)

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

### Orden acordado (2026-10-27)
1. ~~**PR de URB-13 → `develop`**~~ Fusionada (PR #3).
2. **Seeder** `setup_demo_data` (DT-14, DS-17): **hecho** en `chore/DT-14-seeder-datos-demo` (`817da84`). En la misma rama: Pillow declarado en `Pipfile`/`Pipfile.lock` (cierra DT-54) y registro de la validación. Falta la PR hacia `develop`.
3. ~~**Validación visual de Pablo**~~ **Hecha el 2026-10-27:** V-01 a V-12 aprobadas; **DT-40 cerrado**. Hallazgos: DT-25 (actualizado), DT-55 a DT-60 y N-05 (pregunta para el tutor). HU-08 completa: **POR CONFIRMAR** hasta el plazo de D-04 (2026-10-28, 08:00; ver arriba).
4. **Tarea 3:** modales/avisos con Tailwind en `dashboard/page.tsx` + `GET …/publication-requirements/` en el Expediente (DS-15).
5. **Tarea 5:** `docs/handoff/URBANEX_SEGURIDAD_Y_DEUDA.md` (incluye las opciones de DT-42).
6. **Tarea 4:** filtros del catálogo P-02 (HU-10 / URB-16, adelantada) solo con los campos existentes (DS-16).

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
