# Urbanex — Progreso

| Campo | Valor |
|---|---|
| Actualización HU-45 | 2026-11-04 · Rama avanzada a `origin/develop` (`043cfb5`, PR #15); se conservaron `PropertyOwnershipTests` y `AccountUnlockApiTests`. Según Sebas, V-43 cubrió bloqueo tras cinco intentos y desbloqueo por admin. Suite integrada: 159/159 OK en SQLite; migraciones detectan `documents/0002_alter_document_file.py` (DT-92), sin generarla ni aplicarla. |
| Última actualización aditiva | 2026-11-05 · Copilot con Sebas · corrección documental de la auditoría HU-45: DT-120, aclaraciones de Seguridad/USM y pendientes explícitos para el PR |
| Confirmación para PR #17 (2026-11-05) | Según Sebas, el cambio en `backend/apps/users/views.py` fue coordinado antes. Nota preparada para Pablo: DT-111 (`slug` de HU-12, pendiente y fuera de HU-45), DT-49 (usar `git commit -F` en PowerShell 5.1), DT-120 (notificación persistente fuera de HU-45), DT-92 (diferencia conocida; no se generó ni aplicó migración) y PostgreSQL **No ejecutado**. No se publicó la nota: el PR #17 apunta a `master`, en conflicto con `AGENTS.md` §5; requiere aclaración/corrección por Pablo. |
| Estado PR #17 (2026-11-06) | El PR ahora apunta a `develop`. DT-120 está registrado localmente en `b30e5c9`, pendiente de push. Sigue pendiente adjuntar al PR la captura solicitada de que una cuenta no administradora no puede desbloquear; la ruta referenciada por V-43 (`evidence/HU-45/V-43.png`) no existe en este checkout. |
| Última actualización | 2026-11-08 · Pablo (con Claude) · rama `feat/URB-19-18-27-HU-22-HU-18-HU-24-visitas` (PR #19, borrador): validación visual del lote 2, **Ronda 6** (V-65 a V-77, todas Aprobadas), DS-37, DT-143 a DT-147 y nota de cierre. Antes: 2026-11-04 (noche) · Pablo (con Claude Code) · correcciones de la auditoría de solo lectura del PR #15 (No apto, solo por documentación): nota de cierre del merge al día (push ya hecho), V-26..V-32 del 2026-11-03 citadas en Estado y Avance, nueva sección **Traza de la rama** y nota de cierre. Antes: 2026-11-04 (después del merge) · Pablo (con Claude Code) · suite tras el merge (155 OK, `npm test` 9/9), conteo en el paso 6 del protocolo y nota de cierre. Antes: 2026-11-04 · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades`: merge de `origin/develop` (`5fb3910`, con los PR #14 y #16); se conservan las entradas de ambos lados. Antes (develop): 2026-11-03 (tarde) · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`: correcciones de la auditoría de solo lectura de HU-12 (rutas de las capturas de V-60 a V-62, DT-111, Seguridad §3.1), suite y nota de cierre. Antes: 2026-11-03 · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`: merge de `origin/develop` (`40dd147`, sumando filas), BD del worktree reiniciada, V-64 (escape de metaetiquetas) aprobada por Pablo, Seguridad §3.1 y nota de cierre. Antes: 2026-11-03 · Pablo (con Claude Code) · rama `docs/user-story-mapping` (PR #13, borrador): merge de `origin/develop`, columna Código y anclas del USM, fila en el GPS §3 y nota de cierre. Antes: 2026-11-03 · Pablo (con Claude Code) · rama `feat/URB-02-HU-44-gestion-usuarios`: corrección de la documentación según la auditoría del PR #9 (filas de `develop` restauradas, DT-96 POR CONFIRMAR, DT-115 y DT-116). Antes: 2026-11-02 · Sebas · rama `feat/URB-02-HU-44-gestion-usuarios`: merge con `origin/develop`, documentación de HU-44 y validaciones técnicas; suite backend 116/116, build y TypeScript exit 0, ESLint exit 0 con 2 avisos; `makemigrations --check --dry-run` exit 1 por `documents/0002`. Antes: 2026-10-31 · Pablo · rama `docs/reglas-ia-y-deuda`: `AGENTS.md` (DS-25), correcciones de auditoría (FX-22, SEC-15) y nota de cierre de sesión · Rama HU-12: 2026-11-02 · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`: V-60 a V-62 aprobadas por Pablo, V-63 Pendiente (DT-110), nuevo DT-112. Antes: 2026-11-01 · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`: HU-12, metaetiquetas de la ficha (FX-24), validaciones V-60 a V-63 Pendientes, DT-110 y DT-111. Antes: 2026-10-31 · Pablo · rama `docs/reglas-ia-y-deuda`: `AGENTS.md` (DS-25), correcciones de auditoría (FX-22, SEC-15) y nota de cierre de sesión · Rama de oportunidades: 2026-11-03 (noche, 23:50) · Pablo (con Claude Code) · V-26 a V-32 repetidas con hora y captura (fila nueva en cada V), suite 155 OK y nota de cierre. Antes: 2026-11-03 (noche) · Pablo (con Claude Code) · correcciones de la auditoría de solo lectura: título de "Pendiente ahora" y Ronda 4 con un solo estado; DT-117/SEC-16. Antes: 2026-11-03 (tarde) · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (PR en borrador): merge de `origin/develop` (`46033df`, con los PR #9 y #13), DT-14 y DT-39 con C-08 confirmada, DT-105 comprobado, pruebas de DT-106 y DT-107 (FX-25), suite 155 OK y nota de cierre. |

---

## ⚠️ DIRECTIVA DE CONTINUIDAD (GPS) — Regla estricta y obligatoria

> Resumen; la fuente de reglas es [`AGENTS.md`](AGENTS.md).

> **La carpeta `docs/handoff/` es el ecosistema central de navegación del proyecto y la única fuente de verdad.**
> Ningún desarrollador ni asistente de IA debe escribir código, implementar una HU, alterar modelos compartidos ni modificar flujos de negocio **sin antes consultar obligatoriamente** estos tres documentos:
>
> 1. [`URBANEX_ESTADO_PROCESOS.md`](docs/handoff/URBANEX_ESTADO_PROCESOS.md): qué hace hoy cada HU frente al proceso real de la inmobiliaria.
> 2. [`URBANEX_DEUDA_TECNICA.md`](docs/handoff/URBANEX_DEUDA_TECNICA.md): riesgos abiertos (P0 primero), decisiones pendientes que **no se inventan** y decisiones ya tomadas que **no se rediscuten**.
> 3. [`URBANEX_GPS_ARCHIVOS.md`](docs/handoff/URBANEX_GPS_ARCHIVOS.md): qué archivo implementa qué HU, su riesgo y qué coordinar antes de tocarlo.

### Por qué existe
Urbanex debe reflejar los **procesos de la inmobiliaria** (captación → expediente + avalúo → publicación → …), no solo un CRUD. Cada vez que se programó sin mirar el handoff aparecieron fallas de proceso: catálogo con fichas internas (DT-07), publicación sin requisitos (DT-08). Esta directiva evita perder el hilo entre sesiones, entre personas y entre asistentes de IA.

### Protocolo de inicio (cada sesión, antes de cualquier cambio)
1. `git status --short --branch` y `git pull`: confirmar rama y cambios ajenos. Si el pull trae cambios en `Pipfile`, ejecutar `pipenv sync`. Si trae migraciones nuevas: revisar `showmigrations`, confirmar que la conexión activa es la SQLite local (`DB_ENGINE=sqlite` en `backend/.env`) y recién entonces ejecutar `pipenv run python manage.py migrate`. Nunca ejecutar `migrate` contra Supabase. (corregido por Pablo, 2026-11-03)
2. Leer este archivo completo (sobre todo **Próxima tarea**).
3. Leer **Estado de procesos** → la HU objetivo y sus criterios.
4. Leer **Deuda técnica** → P0/P1 que afecten a la HU; decisiones `D-xx`/`N-xx`/`C-xx` pendientes y `DS-xx` tomadas.
5. Leer **GPS de archivos** → archivos implicados, riesgo y si son compartidos.
6. Ejecutar la línea base de pruebas (desde `backend/`) y anotar el resultado:
   `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → `develop`: **90 OK** (FX-18); con HU-44 fusionada: **116 OK** (53 de `users`), con SQLite y correo de consola. (corregido por Pablo, 2026-11-03) Si la sesión toca el frontend, también `npx tsc --noEmit -p .` (desde `frontend/`).
   Rama de oportunidades: el comando lleva además `apps.opportunities.tests` → **155 OK** (55 users, 19 documents, 44 appraisals, 37 opportunities; FX-25, 2026-11-03). Antes: 151 al fusionar `develop`; sin `develop`, 125 (FX-19). **(2026-11-04)** Tras fusionar `develop` `5fb3910` (PR #14 y #16, sin pruebas de backend nuevas): **155 OK** otra vez; en `frontend/`, `npm test` → 9/9 (HU-12).

### Reglas
- **No inventar decisiones pendientes** (D-04 fórmula del motor, C-02, N-02, N-03, etc.). Si una HU depende de una, se usa un placeholder documentado y se pregunta.
- **Si el código y el handoff se contradicen, se detiene el trabajo** y se pregunta al responsable; se corrige el que esté mal y se registra.
- **Archivos compartidos** (`backend/apps/users/models.py`, `users/migrations/`, `backend/config/settings.py`, `frontend/types/property.ts`, `frontend/app/dashboard/page.tsx`): avisar antes de tocarlos (GPS §3).
- **Las transiciones de estado no son un PATCH genérico**: cada una es una acción explícita con sus precondiciones verificadas en el servidor (contexto maestro §11).
- **Un cambio no está terminado** hasta que, en el mismo PR/commit, se actualicen Estado de procesos, Deuda técnica, GPS, Avance de épicas y este archivo, con evidencia (comando + resultado).
- Estándares de código y checklist DoD: [`URBANEX_ESTANDARES_DOD.md`](docs/handoff/URBANEX_ESTANDARES_DOD.md). Requisitos: [`URBANEX_MASTER_CONTEXT.md`](docs/handoff/URBANEX_MASTER_CONTEXT.md) (la copia de `docs/handoff/` es la de referencia).

---

## 📝 Notas de cierre de sesión (la más reciente arriba; regla de `AGENTS.md` §10)

### 2026-11-08 (noche) · Pablo (con Claude) · rama `feat/URB-19-18-27-HU-22-HU-18-HU-24-visitas` (PR #19, ya no es borrador)
- **Auditoría de solo lectura (§11):** "Merge con correcciones menores". Suite 228/228 OK, `npm test` 17/17, build/tsc exit 0, eslint 0 errores (2 avisos DT-24), `makemigrations --check` solo `documents/0002` (DT-92).
- **Decisión (Pablo, 2026-11-08):** las capturas de V-65 a V-77 **no se recapturan**. Queda como evidencia el registro escrito de cada V (quién, cuándo, qué vio).
- **Corregido:** `clean()` de `AgentAvailability` y `Visit` ya no lanza `ValueError` sin horas (500 en el admin), con la prueba `CleanWithoutTimesTests`; nota en DS-37 (commit de la constante). La nota anterior decía "PR #19, borrador": el PR ya no está en borrador.
- **Observación sin ID (rango DT por definir):** el límite de 30/min del endpoint público usa la caché local (LocMemCache), así que cuenta por proceso; revisar caché compartida y `NUM_PROXIES` al desplegar.
- **Falta:** comando de la §4 del DoD con `apps.visits.tests` (228); filas del GPS para los archivos nuevos; decidir el rango de DT-140+ en `AGENTS.md` §4 (DT-143..147 ya usados); título y descripción del PR (orden explícita de Pablo, DS-31); avisar a Sebas del conflicto en `SiteNav.tsx` y `Project_Progress.md` con la rama HU-46; suite en PostgreSQL pendiente (DT-68).

### 2026-11-08 · Pablo (con Claude) · rama `feat/URB-19-18-27-HU-22-HU-18-HU-24-visitas` (PR #19, borrador)
- **Hecho:** validación visual del lote 2 (HU-22, HU-18, HU-24 y la barra por rol) en el worktree `Urbanex-lote2`, con SQLite local y `EMAIL_PROVIDER=console`: **V-65 a V-77 Aprobadas por Pablo** (2026-11-07, 20:55, a 2026-11-08, 00:28). Ver **Ronda 6**. Sin cambios de código.
- **Registrado:** DS-37 (antelación mínima de 2 h configurable), DT-143 (exclusión de visitas cruzadas en PostgreSQL, con HU-19) y DT-144 a DT-147 (observaciones de interfaz de la ronda, P3). La agenda (HU-24) muestra nombre, teléfono y correo del cliente al asesor: pregunta abierta para el tutor, anotada en DT-117/SEC-16.
- **Evidencia:** Pablo tomó las capturas de cada V, pero se guardaron en `Urbanex-lote2\capturas\` (dentro del worktree, sin rastrear) y un agente las borró por error con `Remove-Item -Recurse -Force` el 2026-11-08 durante la corrección de este commit. Queda el registro escrito de cada V (quién, cuándo, qué vio). **Pendiente (Pablo): decidir si se recapturan** con la misma BD del worktree; si se hace, se agrega una fila nueva en cada V con la fecha real.
- **Nota:** `admin.demo` no es staff de Django; en V-73 la visita se creó con `setup_visits_demo` y se canceló por shell.
- **Falta:** quitar el borrador del PR #19, auditoría de solo lectura (`AGENTS.md` §11) y merge. HU-22, HU-18 y HU-24 siguen en **Pruebas** hasta entonces.

### 2026-11-06 · Copilot con Sebas · evidencia V-43 para PR #17
- **Hecho:** se registró la prueba manual de acceso como Asesor en V-43 para publicar la actualización de la bitácora en la rama `feat/URB-03-HU-45-desbloquear-cuenta`.
- **Evidencia:** commit `2bd4be8` publicado en la rama del PR; suite backend SQLite: 159 pruebas OK (exit 0). `makemigrations --check --dry-run`: exit 1 por la diferencia conocida `documents/0002_alter_document_file.py` (DT-92), sin generar ni aplicar migraciones. La ruta `evidence/HU-45/V-43-no-admin.png` no existe en este checkout; Sebas confirmó que la captura se adjuntará o ya está adjunta al PR por separado.
- **Pendiente:** confirmar que la captura esté adjunta al comentario del PR.
- **Siguiente paso:** confirmar que la captura esté adjunta al comentario del PR #17.

### 2026-11-05 · Copilot con Sebas · aclaración de PR #17
- **Hecho:** Sebas confirmó que el cambio en `backend/apps/users/views.py` se había coordinado antes; la pregunta pendiente en la nota siguiente queda resuelta. Texto preparado para Pablo, sin publicar: «Según Sebas, el cambio en `backend/apps/users/views.py` fue coordinado previamente. DT-111 (`slug` estable de HU-12) sigue pendiente y fuera de HU-45; DT-49 indica usar `git commit -F <archivo>` en PowerShell 5.1. La notificación persistente de HU-45 se sigue en DT-120. DT-92 (`documents/0002_alter_document_file.py`) es una diferencia conocida; no se generó ni aplicó migración. Suite contra PostgreSQL: **No ejecutado**; se coordinará más adelante con Pablo».
- **Evidencia:** PR #17 está abierto desde `feat/URB-03-HU-45-desbloquear-cuenta` con destino `master`; `AGENTS.md` §5 indica integrar por PR a `develop`. Suite backend SQLite: 159 pruebas, OK (exit 0). `makemigrations --check --dry-run`: exit 1, detecta `documents/0002_alter_document_file.py` (DT-92). PostgreSQL: **No ejecutado**. No se publicó comentario ni se cambió el destino del PR.
- **Pendiente:** Pablo debe aclarar/corregir el destino del PR y publicar la nota con la autorización requerida. No se tocaron los otros archivos de documentación modificados previamente.
- **Siguiente paso:** coordinar con Pablo la corrección del destino a `develop` antes de actualizar el PR.

### 2026-11-06 · Copilot con Sebas · preparación del push de PR #17
- **Hecho:** se confirmó que el PR #17 apunta a `develop` y que DT-120 aún no aparece en su commit remoto. La deuda técnica ya está registrada en el commit local `b30e5c9`; se preparan las aclaraciones relacionadas de Estado, Seguridad y USM para subirlas en la misma rama.
- **Pendiente:** falta la captura pedida en el PR que demuestre que un usuario no administrador no puede desbloquear. La captura V-43 registrada en esta bitácora cubre el flujo de desbloqueo por admin y login posterior, y su ruta `evidence/HU-45/V-43.png` no existe en este checkout. Adjuntar la nueva captura como respuesta al comentario del PR; no incluir credenciales ni datos personales.
- **Siguiente paso:** subir los cambios documentales a la rama del PR y adjuntar la captura humana pendiente antes de dar por atendida la revisión.

### 2026-11-05 · Copilot con Sebas · rama `feat/URB-03-HU-45-desbloquear-cuenta`
- **Hecho:** correcciones documentales de la auditoría HU-45: DT-120 queda asignado a la notificación persistente y DT-117 sigue identificado como SEC-16/LOPDP; se aclararon como históricas las afirmaciones antiguas sobre login y desbloqueo en Seguridad y USM. La fila antigua del USM queda señalada como supersedida por las actualizaciones de 2026-11-03/04.
- **Evidencia:** `git fetch origin`; búsqueda de DT-120..DT-139 en las ramas remotas actualizadas: sin coincidencias en las tablas de deuda/seguridad. Línea base backend SQLite ejecutada en esta sesión: `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → 159 pruebas OK, exit 0. No se ejecutó PostgreSQL ni se accedió o modificó `test_postgres`.
- **Pendiente:** en el PR, anotar que DT-92 (`documents/0002_alter_document_file.py`) es la diferencia conocida/preexistente, no generada ni aplicada en esta rama, y que PostgreSQL queda **No ejecutado** hasta coordinar con Pablo un entorno autorizado. Confirmar con Pablo la coordinación previa sobre `backend/apps/users/views.py`; si no se avisó antes, avisar ahora y dejar constancia honesta.
- **Siguiente paso:** incorporar esas notas en el PR cuando Pablo lo prepare y resolver con él la coordinación de `views.py` y el entorno PostgreSQL.

### 2026-11-04 · Copilot con Sebas · rama `feat/URB-03-HU-45-desbloquear-cuenta`
- **Hecho:** rama adelantada por fast-forward a `043cfb5` (PR #15 integrado en `develop`); se restauraron los cambios guardados sin borrar los stashes, se conservaron `PropertyOwnershipTests` y `AccountUnlockApiTests`, y se resolvieron los seis conflictos. Según Sebas, V-43 se ejecutó después del último ajuste e incluyó el bloqueo tras cinco intentos, el desbloqueo en A-01 y el login posterior.
- **Evidencia backend:** desde `backend/`, con `DB_ENGINE=sqlite` y `PIPENV_DONT_LOAD_ENV=1` (sin cargar `.env`; `EMAIL_PROVIDER` quedó en su valor por defecto `console`), `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → `Ran 159 tests`, **OK** (exit 0). La advertencia JWT y el rechazo de Resend corresponden a pruebas; el rechazo está simulado con `mock.patch` en `apps/users/tests.py`.
- **Evidencia adicional:** desde `backend/`, `pipenv run python manage.py makemigrations --check --dry-run` → exit 1; detecta `apps/documents/migrations/0002_alter_document_file.py` (DT-92). No se generó ni aplicó migración. Desde `frontend/`: `npm test` 9/9; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0 con 2 avisos de `SiteNav`; `npm run build` exit 0 (11/11 páginas).
- **Pendiente:** PostgreSQL no verificado. El intento con la configuración por defecto abortó antes de correr pruebas porque ya existe `test_postgres`; no se borró ni reutilizó esa base. Coordinar con Pablo el entorno PostgreSQL autorizado y DT-92; después, hacer la auditoría de solo lectura en un chat nuevo. No se hizo commit, push ni PR.
- **Siguiente paso:** coordinar con Pablo la base de pruebas PostgreSQL y el tratamiento de DT-92; cuando estén resueltos, completar la auditoría previa al PR.

### 2026-11-04 (noche) · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (PR #15, borrador)
- **Hecho:** auditoría de solo lectura sobre `105cfd6`: **No apto**, solo por documentación. Código, migraciones, IDs y merge sin problemas: de las 305 líneas que agregaron los PR #14 y #16 no se perdió ninguna; hay una sola sección de notas y no quedan marcadores de conflicto. `gh pr view 15` → `mergeable: MERGEABLE` (BLOCKED: borrador y sin revisión). Con el "ok" de Pablo: nota de cierre del merge al día (push ya hecho), V-26..V-32 del 2026-11-03 citadas en Estado de procesos y Avance de épicas, y nueva sección **Traza de la rama** (abajo). Cuerpo del PR y mensaje para Sebas redactados en un borrador de correo para Pablo; el PR lo edita Pablo en GitHub (DS-31).
- **Evidencia:** `connection.vendor` = `sqlite`; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → `Ran 155 tests in 305.362s` · `OK`; `makemigrations --check --dry-run` → "No changes detected", exit 0. Frontend: `npx tsc --noEmit -p .` exit 0; `npx eslint .` 0 errores y 2 avisos (DT-24); `npm test` 9/9. `npm run build`: **No ejecutado** en esta sesión (escribe `.next`). Suite contra PostgreSQL: **No ejecutado** (DT-01).
- **Hallazgos sin arreglar:** `settings.py` y `urls.py` van en commits mezclados (`257ba1c`, `4282a87`), contra `AGENTS.md` §5; se explica en el PR, sin reescribir el historial. Las filas de V-26..V-32 del 2026-11-01 siguen como "Aprobado" sin captura; quedan como antecedente.
- **Falta:** ~~suite contra PostgreSQL o N/A con motivo (decisión de Pablo); `npm run build`; enviar el aviso a Sebas; pegar el cuerpo del PR; push de este commit (con la orden de Pablo);~~ nueva auditoría de solo lectura en un chat nuevo. **(2026-11-04, más tarde)** Push de `6cfdd53` hecho con la orden de Pablo. `npm run build` lo corrió Pablo en `frontend/`: "Compiled successfully", 11/11 páginas, incluidas `/dashboard/opportunities` y `/dashboard/opportunities/new` (Next.js 16.3.4). Pablo envió el aviso a Sebas. PostgreSQL: pendiente por decisión de Pablo (no hay PostgreSQL local), registrado como nota en DT-68. Pablo pega el cuerpo del PR (corregido por Pablo, 2026-11-04).
- **Siguiente paso:** PostgreSQL y build → aviso a Sebas → push → auditoría → PR #15 listo → merge → quitar "Rama sin fusionar" de HU-27 y HU-34 en el USM.

### 2026-11-04 · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (PR #15, borrador)
- **Hecho:** merge de `origin/develop` (`5fb3910`, con el PR #14 de HU-12 y el PR #16 de DS-31) en `2fac92d`, sin rebase ni squash. Hubo 13 conflictos, todos en los 7 `.md` del handoff. Se conservaron las filas y notas de ambos lados: en las celdas "Última actualización", la entrada del merge, el texto completo de `develop` y las entradas propias de la rama; una sola sección de notas de cierre, con las del mismo día ordenadas por la hora de sus commits; V-26..V-32 y V-60..V-64 sin tocar. Sin IDs repetidos entre los dos lados (DT, FX, DS, SEC y V). Un script comparó a tres bandas que no se perdiera ninguna línea. En `386fb45`, por decisión de Pablo: en la Deuda se quitaron la línea en blanco y el fragmento duplicado de DS-31 que dejó `23ae175` y que cortaban la tabla.
- **Evidencia:** `connection.vendor` = `sqlite`; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → `Ran 155 tests` · `OK` (igual que la línea base antes del merge); `makemigrations --check --dry-run` → "No changes detected", exit 0. Frontend: `npm test` → 9/9; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0, 0 errores y los 2 avisos de `SiteNav` (DT-24); `npm run build` exit 0. No se corrió `migrate`. Suite contra PostgreSQL: **No ejecutado** (DT-01).
- **Falta:** ~~el push de estos 3 commits (con la orden de Pablo, sin force);~~ push hecho: `origin/feat/URB-30-34-HU-27-HU-34-oportunidades` = `105cfd6`, comprobado con `git ls-remote` (corregido por Pablo, 2026-11-04); la auditoría de solo lectura en un chat nuevo (`AGENTS.md` §11); el texto del PR; avisar a Sebas de `PropertyOwnershipTests`; que Pablo marque el PR #15 como listo y lo fusione.
- **Siguiente paso:** auditoría → PR #15 listo → merge → quitar "Rama sin fusionar" de HU-27 y HU-34 en el USM.

### 2026-11-03 (noche) · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (PR #15, borrador)
- **Hecho:** correcciones de la auditoría de solo lectura (`ceb4a70`); DT-117/SEC-16, datos personales de EP-5 (`0f7292b`); DT-109 resuelto: BD local reiniciada con respaldo en el Escritorio, `migrate` en SQLite y `setup_demo_data` (`c3cf5ed`). Pablo publicó A (Casa en Cumbayá) y B (Local en La Mariscal, con PDF de corretaje) y repitió **V-26 a V-32 con hora y captura** (22:51 a 23:49), todas **Aprobadas** por él. Hay una fila nueva en cada V, con las rutas de las capturas en OneDrive, fuera del repo.
- **Evidencia:** suite → `Ran 155 tests` · `OK` (SQLite); `makemigrations --check --dry-run` → "No changes detected". Suite contra PostgreSQL: **No ejecutado** (DT-01).
- **Observaciones:** el correo de Gemini del 2026-11-03 da por hechas la validación de fechas cruzadas y V-32 antes de que se hicieran (luego se hicieron, 23:46 y ~23:50) y menciona un merge que no se decidió. Se toma como fuente el dictado de Pablo y las capturas. ~~Pregunta abierta: ¿se registra como DT-118 que el catálogo vacío diga "No hay propiedades registradas aún" cuando sí hay propiedades, pero ninguna disponible?~~ Registrado como **DT-118** (P3) por decisión de Pablo (corregido por Pablo, 2026-11-03).
- **Falta:** ~~push de los commits locales (con orden de Pablo);~~ push hecho con la orden de Pablo, sin auditoría nueva por su decisión (corregido por Pablo, 2026-11-03); el texto del PR (nota sobre `settings.py` y `urls.py` en `257ba1c` y `4282a87`); avisar a Sebas de `PropertyOwnershipTests`; una nueva auditoría de solo lectura si Pablo la pide; marcar el PR como listo y fusionarlo (decisión de Pablo).
- **Siguiente paso:** Pablo autoriza el push → PR #15 listo → merge → quitar "Rama sin fusionar" de HU-27 y HU-34 en el USM.

### 2026-11-03 (tarde) · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`
- **Hecho:** correcciones de la auditoría de solo lectura (No apto por documentación), sin tocar código. (1) Las rutas de las 6 capturas de V-60 a V-62 apuntan a `C:\Users\Pablo\OneDrive\Documentos\Urbanex\evidencias\HU-12\Pruebas anteriores (cambiar)\`, donde están ahora (no se movió ningún archivo). (2) DT-111 y "Fuera de alcance" de HU-12: el PR #9 ya se fusionó (`d71c7f2`); la migración del `slug` en `apps/users` se coordina con Sebas (HU-45). (3) Seguridad §3.1: el payload RSC se cita como `\u003c/script\u003e`. Decidido por Pablo: no se reordena el texto de `develop` en las cabeceras; la regla de `gh` va en la rama aparte `docs/regla-gh-solo-consultas` (DS-31).
- **Evidencia (en `ed396fd`; el código no cambió después):** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → `Found 116 test(s)`, **OK**; `makemigrations --check --dry-run` → exit 1, propone `documents/0002_alter_document_file.py` (DT-77/DT-92, no se creó); `npm test` → `tests 9 · pass 9 · fail 0`.
- **PostgreSQL (N/A decidido por Pablo, 2026-11-03; texto para el checklist DoD del PR, lo pega Pablo):** "Suite contra PostgreSQL: N/A. Motivo: cambio solo de frontend (`frontend/app/properties/[id]/page.tsx`, `frontend/lib/propertyMetadata.ts`, su prueba y `frontend/package.json`); no hay modelos, migraciones, vistas ni consultas nuevas en el backend. Suite en SQLite: 116 OK; `npm test`: 9/9."
- **PR (consultado con `gh pr list` y `gh pr view 14`, sin modificarlo):** #14, borrador, abierto, base `master`, cabeza `294358a`. Su descripción es una sola línea ("PR that it just for test and draft…"): **no tiene checklist DoD** ni el texto de PostgreSQL. La base `master` no coincide con `AGENTS.md` §5 (se vuelve a `develop` por PR); hallazgo para Pablo, no se tocó.
- **Falta:** V-63 (DT-110, al desplegar), DT-111 (`slug`, con Sebas), pegar el texto de PostgreSQL en el PR, nueva auditoría de solo lectura y pasar el PR a listo (Pablo).
- **Siguiente paso:** auditoría de solo lectura → Pablo pasa el PR a listo.

### 2026-11-03 · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`
- **Hecho:** merge de `origin/develop` (`a071b97`, trae los PR #9 y #13) en `40dd147`. Hubo 7 conflictos, todos de documentación; se resolvieron sumando filas, sin reescribir las ajenas, y un script comprobó a tres bandas que no se perdió ninguna línea editada. **BD del worktree reiniciada** (DT-109; la BD de la carpeta principal la reinicia Pablo aparte): el `db.sqlite3` del worktree estaba vacío (0 bytes, respaldo en el Escritorio), `pipenv sync`, `migrate` (SQLite local, comprobado antes) y `setup_demo_data`. **V-64 aprobada por Pablo**: un título malicioso sale escapado en `<title>`, Open Graph y Twitter (Seguridad §3.1). En Seguridad se restauraron, por decisión de Pablo, dos frases de la celda "Fecha" que `develop` había perdido.
- **Evidencia:** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **116 OK**; `makemigrations --check --dry-run` propone `documents/0002_alter_document_file.py` (síntoma del worktree, DT-77/DT-92; no se creó). Frontend: `npm test` 9/9, `tsc` exit 0, `eslint` 0 errores y 2 avisos previos, `next build` exit 0. Línea base antes del merge: backend no ejecutable (Django sin instalar en el entorno del worktree); `npm test` 9/9.
- **Falta:** V-63 (al desplegar, DT-110), DT-111 (`slug`), suite contra PostgreSQL (No ejecutada), auditoría de solo lectura (`AGENTS.md` §11), push y PR (lo abre Pablo).
- **Siguiente paso:** auditoría en un chat nuevo → corregir → push (cuando Pablo lo diga) → PR.

### 2026-11-03 (tarde) · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (PR en borrador)
- **Hecho:** merge de `origin/develop` (`a071b97`, con los PR #9 y #13) en `46033df`. Hubo conflictos solo en documentación; se conservaron las filas de ambos lados, quedó una sola sección de notas de cierre y C-08 tiene el texto de `develop`, con una nota añadida. `frontend/CLAUDE.md` deja de versionarse (FX-21); la copia local sigue ignorada. En `bc53be6`: notas en DT-14 y DT-39 (C-08 confirmada, DS-30; SEC-01 sigue abierto) y DT-105/FX-23 resueltos, comprobados con HU-44 fusionada. En `36d1cec`: DT-106, dos pruebas del 403 de `IsInternalUser` con el rol heredado `cliente`. En `1ee3c1b`: DT-107, `PropertyOwnershipTests` en `users/tests.py` (asesor A dueño, 200; asesor B, 403 en PATCH, publish y requisitos), sin renombrar `client_user`. Registro: FX-25.
- **Evidencia:** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → `Ran 155 tests` · `OK` (SQLite, `connection.vendor` = `sqlite`); `makemigrations --check --dry-run` → "No changes detected", exit 0. Frontend: `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0 con los 2 avisos de `SiteNav` (DT-24); `npm run build` exit 0. No se corrió `migrate` (ni local ni contra Supabase). Suite contra PostgreSQL: **No ejecutado** (DT-01).
- **Falta:** la auditoría de solo lectura en un chat nuevo (`AGENTS.md` §11); ~~que Pablo confirme cómo leer el criterio de cierre de DT-107 (POR CONFIRMAR, ver su fila);~~ DT-107 Resuelto: el criterio se lee como "ninguna prueba usa `cliente` como rol válido" (corregido por Pablo, 2026-11-03); el commit 4 (enlace en el menú, DT-101) solo con su orden; avisar a Sebas de que `users/tests.py` tiene una clase nueva al final (choca con HU-45 si él también agrega al final). No hay V-xx nuevas: no cambia la interfaz.
- **Siguiente paso:** auditoría en un chat nuevo → Pablo marca el PR como listo y lo fusiona → quitar "Rama sin fusionar" de HU-27 y HU-34 en el §4 del USM.

### 2026-11-03 · Pablo (con Claude Code) · rama `docs/user-story-mapping` (PR #13, borrador)
- **Hecho:** merge de `origin/develop` (`d71c7f2`, trae el PR #9) en `77d68cd`, sin conflictos. En [`URBANEX_USM_TRAZABILIDAD.md`](docs/handoff/URBANEX_USM_TRAZABILIDAD.md) (`2347fa2`), §4: la columna **Código** quedó completa con archivos y endpoints de `develop` (Parcial, Rama sin fusionar o No implementado), y HU-12, HU-27 y HU-34 se citan con su rama sin fusionar. Las anclas `#hu-xx` se comprobaron: 13 existen y las de HU-27 y HU-34 no existían. Las HU de EP-3 a EP-6 sin sección en ningún documento quedan con "—", por decisión de Pablo. HU-44 ya no figura como "sin fusionar". En el §6, la fila 7 dice que C-08 está confirmada (DS-30). Fila del USM en el GPS §3 (`10d2ccc`). Suite después del merge: `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **116 OK** (SQLite); `makemigrations --check --dry-run` → "No changes detected", exit 0. Antes del merge, la línea base dio 90 OK.
- **Falta:** el corte del 60 % (§2) y el §6 siguen como **PROPUESTA**, y el recálculo va aparte. Entre lo que queda está la fila 8 del §6: D-05 solo cubre JWT y sesión. Avance de épicas cubre solo EP-1 y EP-2; por decisión de Pablo no se abre DT. También falta la auditoría de solo lectura (`AGENTS.md` §11) y agregar la tarjeta de HU-05 en Miro.
- **Siguiente paso:** auditoría en un chat nuevo → Pablo marca el PR #13 como listo y lo fusiona. Cuando se fusionen HU-12 o la rama de oportunidades, quitar la marca "Rama sin fusionar" en el §4 del USM.

### 2026-11-03 · Pablo (con Claude Code) · rama `feat/URB-02-HU-44-gestion-usuarios`
- **Hecho:** corrección de la documentación según la auditoría del PR #9, solo en `.md` (sin código ni migraciones). Filas de `develop` restauradas con su texto exacto: FX-05, FX-17, DT-12, DT-14 (a su lugar), DT-15, DT-21, DT-24, DT-26, DT-39, DT-43, DT-65, DT-68, DT-82, DS-13, DS-24 y DS-25; lo nuevo de Sebas pasó a notas añadidas con autor y fecha. DT-13 sin contradicción y **no resuelto**. El reinicio de Supabase (DT-96) queda como **propuesta POR CONFIRMAR** en Deuda, Progress, Seguridad, GPS y Guía. Nuevos **DT-115** (desactivar un asesor borra el captador; aceptado por ahora, se corrige en HU-02) y **DT-116** (riesgos de `users.0007`). Restaurados el historial de "Última actualización" y tres puntos de "Pendiente ahora" (PR #11, ronda 3, DT-65).
- **Falta:** la decisión sobre DT-96. (Los pasos 1 y 6 del protocolo de inicio, que Sebas había cambiado, los combinó Pablo en un commit aparte.) La PR #11 ya se fusionó (`3748e7f`), pero su punto se restauró con el texto de `develop`.
- **Siguiente paso:** Sebas hace pull de esta rama antes de volver a escribir en ella.

### 2026-11-02 · Sebas · rama `feat/URB-02-HU-44-gestion-usuarios`
- **Hecho:** se añadió el registro histórico reportado del cambio de `717d55b` a `3f8bed8` mediante rebase/force push, con aprobación posterior atribuida a Pablo el 2026-10-31. Git confirma ambos commits y sus metadatos, pero no demuestra por sí solo el force push ni esa aprobación. Se conserva `2c07f7d8` como referencia histórica de GPS y FX-05/DS-13.
- **Falta:** el texto íntegro del prompt original no está en el repositorio; este registro se limita a los datos compartidos en la conversación. Siguen pendientes V-33..V-42 y la suite local contra PostgreSQL.
- **Siguiente paso:** conservar los cambios locales restaurados del stash; coordinar la evidencia humana y la validación PostgreSQL según los pendientes ya documentados.

### 2026-11-02 · Sebas · rama `feat/URB-02-HU-44-gestion-usuarios`
- **Hecho:** merge de `origin/develop` en `8ff1e9f`; stash aplicado sin conflictos. Se conserva sin incluir en commits el cambio local de `.vscode/settings.json` y un archivo sin seguimiento con nombre anómalo. Documentación de HU-44, ambiente, deuda y decisiones actualizada en `27724a8`; commit y push normales completados. Suite backend: 116/116 OK; `npm run build` y `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0 con 2 avisos; `makemigrations --check --dry-run` exit 1 por la diferencia preexistente `documents/0002_alter_document_file.py`.
- **Falta:** validación humana V-33..V-42 y suite local contra PostgreSQL (**No ejecutado**); no resolver la diferencia de migración en este alcance.
- **Siguiente paso:** coordinar con Pablo la evidencia humana pendiente y la propuesta DT-96 (POR CONFIRMAR) (corregido por Pablo, 2026-11-03); confirmar respaldo y ambiente antes de cualquier restablecimiento o migración.

### 2026-11-02 · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`
- **Hecho:** Pablo validó HU-12 en local (incógnito, `localhost:3001`): **V-60, V-61 y V-62 aprobadas**. V-63 sigue Pendiente (DT-110: necesita una URL pública). Registrado **DT-112**: la ficha inexistente dice "Verifica la conexión con el servidor".
- **Observaciones de la validación:** la primera vez fue sin hora ni capturas (`AGENTS.md` §9 pide ambas). **Pablo repitió V-60 a V-62 el mismo día con hora y captura** (6 capturas en `C:\Users\Pablo\OneDrive\Documentos\Urbanex\evidencias\HU-12\Pruebas anteriores (cambiar)\`, ruta actualizada el 2026-11-03; revisadas por Claude Code). V-60 se hizo con `/properties/1` y V-61 con `/properties/7`, no con `#33` y `#35`. La #1 tiene `property_type` = `"no_disponible"` (dato local, DT-109, registrada en la rama de oportunidades, sin fusionar; revisar en HU-05).
- **Falta:** V-63 (al desplegar), DT-111 (`slug`, tras el PR #9), auditoría de solo lectura (`AGENTS.md` §11), push y PR (lo abre Pablo).
- **Siguiente paso:** auditoría en un chat nuevo → corregir lo que reporte → push → PR.
- **Correcciones de la auditoría (mismo día, sin tocar código):** el párrafo "Validación funcional pendiente" vuelve a HU-53 en Estado de procesos; las primeras filas de V-60 a V-62 quedan como "Reemplazada por la repetición con captura"; DT-109 se cita como registrada en la rama de oportunidades, sin fusionar; Pablo confirma "Técnica: Aprobado" de HU-12; nuevos **DT-113** (el mismo patrón en 9 HU anteriores, sin tocarlas) y **DT-114** (Progress y Deuda fuera de GPS §3). **Pendiente:** la prueba de escape de las metaetiquetas (XSS), que hace Pablo; el resultado va en Seguridad §3.1. **Aplazada al 2026-11-03:** la #1 pertenece a un usuario borrado y no se puede editar; Pablo reiniciará la BD local (DT-109) con `migrate` y el seeder y hará la prueba con una ficha pública de `asesor.demo`. Queda anotada como Pendiente en Seguridad §3.1. Nota: el frontend del worktree debe correr en el puerto 3000 para iniciar sesión (CORS solo permite 3000 en `backend/config/settings.py`). **El PR se abre después de fusionar el #9.**

### 2026-11-01 · Pablo (con Claude Code) · rama `feat/URB-17-HU-12-compartir-ficha`
- **Hecho:** HU-12 / URB-17, solo frontend. `generateMetadata` en la ficha P-03 con título, descripción (precio referencial), imagen principal, Open Graph y Twitter, solo para fichas Disponibles o Reservadas. Las demás dan "Propiedad no disponible \| Urbanex" con `noindex` (FX-24). 9 pruebas con `npm test` (`node --test`, sin dependencias). Commits `2305868` y `d690286`, más el de documentación.
- **Cómo se trabajó:** en un worktree aparte (`../Urbanex-hu12`, desde `develop` `3748e7f`), por decisión de Pablo, para no tocar su carpeta ni su `db.sqlite3`. La rama no tiene upstream; **no se hizo push**.
- **Evidencia:** backend 90/90 OK (línea base, sin cambios); `npm test` 9/9; `next build` y `tsc` exit 0; `eslint` con los mismos 6 problemas previos. El backend de Pablo no estaba corriendo, así que el HTML se comprobó con un backend falso: disponible con foto, reservada sin foto y 404.
- **Falta:** V-60 a V-63 (Pablo); la previsualización real necesita una URL pública (DT-110); `slug` tras el PR #9 (DT-111); auditoría de solo lectura (`AGENTS.md` §11) y PR.
- **Observación de la línea base:** en el worktree, `makemigrations --check` propone `documents/0002_alter_document_file.py`. Es el síntoma de DT-77 (ruta absoluta en `documents.0001`), que aparece porque el worktree vive en otra carpeta. No se creó ninguna migración.
- **Siguiente paso:** Pablo hace V-60 a V-63 → auditoría → push y PR.

### 2026-11-01 (noche) · Pablo (con Claude Code) · `feat/URB-30-34-HU-27-HU-34-oportunidades`

- **Hecho:** ronda 4 validada por Pablo en el navegador (sin capturas): **V-26 a V-32 Aprobadas**. Antes se aplicó `migrate` en la BD local (`opportunities.0001`, y además `appraisals.0002` y `0003`, que estaban pendientes) y se corrió `setup_demo_data` (propiedades #32 a #35 en captación). Quedaron en la BD local las oportunidades #1 a #3.
- **Hallazgos nuevos:** DT-108 (la #1 y la #2 tienen el mismo título y la misma dirección, y no se distinguen en I-06 ni en I-07) y DT-109 (BD local con datos basura). No se corrigen ahora.
- **Falta:** que Pablo decida si HU-27 y HU-34 pasan de **Pruebas** a **Listo** (Estado de procesos, FX-19 y Avance de épicas siguen diciendo "validación Pendiente"); el commit 4 (enlace en el menú, DT-101) solo con su orden; la PR (la abre Pablo).
- **Siguiente paso:** decidir el estado de HU-27 y HU-34 y actualizar esos documentos.
- **Auditoría del PR #9 (HU-44), punto obligatorio:** el commit `906cc0d` hace que `users.0007` también **desactive** a los usuarios `cliente` que no son superusuarios. Hay que comprobar qué pasa con los usuarios creados con `createsuperuser` (rol por defecto `cliente`) y que ningún admin quede desactivado. Detalle en DT-105.

### 2026-11-01 · Pablo (con Claude Code) · `feat/URB-30-34-HU-27-HU-34-oportunidades`

- **Hecho:** DT-105 resuelto en código (FX-23). Las dos pruebas de oportunidades que usaban `role='cliente'` ahora comprueban el 401 de un visitante anónimo (`test_anonymous_cannot_open`, `test_anonymous_cannot_list`). C-08 confirmada por Pablo: solo hay roles `admin` y `asesor`, y el cliente es anónimo. Regla nueva en Estándares §4. Suite **125/125 OK**; `makemigrations --check` sin cambios.
- **Sin tocar (reportado):** `backend/apps/users/models.py:11-14` sigue con `cliente` en `ROLE_CHOICES` y como valor por defecto (lo quita HU-44, PR #9, con `users.0007`). `backend/apps/users/tests.py` sigue usando `client_user` (DT-107, carpeta de Sebas).
- **Falta:** comprobar DT-105 con HU-44 fusionada; DT-106 (el 403 de `IsInternalUser` sin prueba) y DT-107, ambos después del PR #9. DT-14 y DT-39 todavía citan C-08 como abierta.
- **Siguiente paso:** commit local sin push (orden de Pablo); luego seguir con V-26 a V-32.

### 2026-10-31 · Pablo (con Claude Code) · rama `docs/reglas-ia-y-deuda`
- **Hecho:** `AGENTS.md` en la raíz como única fuente de reglas para la IA (DS-25); `CLAUDE.md` y `.github/copilot-instructions.md` apuntan a él; ficha `docs/handoff/PLANTILLA_TAREA.md` y plantilla de PR; `backend/db.sqlite3` y `frontend/CLAUDE.md` ya no se versionan (DT-45 resuelto, FX-21); Guía, pasos 5 y 6; registrados DT-77, DT-78 y DT-79.
- **⚠️ Antes de hacer pull de develop con este cambio, copia tu `backend/db.sqlite3` fuera del repo; Git lo va a borrar de tu carpeta.**
- **Correcciones de auditoría (mismo día):** FX-22 (`db.sqlite3`, `9872e98`); DT-02, DT-65/SEC-09, DT-70, N-04 y Seguridad §5.3 alineados; DS-24 → DS-25; DT-79 = SEC-15; Estándares §4/§5, directiva GPS y contexto maestro §13.3 remiten a `AGENTS.md`; excepción de ramas `docs/…` en `AGENTS.md` §5.
- **Falta:** el PR a `develop` (lo abre Pablo), con la auditoría de solo lectura de `AGENTS.md` §11 antes; la rotación de credenciales de DT-79 (POR CONFIRMAR); DT-77 y DT-78 sin corregir.
- **Siguiente paso:** auditoría de solo lectura → PR de `docs/reglas-ia-y-deuda` → avisar a Sebas del respaldo de `db.sqlite3` antes de su pull.

---

## 🧾 Traza de la rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (PR #15)

> Para revisiones futuras: qué hizo la rama, dónde y con qué IDs. Comparada con `origin/develop` `5fb3910` (2026-11-04). Cabeza al redactarla: `105cfd6`, más el commit de correcciones de esta misma sesión. Si la rama recibe más commits, se agregan filas; no se reescriben estas.

**Historias:** HU-27 (URB-30, apertura manual, pantalla I-07) y HU-34 (URB-34, cartera con filtros, pantalla I-06), EP-5, adelantadas por DS-26. Estado: **Pruebas**, hasta el merge en `develop`.

**Commits** (de los más antiguos a los más recientes; 25 sobre `develop` antes de las correcciones):

| Capa | Commits |
|---|---|
| Modelo | `257ba1c` modelos `Contact`, `Opportunity` y `OpportunityStatusHistory`, más `opportunities.0001` (incluye la línea de `settings.py`) |
| API y pruebas | `4282a87` API de apertura y cartera (incluye la línea de `urls.py`) · `033b845` DT-105, fuera el rol `cliente` · `36d1cec` DT-106 (403 de `IsInternalUser`) · `1ee3c1b` DT-107 (`PropertyOwnershipTests` en `users/tests.py`, de Sebas, en commit propio) |
| Pantallas | `199294a` I-07 e I-06 |
| Merges de `develop` | `46033df` (PR #9 y #13) · `2fac92d` (`5fb3910`, PR #14 y #16) |
| Documentación | `9254a26`, `2982406`, `5a3f71f`, `cd5e7c1`, `04fc6c8`, `6264780`, `bc53be6`, `f2cb2fc`, `6d30093`, `0f7292b`, `ceb4a70`, `c3cf5ed`, `b59290d`, `ce90537`, `386fb45`, `105cfd6` y el commit de correcciones del 2026-11-04 (noche) |
| Otros | `a6cde69` `frontend/CLAUDE.md` (sigue ignorado, `.gitignore:34`; no queda en el diff neto) |

**Archivos** (28 en `git diff origin/develop...HEAD --name-only`):
- **Backend, app nueva** (de Pablo): `backend/apps/opportunities/` → `__init__.py`, `admin.py`, `apps.py`, `models.py`, `validators.py`, `services.py`, `serializers.py`, `views.py`, `urls.py`, `tests.py` (37 pruebas), `migrations/__init__.py` y `migrations/0001_initial.py` (depende de `users.0006`).
- **Compartidos:** `backend/config/settings.py` (+1 línea, `INSTALLED_APPS`) y `backend/config/urls.py` (+1 línea, `api/opportunities/`).
- **De Sebas:** `backend/apps/users/tests.py` (clase `PropertyOwnershipTests` al final y un comentario en `setUp`).
- **Frontend** (de Pablo): `frontend/types/opportunity.ts`, `frontend/lib/opportunities.ts`, `frontend/app/dashboard/opportunities/page.tsx` (I-06) y `frontend/app/dashboard/opportunities/new/page.tsx` (I-07).
- **Documentación:** `Project_Progress.md` y, en `docs/handoff/`: `URBANEX_AVANCE_EPICAS.md`, `URBANEX_DEUDA_TECNICA.md`, `URBANEX_ESTADO_PROCESOS.md`, `URBANEX_ESTANDARES_DOD.md`, `URBANEX_GPS_ARCHIVOS.md`, `URBANEX_GUIA_CONTINUIDAD.md`, `URBANEX_MASTER_CONTEXT.md` y `URBANEX_SEGURIDAD_Y_DEUDA.md`.

**Endpoints nuevos:** `GET` y `POST /api/opportunities/`, `GET /api/opportunities/eligible-properties/` y `GET /api/opportunities/agents/` (solo admin).

**IDs nuevos** (todos del rango de Pablo, `AGENTS.md` §4; sin repetidos en `develop` ni en las ramas remotas, comprobado el 2026-11-04):

| Tipo | IDs |
|---|---|
| FX | FX-19 (primer corte de EP-5) · FX-23 (DT-105) · FX-25 (DT-106 y DT-107) |
| DS | DS-26 (EP-5 antes de la tarea 4) · DS-27 (`apps.opportunities`, no `apps.crm`) · DS-28 (reglas del primer corte: celular de Ecuador, LOPDP, solo propiedades disponibles…) |
| DT abiertos | DT-100 (copia vieja del contexto maestro en la raíz) · DT-101 (sin enlace en el menú) · DT-102 ("sector" = `location`) · DT-103 (el filtro solo ofrece propiedades disponibles, Potencial) · DT-104 (sin auditoría RF-14) · DT-108 (propiedades indistinguibles) · DT-117 / SEC-16 (datos personales, LOPDP) · DT-118 (texto del catálogo vacío) |
| DT resueltos | DT-105 · DT-106 · DT-107 · DT-109 (BD local reiniciada) |
| SEC | SEC-16 (= DT-117) |
| V | V-26 a V-32 (Ronda 4): Aprobadas por Pablo el 2026-11-01 sin captura y repetidas con hora y captura el 2026-11-03, 22:50 a 23:49 |

**Filas existentes con notas añadidas** (sin borrar el texto original): DT-14, DT-31 y DT-39 (Deuda); C-08 (Estado de procesos); filas de `settings.py` y `urls.py` (GPS §3); cabeceras "Última actualización" de todos los documentos del handoff.

**Pruebas al cierre de la traza:** 155 OK (55 users, 19 documents, 44 appraisals y 37 opportunities), en SQLite. PostgreSQL: No ejecutado.

---

## 🧭 Pendiente ahora (2026-11-03)

> (corregido por Pablo, 2026-11-03: antes el título decía "2026-11-02"; los puntos de ese día se conservan.)

> - **HU-44, PR #9 existente:** merge con `origin/develop` guardado en `8ff1e9f`; el stash se aplicó sin conflictos. No abrir otra PR.
> - **Validación humana pendiente:** V-33..V-39 quedan en **Pendiente**; las observaciones reportadas previamente por Sebas se conservan, pero no sustituyen la evidencia requerida por `AGENTS.md` §9. V-40..V-42 también quedan **Pendiente**.
> - **Pruebas (2026-11-02):** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → **116 tests, OK** (55.180 s, exit 0), SQLite + `EMAIL_PROVIDER=console`. `makemigrations --check --dry-run` → exit 1; detecta `documents/0002_alter_document_file.py` (DT-92), no se generó ni aplicó migración. Suite local contra PostgreSQL **No ejecutado**. No ejecutar migraciones contra Supabase en esta tarea.
> - **Frontend (2026-11-02):** `npm run build` exit 0; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0 con 2 avisos preexistentes de `SiteNav` sin usar (`app/page.tsx` y `app/properties/page.tsx`).
> - **DT-96:** el restablecimiento de la base de desarrollo y la migración desde `develop` con Pablo son una **propuesta de Sebas, POR CONFIRMAR** por Pablo; no se ha ejecutado. Si se aprueba, documentarla con respaldo y confirmación de ambiente (corregido por Pablo, 2026-11-03).
> - ~~**(2026-11-01) 🧪 HU-12 (URB-17):** validaciones **V-60 a V-63**~~ **(2026-11-02) V-60 a V-62 aprobadas por Pablo; V-63 Pendiente (DT-110).** **(2026-11-03) Merge de `develop` (`40dd147`) y V-64 (escape de metaetiquetas) aprobada por Pablo.** **Siguiente:** auditoría de solo lectura (`AGENTS.md` §11), push y PR de `feat/URB-17-HU-12-compartir-ficha` (worktree `../Urbanex-hu12`).
> - **(2026-10-31) PR de `docs/reglas-ia-y-deuda` → `develop`** (lo abre Pablo): `AGENTS.md` como única fuente de reglas (DS-25), plantillas, `db.sqlite3` y `frontend/CLAUDE.md` fuera del repositorio (FX-22, FX-21), DT-77 a DT-79. **⚠️ Antes de hacer pull de develop con este cambio, copia tu `backend/db.sqlite3` fuera del repo; Git lo va a borrar de tu carpeta.**
> - **🧪 Ronda 4 (EP-5, primer corte):** validaciones **V-26 a V-32** ~~todas **Pendientes (Pablo)**. Rama `feat/URB-30-34-HU-27-HU-34-oportunidades`, **con push** (`origin/feat/URB-30-34-HU-27-HU-34-oportunidades`, 2026-10-30) y **sin PR todavía** (la abre Pablo).~~ **Aprobadas el 2026-11-01, sin captura;** ~~falta repetirlas con hora y captura (AGENTS §9).~~ **repetidas y Aprobadas con hora y captura el 2026-11-03 (corregido por Pablo, 2026-11-03).** La PR existe en borrador y la rama ya trae `develop`. El commit 4 (enlace en el menú, DT-101) espera la orden de Pablo (corregido por Pablo, 2026-11-03).
> - ~~**🧪 Ronda 3 (motor DS-21):** validaciones V-20 a V-25~~ **Hechas el 2026-10-29 y el 2026-10-30: las 6 aprobadas**. V-25 pasó tras la corrección FX-18. ~~**Siguiente:** la PR de `feat/URB-10-11-motor-avaluos` a `develop`.~~ **Fusionada (PR #7, `9801bc9`).**
> - **POR CONFIRMAR (Pablo / tutor):** si HU-04, HU-06 y HU-08 cuentan como completas (C-02 y θ v1 siguen provisionales). Pregunta para la empresa: N-05 (¿el avalúo aprobado actualiza el precio?), ampliada el 2026-10-30.
> - **DT-65:** falta la copia de Sebas.
> - Los pendientes anteriores ya resueltos están archivados en [Historial](#historial).

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
> **HU-44:** implementación registrada; la suite automatizada se ejecutó en SQLite (resultado vigente en "Estado actual"). La validación manual V-33..V-39 queda **Pendiente**. Se conservan como observaciones atribuidas a Sebas los reportes previos; V-37 fue parcial (motivo, baja y propiedad presente) y falta comprobar visualmente `agent: null`.

**Preparación (antes de empezar):**
1. Desde `backend/`, configura el entorno local de pruebas para SQLite y correo `console`, confirma el motor con `settings.DATABASES['default']['ENGINE']` y luego inicia `pipenv run python manage.py runserver`. No ejecutes `migrate` si el motor es PostgreSQL/Supabase.
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

1. Solo si estás trabajando en una base local de desarrollo y verificaste que el motor activo es SQLite: `pipenv run python manage.py migrate` aplica `appraisals.0002` y `0003` (θ v1). La BD local cambia: **no la incluyas en ningún commit** (DT-02). Nunca ejecutar contra Supabase.
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

### Ronda 4 — EP-5, primer corte: HU-27 (I-07) y HU-34 (I-06) (rama `feat/URB-30-34-HU-27-HU-34-oportunidades`)

> **(2026-11-03) Repetida con hora y captura** tras reiniciar la BD (DT-109): las 7 **Aprobadas por Pablo** (fila nueva en cada V; capturas en `OneDrive\Documentos\Urbanex\evidencias\HU-27_34\`, fuera del repo). Propiedades: A = [DEMO] Casa en Cumbayá y B = [DEMO] Local en La Mariscal, publicadas por Pablo antes de la ronda.
>
> **Estado (2026-11-01): las 7 pruebas Aprobadas por Pablo** en el navegador, sin capturas. Observaciones registradas como DT-108 (propiedades #1 y #2 indistinguibles) y DT-109 (BD local con datos basura). ~~Las 7 pruebas están Pendientes (Pablo).~~

**Preparación (desde `backend/`):**
1. `pipenv run python manage.py migrate`: aplica `opportunities.0001`. Tu `db.sqlite3` cambia: **no la incluyas en ningún commit** (DT-02).
2. Reinicia `runserver` y `npm run dev`. Inicia sesión como `asesor.demo`.
3. Las pantallas aún **no tienen enlace en el menú** (DT-101): entra escribiendo la URL `http://localhost:3000/dashboard/opportunities`.
4. Usa datos ficticios (los celulares de abajo). **Ojo:** las oportunidades y su historial **no se pueden borrar** (el historial es inmutable y la oportunidad está protegida); quedan en tu BD local.

### V-26 · HU-27 — Abrir una oportunidad manual (asesor)
1. En I-06 pulsa "+ Abrir oportunidad".
2. Nombre `Prueba Uno`, celular `0991112233`, sin correo; elige `#33 La Carolina` (o cualquier tarjeta disponible); marca la casilla de la política de privacidad.
3. "Abrir oportunidad" → confirma en el modal.

**Resultado esperado:** ¿el modal pide confirmar y avisa que la apertura no se puede eliminar? ¿Vuelve a I-06 con el aviso verde "Oportunidad #N abierta en Contacto inicial" y la fila resaltada, con el celular `+593991112233`, el estado **Contacto inicial**, el canal **Captación manual** y la fecha y hora de Ecuador?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01, 19:56 (hora de la fila creada) | Como `asesor.demo`: "Prueba Uno", `0991112233`, sin correo, propiedad #1 (Departamento Moderno en La Carolina). El modal avisa que la apertura no se puede eliminar. Aviso verde "Oportunidad #1 abierta en Contacto inicial". Fila: `+593991112233`, Contacto inicial, Captación manual, "1 nov 2026 7:56 p. m." | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 22:51 (captura); apertura 22:50 | Como `asesor.demo`, BD nueva: "PruebaUno", `0991112233`, sin correo, propiedad **[DEMO] Casa en Cumbayá** (A). El modal avisó que la apertura no se puede eliminar. Aviso verde "Oportunidad #1 abierta en Contacto inicial". Fila: `+593991112233`, Contacto inicial, Captación manual, "3 nov 2026, 10:50 p. m.". Captura: `OneDrive\Documentos\Urbanex\evidencias\HU-27_34\V26.png` (fuera del repo) | **Aprobado** (Pablo, dictado y bitácora del 2026-11-03) |

### V-27 · HU-27 — Celular inválido y política de privacidad
1. En I-07, con otra propiedad, escribe el fijo `022345678` → "Abrir oportunidad" → confirma.
2. Corrige el celular a `0994445566`, desmarca la casilla de privacidad y pulsa "Abrir oportunidad".

**Resultado esperado:** en el paso 1, ¿aparece bajo "Celular" el error "Ingrese un celular de Ecuador válido: 09XXXXXXXX o +5939XXXXXXXX."? En el paso 2, ¿aparece el error bajo la casilla **sin abrir el modal**? ¿En I-06 no aparece ninguna oportunidad nueva?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01 (hora no indicada) | Con el fijo `022345678` (propiedad #31 Casa de 4 pisos), bajo "Celular" salió el error de celular de Ecuador válido. Con `0994445566` y la privacidad desmarcada, el error salió bajo la casilla sin abrir el modal. No se creó ninguna fila | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 22:54 | Como `asesor.demo`, "PruebaDos", propiedad [DEMO] Local en La Mariscal (B). Con el fijo `022345678` y la privacidad marcada salió bajo "Celular": "Ingrese un celular de Ecuador válido: 09XXXXXXXX o +5939XXXXXXXX.". Con `0994445566` y la privacidad desmarcada salió bajo la casilla: "Confirme que el interesado aceptó la política de privacidad (LOPDP).", sin abrir el modal. No se creó ninguna fila. Capturas: `…\HU-27_34\V-27_1_celular_2_.png` y `…\HU-27_34\V-27_2_privacidad.png`. Extra (2026-11-03, 23:37, como `admin.demo`): el mismo error de privacidad con un asesor elegido, `…\HU-27_34\V32_privacidad.png` | **Aprobado** (Pablo, dictado y bitácora del 2026-11-03) |

### V-28 · HU-27 — Reutiliza el contacto existente
1. En I-07: nombre `Otro Nombre`, celular `+593 99 111 2233` (el de V-26 con otro formato), correo `otro@correo.ec`, **otra propiedad** (no la de V-26), privacidad marcada → confirma.

**Resultado esperado:** ¿aparece el modal "Se usó un contacto existente" con los datos guardados (`Prueba Uno`, `+593991112233`, sin correo)? Al pulsar "Ver oportunidades", ¿la fila nueva muestra **Prueba Uno**, no "Otro Nombre"?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01 (hora no indicada) | "Otro Nombre", `+593 99 111 2233`, `otro@correo.ec`, propiedad #2. Modal "Se usó un contacto existente" con Prueba Uno, `+593991112233`, sin correo. La oportunidad #2 quedó con el contacto Prueba Uno. Pablo lo comprobó también en la BD: la #1 tiene `property_id` 1 y la #2, `property_id` 2 | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 23:02 (captura); apertura 23:01 | "Otro Nombre", `0991112233`, `otro@correo.ec`, propiedad B (Local en La Mariscal). Tras confirmar, aviso naranja "Se usó un contacto existente" (según el dictado de Pablo; no está en la captura): datos guardados PruebaUno `+593991112233`, sin cambios. En "Ver oportunidades", la #2 (Local en La Mariscal, 3 nov 2026, 11:01 p. m.) quedó con el contacto **PruebaUno**, no "Otro Nombre". Captura: `…\HU-27_34\V-28_contacto_existente.png` | **Aprobado** (Pablo, dictado y bitácora del 2026-11-03) |

### V-29 · RF-05 — Una sola oportunidad activa por contacto e inmueble
1. En I-07 repite el celular `0991112233` con **la misma propiedad de V-26** → confirma.

**Resultado esperado:** ¿aparece el aviso ámbar "El contacto ya tiene una oportunidad activa sobre este inmueble. (oportunidad #N)" con el número de V-26? ¿"Ver oportunidades" abre I-06 filtrada por esa propiedad? ¿No se creó otra fila?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01 (hora no indicada) | `0991112233` con la propiedad #1: aviso "El contacto ya tiene una oportunidad activa sobre este inmueble (oportunidad #1)". "Ver oportunidades" abrió I-06 filtrada por esa propiedad. No se creó otra fila | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 23:06 | "PRUEBA TRES", `0991112233`, propiedad A (Casa en Cumbayá). Aviso ámbar "El contacto ya tiene una oportunidad activa sobre este inmueble. (oportunidad #1)" (según el dictado de Pablo). "Ver oportunidades" abrió I-06 con la propiedad A ya en el filtro: 1 oportunidad (#1 PruebaUno, 10:50 p. m.), sin duplicado. Captura: `…\HU-27_34\V-29_oportunidad_activa_duplicada.png` | **Aprobado** (Pablo, dictado y bitácora del 2026-11-03) |

### V-30 · HU-34 — Los filtros se combinan
1. En I-06 elige la propiedad de V-26 y el estado "Contacto inicial" → "Filtrar".
2. "Abierta desde" y "Abierta hasta" = **hoy** → "Filtrar". Luego "Abierta desde" = **mañana** → "Filtrar".
3. "Abierta desde" = mañana y "Abierta hasta" = hoy → "Filtrar". Al final, "Limpiar".

**Resultado esperado:** ¿en el paso 1 solo quedan las filas de esa propiedad? En el paso 2, ¿con hoy aparecen y con mañana sale "No hay oportunidades con estos filtros."? En el paso 3, ¿aparece bajo "Abierta hasta" el error "La fecha final no puede ser anterior a la inicial."? ¿"Limpiar" vuelve a la lista completa?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01 (hora no indicada) | Propiedad #1 + Contacto inicial + desde 01/11: solo la #1. Desde 02/11: "No hay oportunidades con estos filtros." (el enlace para abrir una oportunidad funciona). Desde 02/11 hasta 01/11: error "La fecha final no puede ser anterior a la inicial." "Limpiar" restaura la lista | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 23:13 a 23:49 | Como `asesor.demo`: propiedad A + Contacto inicial → solo las filas de A. Con 03/11 a 03/11 aparecen (a las 23:45: PRUEBA TRES 11:15 p. m. y PruebaUno 10:50 p. m.). Con 04/11 a 05/11: "No hay oportunidades con estos filtros." y el enlace "Abrir una oportunidad". Con 04/11 a 03/11: bajo "Abierta hasta", "La fecha final no puede ser anterior a la inicial." y el aviso "Revisa los filtros marcados.". "Limpiar" vuelve a las 3 oportunidades. Capturas: `…\HU-27_34\V32_Filtro.png` (23:46, fechas cruzadas; Pablo la nombró V32, pero es de V-30), `…\HU-27_34\V32_Filtro2.png` (23:49, después de Limpiar) y `…\HU-27_34\V-30_filtros.png` (23:13) | **Aprobado** (Pablo, dictado del 2026-11-03) |

### V-31 · HU-34 / DS-28 — El asesor ve su cartera y el admin ve todas
1. Cierra sesión e inicia como `admin.demo`. Abre `/dashboard/opportunities`.
2. "+ Abrir oportunidad": llena los datos con el celular `0997778899`, sin elegir asesor → "Abrir oportunidad". Después elige `asesor.demo` como responsable → confirma.
3. Vuelve a entrar como `asesor.demo` y abre `/dashboard/opportunities`.

**Resultado esperado:** como admin, ¿el título dice "Oportunidades del equipo", hay una columna "Asesor" y un filtro "Asesor"? En el paso 2, ¿sin asesor sale el error "Elija el asesor responsable." y, con él, la oportunidad se abre a cargo de `asesor.demo`? En el paso 3, ¿el título dice "Mi cartera de oportunidades", sin columna ni filtro de asesor, y la oportunidad del paso 2 aparece en su lista?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01, 21:14 (hora de la fila creada) | Como `admin.demo`: título "Oportunidades del equipo", filtro y columna "Asesor". Sin asesor: "Elija el asesor responsable.". Con `asesor.demo` se abrió la #3 (Prueba 3, `0997778899`, propiedad #31, 9:14 p. m.). Como `asesor.demo`: "Mi cartera de oportunidades", sin columna ni filtro de asesor, y la #3 aparece | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 23:15 (apertura) a 23:37 | Como `admin.demo`: "Oportunidades del equipo", filtro de 5 campos (con "Asesor") y columna "Asesor". "PRUEBA TRES", `0997778899`, propiedad A, sin asesor → bajo el campo "Elija el asesor responsable." (según el dictado de Pablo; en `V32_Asesor.png` se ve el selector vacío, pero el error no). Con `asesor.demo` elegido se abrió la #3 (11:15 p. m.). Como `asesor.demo`: "Mi cartera de oportunidades", filtro de 4 campos sin asesor, y la #3 PRUEBA TRES arriba de las otras dos. Capturas: `…\HU-27_34\V-31_roles_admin_asesor.png` (23:17, vista del asesor) y `…\HU-27_34\V32_Asesor.png` (23:37, formulario del admin) | **Aprobado** (Pablo, dictado y bitácora del 2026-11-03) |

### V-32 · DS-28 — El selector de I-07 solo muestra datos públicos
1. En I-07 (como `asesor.demo`), revisa las tarjetas de "Propiedad de interés".

**Resultado esperado:** ¿cada tarjeta muestra solo la foto (o "Sin foto"), el título, el sector, el tipo y el precio, **sin** el nombre del asesor ni datos internos? ¿Solo aparecen propiedades **disponibles** (una en captación, por ejemplo una nueva que registres, no sale)?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador, sin captura) | 2026-11-01 (hora no indicada) | Las tarjetas muestran solo foto, título, sector, tipo y precio, sin asesor. Son 8 tarjetas (las 8 disponibles de la BD local) y ninguna `[DEMO]` (las #32 a #35 están en captación). Observación: la #1 y la #2 no se distinguen (DT-108) | **Aprobado** |
| Pablo (navegador, con captura; repetición tras DT-109) | 2026-11-03, 22:54 (asesor) y 23:37 (admin) | Pablo confirma (dictado del 2026-11-03, ~23:50): el selector de I-07 muestra **solo las 2 propiedades disponibles**, A (Casa en Cumbayá, Casa, $285.000,00) y B (Local en La Mariscal, Local Comercial, $120.000,00). Cada tarjeta tiene foto, título, sector, tipo y precio, **sin el asesor**. Las dos [DEMO] en captación (Departamento en La Carolina y Terreno en Tumbaco) no aparecen. Capturas: `…\HU-27_34\V-27_2_privacidad.png` (como asesor) y `…\HU-27_34\V32_privacidad.png` (como admin) | **Aprobado** (Pablo, dictado del 2026-11-03) |

### Ronda HU-12 — Compartir la ficha (rama `feat/URB-17-HU-12-compartir-ficha`; validada en local el 2026-11-02: V-60 a V-62 aprobadas, V-63 Pendiente por DT-110; 2026-11-03: V-64, escape de metaetiquetas, aprobada)

> **Preparación.** Esta ronda usa tu backend de siempre (`http://127.0.0.1:8000`, en tu carpeta) y el frontend del worktree:
> 1. Arranca el backend como siempre, desde tu carpeta principal.
> 2. En otra terminal: `cd ..\Urbanex-hu12\frontend` y `npm run dev -- -p 3001` (el puerto 3001 evita chocar con tu frontend).
> 3. Usa una **ventana de incógnito sin sesión**: así ves la ficha como un cliente.
>
> Para ver las etiquetas: abre la ficha y pulsa **Ctrl+U** (código fuente); luego **Ctrl+F** y busca `og:`. Las pruebas automáticas ya cubren la ficha Reservada y la ficha sin fotos; si tienes una a mano, puedes comprobarla también en V-60.

### V-60 · HU-12 — La ficha publicada tiene sus metaetiquetas
1. Abre `http://localhost:3001/properties/33` (La Carolina, Disponible, con foto). Si no está disponible, usa cualquier ficha que salga en `/properties`.
2. Mira el título de la pestaña y luego el código fuente (Ctrl+U).

**Resultado esperado:** ¿la pestaña dice **"<título de la propiedad> | Urbanex"**? ¿En el código fuente aparecen `og:title`, `og:description` (tipo, ubicación, precio y "(precio referencial)"), `og:image` con la URL de la foto principal, `og:url` con `http://localhost:3000/properties/33` (dice 3000 aunque abras en 3001: sale del valor por defecto de `NEXT_PUBLIC_SITE_URL`), y `twitter:card` con `summary_large_image`? ¿Hay `<link rel="canonical">`?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (incógnito, `localhost:3001`) | 2026-11-02 (hora no anotada; sin captura) | Usó `/properties/1` en lugar de `#33`. Vio `og:title`, `og:description`, `og:image`, `og:image:alt`, `og:type`, `og:locale`, `twitter:card` = `summary_large_image`, `twitter:title`, `twitter:description` y `twitter:image`. No se anotó si vio `og:url`, `og:site_name` ni la canónica | Reemplazada por la repetición con captura (ver fila siguiente) |
| Pablo (incógnito, `localhost:3001`), repetición con captura | 2026-11-02, 22:12 | Código fuente de `/properties/1`, búsqueda `og:` → "1 de 16": `<title>` "Departamento Moderno en La Carolina \| Urbanex", descripción, canónica, `og:title`, `og:description`, `og:url`, `og:site_name`, `og:locale` (`es_EC`), `og:image`, `og:image:alt`, `og:type` (`website`), `twitter:card` = `summary_large_image`, `twitter:title`, `twitter:description` y `twitter:image`. **Observaciones:** (1) la #1 tiene `property_type` = `"no_disponible"`, por eso la ficha y la descripción dicen "no_disponible". Es un dato basura local (DT-109, registrada en la rama de oportunidades, sin fusionar): el modelo sí limita los valores (`choices` en `backend/apps/users/models.py:21,26`) y DRF los valida, así que el valor no entró por la API normal (origen No verificado); revisarlo en HU-05. (2) Su foto principal es `/media/properties/images/Error.png`, también un dato local. (3) `og:url` y la canónica apuntan a `localhost:3000` por el valor por defecto de `NEXT_PUBLIC_SITE_URL` (esperado en local). Captura: `C:\Users\Pablo\OneDrive\Documentos\Urbanex\evidencias\HU-12\Pruebas anteriores (cambiar)\OG_1_HU12_New.png` (ruta actualizada el 2026-11-03: la captura está en esa subcarpeta) | **Aprobado** |

### V-61 · HU-12 — Una ficha que no es pública no muestra datos
1. Sin sesión, abre `http://localhost:3001/properties/35` (Tumbaco, en captación). Si ya no está en captación, usa cualquier propiedad en captación o no disponible del dashboard.
2. Abre también `http://localhost:3001/properties/99999` (no existe).
3. En cada una, mira la pestaña y el código fuente (Ctrl+U).

**Resultado esperado:** ¿las dos dicen **"Propiedad no disponible | Urbanex"** en la pestaña, con `<meta name="robots" content="noindex, nofollow">`? ¿**No** hay ninguna etiqueta `og:` ni `twitter:`, ni el título, la ubicación o el precio de la propiedad? ¿La página muestra "No se pudo cargar esta propiedad"?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (incógnito, `localhost:3001`) | 2026-11-02 (hora no anotada; sin captura) | `/properties/99999` (no existe) y `/properties/7` (en captación): solo `noindex`, sin etiquetas `og:` ni `twitter:`. **Observación:** en `/properties/99999` la pantalla dice "No se pudo cargar esta propiedad. Verifica la conexión con el servidor", lo que confunde cuando la propiedad no existe → **DT-112**. La navbar duplicada ya es DT-25 | Reemplazada por la repetición con captura (ver fila siguiente) |
| Pablo (incógnito, `localhost:3001`), repetición con captura | 2026-11-02: `/properties/99999` a las 21:31 y 21:34 y `/properties/7` a las 21:32 (horas del log del backend: `404` en ambas); capturas a las 21:51 y 21:54 | En las dos: `<title>` "Propiedad no disponible \| Urbanex", `<meta name="robots" content="noindex, nofollow">` y búsqueda `og:` → "Sin coincidencias". Capturas en `C:\Users\Pablo\OneDrive\Documentos\Urbanex\evidencias\HU-12\Pruebas anteriores (cambiar)\` (ruta actualizada el 2026-11-03): `noindex_99999_hu12.png` y `og_99999_hu12.png` (21:51); `noindex_7_hu12.png` y `og_7_hu12_.png` (21:54) | **Aprobado** |

### V-62 · HU-12 — La ficha se ve igual y consulta la API una sola vez
1. Abre `http://localhost:3001/properties/33` y recarga la página una vez.
2. Mira la terminal del backend (`runserver`).

**Resultado esperado:** ¿la ficha se ve igual que antes (foto, precio, características, descripción)? ¿Cada recarga produce **una sola** línea `GET /api/auth/properties/33/` en el backend, y no dos? (El modo de desarrollo puede repetir la petición la primera vez que compila la página; cuenta la de la recarga.)

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (incógnito, `localhost:3001`) | 2026-11-02 (hora no anotada; sin captura) | La ficha se ve igual que antes; cada recarga hace un solo `GET` en el backend | Reemplazada por la repetición con captura (ver fila siguiente) |
| Pablo (incógnito, `localhost:3001`), repetición con captura | 2026-11-02, 21:35 (captura a las 21:54) | La ficha `/properties/1` se ve normal; el log del backend muestra un solo `GET /api/auth/properties/1/` por recarga (21:35:02, 21:35:35, 21:50:41 y 21:54:05, todos `200`). En la captura también se ve la navbar duplicada (DT-25). Captura: `C:\Users\Pablo\OneDrive\Documentos\Urbanex\evidencias\HU-12\Pruebas anteriores (cambiar)\Get_1_HU12.png` (ruta actualizada el 2026-11-03) | **Aprobado** |

### V-63 · HU-12 / DT-110 — La previsualización real en una red (Pendiente hasta tener una URL pública)
1. Con la aplicación desplegada en una URL pública y `NEXT_PUBLIC_SITE_URL` con ese dominio, pega el enlace de una ficha Disponible en un chat de WhatsApp (o en el depurador de enlaces de Facebook).

**Resultado esperado:** ¿la tarjeta muestra el título, el resumen con el precio referencial y la foto principal? **No se puede hacer en local** (DT-110): WhatsApp no llega a `localhost` ni a las fotos de `127.0.0.1:8000`. Queda Pendiente hasta el despliegue (DS-20).

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| — | — | No se puede hacer en local (DT-110); confirmado por Pablo el 2026-11-02 | Pendiente |

### V-64 · HU-12 / Seguridad §3.1 — Un título malicioso sale escapado en las metaetiquetas
> **Preparación (2026-11-03, Claude Code, solo SQLite local):** worktree `../Urbanex-hu12` en `40dd147` (merge de `develop`), BD recién creada con `migrate` + `setup_demo_data`, `next build` + `next start` en `localhost:3000` y `runserver` en `127.0.0.1:8000`. El título de la #1 ("[DEMO] Casa en Cumbayá - lista para publicar") se cambió con `manage.py shell` y se restauró al terminar.

1. Como `asesor.demo`, publica la #1, que tiene el título `XSS-HU12 </title><script>alert('titulo')</script> "><img src=x onerror=alert('atributo')> & 'fin'`.
2. Sin sesión (incógnito), abre `http://localhost:3000/properties/1`.
3. Abre el código fuente (Ctrl+U) y busca `XSS-HU12`.
4. En PowerShell: `curl.exe -s -A "facebookexternalhit/1.1" http://localhost:3000/properties/1 | Select-String -Pattern 'og:title' -AllMatches`.

**Resultado esperado:** ¿no aparece ninguna alerta? ¿El título se ve como texto literal en el dashboard, en la pestaña y en la ficha? ¿En el código fuente `<title>`, `og:title`, `og:image:alt` y `twitter:title` tienen `&lt;`, `&gt;`, `&quot;` y `&amp;`, sin `<script>` ni `<img src=x` literales? ¿Hay **un solo** `og:title` y su `content="…"` se cierra al final del título?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (incógnito, `localhost:3000`), guiado por Gemini | 2026-11-03: pasos 1 y 2 a las 13:33 y 13:37; pasos 3 y 4 a las 13:50–13:53 (hora del reloj de las capturas) (corregido por Pablo, 2026-11-03: hora aproximada, vale la de las capturas) | Paso 1: dashboard con la #1 Disponible y el título como texto plano, sin alerta (`Prueba 1.2.png`, 13:33); catálogo con sesión (`Prueba 1.png`, 13:33). Paso 2: ficha `/properties/1` con el título literal en la pestaña y en el encabezado, sin alerta (`Captura de pantalla (11).png`, 13:37); catálogo sin sesión (`Captura de pantalla (12).png`, 13:37). Paso 3: código fuente de `/properties/1`, búsqueda `XSS-HU12` → 12 coincidencias, título escapado (`&lt;/title&gt;&lt;script&gt;…`) en `<title>`, `og:title`, `og:image:alt`, `twitter:title`, `alt` de la imagen y `<h1>`, sin `<script>` literal (`Captura de pantalla (14).png`, 13:50, y `(15)`, 13:51). Paso 4: `curl` como `facebookexternalhit/1.1` → una sola etiqueta `og:title`, con el `content` escapado y cerrado al final (`Captura de pantalla (16).png`, 13:53). **Observación:** el primer intento del paso 3 se hizo sobre `/properties` (catálogo) y no sobre la ficha (`Captura de pantalla (13).png`, 13:38); se repitió sobre `/properties/1`. Capturas en `C:\Users\Pablo\OneDrive\Documentos\Urbanex\evidencias\HU-12\`, revisadas por Claude Code | **Aprobado** (Pablo, 2026-11-03) |

> **Comprobación técnica complementaria (Claude Code, 2026-11-03 13:45:08; no sustituye la validación de Pablo):** `Invoke-WebRequest` a `/properties/1` con agente de navegador y con `facebookexternalhit/1.1`. En los dos: `<script>alert` literal = 0, `<img src=x` literal = 0, `og:title` = 1 (dentro de `<head>`). `<title>`, `og:title`, `og:image:alt` y `twitter:title` salen como `XSS-HU12 &lt;/title&gt;&lt;script&gt;alert(&#x27;titulo&#x27;)&lt;/script&gt; &quot;&gt;&lt;img src=x onerror=alert(&#x27;atributo&#x27;)&gt; &amp; &#x27;fin&#x27;`, y en `self.__next_f` como `\u003c/title\u003e\u003cscript\u003e…`.

---

### Ronda 5 — HU-44 · Invitaciones y administración de usuarios

> **Antes de repetir la ronda:** usa `EMAIL_PROVIDER=console` con SQLite local. Los enlaces aparecen en la consola del backend; no uses Resend ni Supabase para estas pruebas. La ejecución manual reportada por Sebas el 2026-10-30 fue en Supabase PostgreSQL; no se verificó en esta sesión. La suite automatizada registrada se ejecutó con SQLite.
>
> **Capturas:** no se encontraron imágenes de esta ronda en el repositorio. Las rutas indicadas son destinos para guardar las capturas al repetir la prueba, no archivos ya existentes.

### V-33 · HU-44 — Crear usuario y localizar el enlace de activación
1. Inicia sesión como administrador y abre `/dashboard/users`.
2. Crea un asesor con un correo nuevo de prueba.
3. Busca en la consola el correo de activación y el enlace `/activate#...`.

**Resultado esperado:** A-01 confirma la creación y la cuenta queda pendiente/inactiva; el enlace aparece en consola sin contraseña temporal ni correo externo.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-30 17:41:23 | `POST /api/auth/users/` respondió 201; el correo "Activa tu cuenta de Urbanex" y el enlace local aparecieron en la consola con proveedor `console` | No aportada; destino: `evidence/HU-44/V-33.png` | **Pendiente** |

### V-34 · HU-44 — Activar la cuenta e iniciar sesión
1. Desde el enlace de V-33, establece una contraseña válida.
2. Inicia sesión con el correo y la contraseña recién establecida.
3. Comprueba en A-01 que la cuenta figura activa.

**Resultado esperado:** la activación concluye, el usuario inicia sesión y A-01 refleja su estado activo.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-30 17:41:55; 17:43:14 | `POST /api/auth/users/activate/` respondió 200 y después `POST /api/auth/login/` respondió 200 | No aportada; destino: `evidence/HU-44/V-34.png` | **Pendiente** |

### V-35 · HU-44 — Rechazar un enlace de activación usado
1. Activa una cuenta desde su invitación.
2. Abre de nuevo el mismo enlace e intenta enviar otra vez la contraseña.

**Resultado esperado:** el segundo uso se rechaza como inválido o vencido y no cambia la contraseña ya establecida. La expiración de 24 horas se cubre en pruebas automatizadas.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-30; hora no registrada | Sebas informó que, después de activar la cuenta, el enlace usado fue rechazado al volver a abrirlo; no se aportó el detalle visual ni una hora verificable | No aportada; destino: `evidence/HU-44/V-35.png` | **Pendiente** |

### V-36 · HU-44 — Reenviar una invitación
1. Crea un asesor de prueba y conserva el enlace original de la consola.
2. Desde A-01, reenvía la invitación y copia el enlace nuevo.
3. Abre primero el enlace antiguo y confirma que se rechaza.
4. Abre después el enlace nuevo, establece la contraseña y confirma la activación.

**Resultado esperado:** el enlace antiguo no sirve; el nuevo permite activar la cuenta.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-31, 01:31 (hora del reporte) | Confirma que probó el enlace antiguo y fue rechazado, y que el enlace nuevo permitió activar la cuenta | Sin captura adjunta | **Pendiente** |

### V-37 · HU-44 — Desactivar un asesor, ver el motivo y liberar sus propiedades (**Verificación manual parcial; comportamiento cubierto por prueba automática**)
1. Con datos locales de prueba, crea y activa un asesor con una propiedad asignada.
2. Como administrador, desactívalo indicando un motivo.
3. En A-01, vuelve a abrir el usuario y verifica que el motivo se muestra.
4. Comprueba que la propiedad sigue existiendo y su responsable queda vacío (`agent: null`). La tabla del frontend no muestra a qué asesor está asociada. Sebas no necesita usar herramientas técnicas para esta comprobación: la prueba automática `test_deactivation_keeps_user_and_unassigns_properties` verifica que la propiedad queda sin asesor; si se exige evidencia manual adicional, debe revisarla alguien con acceso a una vista técnica adecuada.
5. Intenta iniciar sesión con el asesor y confirma que se rechaza.

**Resultado esperado:** se ve el motivo; la propiedad persiste sin responsable; el asesor inactivo no inicia sesión.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-31 01:26–01:27 | `POST /api/auth/users/2/deactivate/` respondió 200; confirmó que el asesor quedó inactivo y no pudo iniciar sesión, que A-01 muestra el motivo y que la propiedad sigue apareciendo. No pudo confirmar desde la interfaz si `agent: null`; la prueba automática `test_deactivation_keeps_user_and_unassigns_properties` sí verifica que el asesor queda desasignado en la base de pruebas | Sin captura | **Pendiente; observación manual parcial** |

### V-38 · HU-44 — Bloquear A-01 incluso mediante URL directa
1. Inicia sesión con un asesor.
2. Escribe directamente `/dashboard/users` en la barra del navegador.
3. Confirma que la página no permite ver ni gestionar usuarios.
4. Comprueba que `GET /api/auth/users/` responde 403.

**Resultado esperado:** el asesor no accede a A-01 por navegación ni URL directa; la API responde 403.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-31, 01:31 (hora del reporte) | Confirma que abrió directamente `/dashboard/users` con rol asesor y que el acceso quedó bloqueado; confirma también la respuesta 403 de la API | Sin captura adjunta | **Pendiente** |

### V-39 · A-01 — Rechazar celulares inválidos
1. En `/dashboard/users`, edita un usuario de prueba y confirma un celular válido de 10 dígitos que empiece con `09`.
2. Prueba un número de 10 dígitos que no empiece con `09`.
3. Prueba una entrada con letras y otra con prefijo `+593`.
4. Guarda cada valor inválido y comprueba el mensaje de validación.

**Resultado esperado:** el número válido se acepta; el que no empieza en `09`, el que contiene letras y el internacional `+593` se rechazan con un mensaje claro.

| Quién | Fecha y hora | Qué se observó exactamente | Captura | Resultado |
|---|---|---|---|---|
| Sebas | 2026-10-31, 01:31 (hora del reporte) | Confirma que el celular válido se aceptó y que se rechazaron los tres casos inválidos: sin prefijo `09`, con letras y con `+593` | Sin captura adjunta | **Pendiente** |

### V-40 · HU-44 — Acceso a A-01 desde el dashboard
1. Inicia sesión con un administrador y abre el dashboard.
2. Comprueba que el botón **Administrar usuarios** aparece y abre `/dashboard/users`.
3. Inicia sesión con un asesor y comprueba que el botón no aparece.

**Resultado esperado:** solo el administrador ve el acceso a A-01 y llega a la pantalla de gestión.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|

**Estado: Pendiente.**

### V-41 · HU-44 — Cierre de sesión desde la navegación global
1. Inicia sesión y abre A-01.
2. Usa la acción de cierre de sesión de `SiteNav`.
3. Comprueba que se cierra la sesión y que una ruta protegida ya no muestra información de usuarios.

**Resultado esperado:** la navegación global cierra la sesión de forma consistente y la ruta protegida requiere volver a iniciar sesión.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|

**Estado: Pendiente.**

### V-42 · HU-44 — Mensaje de sesión vencida en pantallas autenticadas
1. En un entorno de prueba, invalida o deja vencer el token de sesión.
2. Abre una pantalla autenticada que use `authFetch` (I-06, I-07, I-11 o I-12).
3. Registra el mensaje que aparece y si la persona puede volver a iniciar sesión.

**Resultado esperado:** la persona recibe un mensaje comprensible y un camino claro para recuperar la sesión; registra cualquier confusión entre un token vencido y otros errores 401 (DT-97).

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|

**Estado: Pendiente.**

---

### V-43 · HU-45 — Un administrador desbloquea una cuenta bloqueada
1. Inicia sesión con una cuenta de administrador y abre A-01 (`/dashboard/users`).
2. En un usuario de prueba activo, provoca el bloqueo con cinco intentos de inicio de sesión incorrectos.
3. Comprueba que A-01 muestra el estado bloqueado y los intentos fallidos.
4. Pulsa **Desbloquear** y comprueba que desaparece el estado bloqueado y la acción.
5. Inicia sesión con la contraseña correcta de la cuenta de prueba.

**Resultado esperado:** solo el administrador puede desbloquear desde A-01; el desbloqueo reinicia el contador a 0 y permite el acceso. El texto del login no distingue una cuenta bloqueada de credenciales incorrectas.

**Comprobaciones adicionales de interfaz (2026-11-04):** al fallar el login, la contraseña debe borrarse y el correo conservarse. El mensaje debe ser breve y neutral, sin explicar la regla de bloqueo ni confirmar el estado de una cuenta. Probar que el mensaje se mantiene igual para una contraseña incorrecta y para una cuenta bloqueada.

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Sebas | 2026-11-04, 18:59 | Probé el inicio de sesión con contraseña incorrecta y con la cuenta bloqueada: apareció el mismo mensaje, se borró la contraseña y el correo permaneció. Desbloqueé la cuenta en `/dashboard/users` y pude iniciar sesión con la contraseña correcta. | [Captura V-43](evidence/HU-45/V-43.png) — Aprobado |

| Sebas | 2026-11-06, 14:03 | Inicié sesión como Asesor, abrí `/dashboard/users` y comprobé que no pude acceder a la gestión de usuarios ni al desbloqueo. | `evidence/HU-45/V-43-no-admin.png` — Aprobado |
### Evidencia técnica HU-45 (2026-11-03)

- **Suite backend (desde `backend/`):** `pipenv run python -c "import os, sys; os.environ['DB_ENGINE']='sqlite'; os.environ['EMAIL_PROVIDER']='console'; import config.settings as settings; print('Engine aislado:', settings.DATABASES['default']['ENGINE']); print('Correo:', os.environ['EMAIL_PROVIDER']); settings.DATABASES['default']['NAME']=':memory:'; sys.modules['urbanex_test_settings']=settings; from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py','test','--settings=urbanex_test_settings','apps.users.tests','apps.documents.tests','apps.appraisals.tests'])"` → `Engine aislado: django.db.backends.sqlite3`; `Correo: console`; `Found 120 test(s)`; `Ran 120 tests in 58.160s`; `OK`; exit 0. El registro de rechazo de Resend corresponde a `test_resend_failure_returns_gateway_error_and_rolls_back_user_creation`, que simula el error con `mock.patch`; no hubo envío externo confirmado.
- **Migraciones (desde `backend/`):** `pipenv run python -c "import os, sys; os.environ['DB_ENGINE']='sqlite'; import config.settings as settings; settings.DATABASES['default']['NAME']=':memory:'; sys.modules['urbanex_test_settings']=settings; from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py','makemigrations','--check','--dry-run','--settings=urbanex_test_settings'])"` → detecta `apps\documents\migrations\0002_alter_document_file.py`; exit 1. No genera ni aplica migraciones.
- **Frontend (desde `frontend/`):** `npm run build` → exit 0; `npx tsc --noEmit -p .` → exit 0; `npx eslint .` → exit 0, 2 avisos preexistentes en `app/page.tsx` y `app/properties/page.tsx` por `SiteNav` sin usar.

### Ronda 6 — Lote 2: HU-22 (I-09), HU-18 (P-07), HU-24 (I-08) y barra por rol (rama `feat/URB-19-18-27-HU-22-HU-18-HU-24-visitas`, PR #19)

> **Estado (2026-11-08): las 13 pruebas Aprobadas por Pablo** (2026-11-07, 20:55, a 2026-11-08, 00:28). Entorno: worktree `Urbanex-lote2`, `backend/db.sqlite3` local migrada (`visits.0001` y `visits.0002`), `EMAIL_PROVIDER=console`; nunca contra Supabase. Usuarios: `asesor.demo` (A), `asesor.b@urbanex.test` (B, creado y activado en la ronda) y `admin.demo`. Guía de pasos fuera del repo: `Urbanex-lote2-validacion\GUIA_VALIDACION_LOTE2.md`. Observaciones registradas como DT-144 a DT-147. Capturas: ver la nota de cierre del 2026-11-08.

**Preparación de V-77 (2026-11-07, ~21:40–21:49):** el admin creó al asesor B en A-01 (estado "Pendiente de activación"); la terminal del backend imprimió el correo "Activa tu cuenta de Urbanex" con el enlace `/activate/#<token>` (POST de creación → 201). La página de activación rechazó una contraseña de menos de 8 caracteres y otra demasiado común, y con una válida mostró "Cuenta activada, ya puedes iniciar sesión". B entra con los 5 enlaces de asesor, sin administración de usuarios, y todo vacío.

### V-65 · SiteNav — Barra sin sesión

**Resultado esperado:** ¿Sin sesión, la barra muestra solo "Propiedades" y "Panel del agente"?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, 20:55–21:04 | Incógnito, `/properties`: solo "Propiedades" y "Panel del agente", con la marca Urbanex al otro extremo; catálogo con las 2 propiedades Disponibles de demo (Casa en Cumbayá, Local en La Mariscal). capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-66 · SiteNav — Barra del asesor y ventana angosta

**Resultado esperado:** ¿El asesor ve Propiedades · Panel del agente · Oportunidades · Disponibilidad · Agenda, con una sola pestaña resaltada, y en ventana angosta la fila se desplaza de lado sin romperse?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~21:05–21:16 | Como `asesor.demo`: los 5 enlaces, el nombre y "Cerrar sesión"; en cada enlace solo esa pestaña resaltada (recuadro celeste y subrayado azul). Oportunidades con la cartera y "Abrir oportunidad"; Disponibilidad (I-09) con franjas de lunes a domingo y Excepciones; Agenda (I-08) con la semana del 2 al 8-nov y el sábado 7 como "Hoy". Vista de teléfono (Opera GX, DevTools): la fila de enlaces se desplaza de lado con barra horizontal sin romperse; catálogo, Oportunidades, Disponibilidad y Agenda responsive. Observaciones: el formulario de login sigue visible ~0,5 s tras iniciar sesión (DT-144); en el Panel angosto las acciones requieren desplazamiento horizontal (DT-145, pantalla fuera del lote). capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-67 · SiteNav — Barra del admin

**Resultado esperado:** ¿El admin ve los mismos 5 enlaces, sin "Usuarios" en la barra, y el botón de Usuarios sigue en el Panel?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~21:20–21:40 | Como `admin.demo`: los 5 enlaces; "Usuarios" no está en la barra; en el Panel, "Administrar usuarios" junto a "Registrar propiedad". Disponibilidad y Agenda piden elegir asesor. A-01 lista `admin.demo` y `asesor.demo` activas con Editar y Desactivar. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-68 · HU-22 — Agregar una franja (I-09)

**Resultado esperado:** ¿Lunes 09:00–12:00 con la duración por defecto aparece en "Lunes" con "visitas de 60 min" y el aviso "Franja agregada"?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~21:52–21:54 | Como asesor A: aviso verde "Franja agregada"; la franja "09:00–12:00 · visitas de 60 min" en la fila Lunes, con Editar y Eliminar. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-69 · HU-22 — Errores, edición y eliminación (I-09)

**Resultado esperado:** ¿09:00–09:20 da el error de 30 minutos y Lunes 11:00–13:00 el de cruce, en rojo junto al campo? ¿Editar marca la franja en azul y Eliminar pide confirmación?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~21:55–22:00 | (a) 09:00–09:20: error en rojo por el mínimo de 30 min, no se guarda. (b) 11:00–13:00: error en rojo por cruce con otra franja del mismo día, no se guarda. (c) Editar: franja en azul y botones "Guardar cambios" y "Cancelar"; Eliminar: modal de confirmación (se canceló para conservar la franja). capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-70 · HU-22 — Excepciones (I-09)

**Resultado esperado:** ¿Una excepción de día completo y otra de 10:00–11:00 aparecen en la lista, y el calendario no deja elegir fechas pasadas?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~22:02–22:10 | "martes 10 de noviembre · Día completo" y "lunes 16 de noviembre · 10:00–11:00", cada una con Eliminar. El calendario no permitió elegir el 6-nov ni otras fechas pasadas. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-71 · HU-22 — Disponibilidad desde el admin (I-09)

**Resultado esperado:** ¿Sin asesor dice "Elija un asesor…" y la franja que agrega el admin queda a nombre del asesor elegido?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~22:11–22:16 | Sin asesor: "Elija un asesor…". Con A: su franja del lunes y sus dos excepciones. El admin agregó una franja el miércoles → "Franja agregada" en la fila Miércoles de A; B no la tiene. La franja quedó guardada como 14:00–16:00 por error al cargarla y en V-72 se editó a 12:00–16:00. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-72 · HU-18 — Franjas libres en la ficha (P-07)

**Resultado esperado:** ¿Sin sesión, la ficha de una propiedad Disponible muestra "Horarios disponibles para visitas" en hora de Ecuador, sin horas seleccionables, sin datos del asesor, sin nada antes de 2 h y sin las horas de las excepciones?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~22:20–22:30 | Ficha de [DEMO] Casa en Cumbayá: sección con Actualizar, próximos 14 días, pestañas por día y la nota "Pronto podrás solicitar tu visita aquí"; horas no seleccionables; sin nombre, foto, correo ni teléfono del asesor. Lun 9: 09:00, 10:00, 11:00; lun 16: 09:00 y 11:00 (sin 10:00 por la excepción); ningún martes ni nada de hoy. Los miércoles salían 14:00 y 15:00 porque la franja era 14:00–16:00; tras editarla a 12:00–16:00 y pulsar Actualizar: 12:00 a 15:00 el mié 11 y el mié 18. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-73 · HU-18 — Una visita ocupa la hora y al cancelarla la libera

**Resultado esperado:** ¿Tras crear una visita y pulsar Actualizar, esa hora desaparece; y al cancelarla, vuelve?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-07, ~22:50 – 2026-11-08, 00:05 | `admin.demo` no es staff de Django, así que las visitas se crearon con `setup_visits_demo`: lun 9 a las 09:00 (Cumbayá), 10:00 (Local La Mariscal) y 11:00 (Cumbayá), y mié 11 a las 12:00 (Cumbayá), todas del asesor A; las oportunidades siguieron en Contacto Inicial. Actualizar: el lun 9 desapareció (A ocupado de 09 a 12, también por la visita en otra propiedad: la ocupación es por asesor) y el mié 11 quedó con 13:00 a 15:00. Visita #1 cancelada por shell (lun 9, 09:00 Ecuador = 14:00 UTC) → Actualizar: el lun 9 volvió solo con 09:00. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-74 · HU-18 — Propiedad no disponible

**Resultado esperado:** ¿La ficha de una propiedad en captación no muestra la sección de horarios?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-08, ~00:08–00:12 | Propiedades #2 y #4 en captación (shell). Incógnito, `/properties/<id>`: la ficha no carga ("No se pudo cargar esta propiedad. Verifica la conexión con el servidor" y "Volver al catálogo"); no aparece la sección de horarios. Observación: el mensaje sugiere un fallo de conexión (DT-147). capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-75 · HU-24 — Agenda del asesor (I-08)

**Resultado esperado:** ¿"Mi agenda" muestra la semana de lunes a domingo con "Hoy", cada visita con hora, propiedad, ubicación, cliente, teléfono (enlace para llamar), correo y estado, y "Sin visitas." en los días vacíos?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-08, ~00:13–00:16 | Como asesor A: semana del 2 al 8-nov con el domingo 8 como "Hoy", todo "Sin visitas.". Siguiente (9–15-nov): lun 9 con 10:00–11:00 (Local La Mariscal) y 11:00–12:00 (Casa Cumbayá); mié 11 con 12:00–13:00 (Casa Cumbayá); la de las 09:00, cancelada, no aparece. Cada visita con hora, propiedad, ubicación, nombre del cliente, teléfono (enlace `tel:`), correo y la etiqueta "Programada". "Esta semana" vuelve al 2–8-nov. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-76 · HU-24 — Filtro de estado (I-08)

**Resultado esperado:** ¿Por defecto no aparecen las canceladas; con "Cancelada" solo esas; con "Todas", todas?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-08, ~00:17–00:22 | Semana 9–15-nov. Por defecto ("Activas, sin canceladas"): las 3 programadas. "Cancelada": solo lun 9, 09:00–10:00, Casa Cumbayá, con la etiqueta Cancelada. "Todas": las 4. "Programada": las 3 activas. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

### V-77 · HU-24 — Agenda aislada por asesor y vista del admin (I-08)

**Resultado esperado:** ¿B no ve las visitas de A; el admin ve "Elija un asesor para ver su agenda." y, al elegir a A, la agenda de A?

| Quién | Cuándo | Qué vi | Resultado |
|---|---|---|---|
| Pablo (navegador; worktree `Urbanex-lote2`, SQLite) | 2026-11-08, ~00:23–00:28 | Asesor B, semana 9–15-nov con "Todas": ninguna visita. Admin sin asesor: "Elija un asesor para ver su agenda."; con A: sus 4 visitas; con B: ninguna. capturas borradas por error (ver nota de cierre 2026-11-08). | **Aprobado** |

## Estado actual (2026-11-02)

- **Ronda 3 validada** (V-20 a V-25, Pablo, 2026-10-29 y 2026-10-30): las 6 aprobadas.
- **HU-44 (Fase B), PR #9 existente:** rama `feat/URB-02-HU-44-gestion-usuarios`; V-33..V-39 quedan **Pendiente**. Se conservan las observaciones atribuidas a Sebas del 2026-10-30/31, sin tratarlas como validación aprobada ni reemplazar la evidencia visual pendiente. V-40..V-42 aún no se han realizado.
- **Ambientes:** Sebas informó que la ronda manual del 2026-10-30 se hizo en Supabase PostgreSQL; esa información no se verificó en esta sesión. La suite automatizada de la rama se ejecuta en SQLite con `EMAIL_PROVIDER=console`; la suite local contra PostgreSQL: **No ejecutado**.
- **Seguridad de pruebas (FX-20):** `UserManagementApiTests` fuerza el proveedor de consola y las dos pruebas específicas de Resend parchean el punto de uso en `apps.users.serializers`; la `.env` local no dispara llamadas externas durante la suite.
- **Migraciones:** Sebas indicó que `users.0007`/`0008` ya se aplicaron en Supabase antes de editar el archivo histórico. Sebas propuso restablecer la base de desarrollo y migrar desde `develop` junto a Pablo (DT-96): propuesta **POR CONFIRMAR**, no ejecutada (corregido por Pablo, 2026-11-03). No correr `migrate` contra Supabase en esta tarea. `appraisals.0002`/`0003` aparecían pendientes al iniciar el servidor; no se aplicaron. `makemigrations --check --dry-run` detectó la diferencia `documents/0002_alter_document_file.py` (DT-92); no se generó migración.
- **Frontend (2026-11-02):** `npm run build` exit 0; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0, con 0 errores y 2 avisos por `SiteNav` sin usar en `app/page.tsx` y `app/properties/page.tsx` (DT-24).
- **FX-18 (2026-10-30):** el admin de θ da por rol admin, además de agregar, los permisos de ver la app y la lista (`backend/apps/appraisals/admin.py`), con 2 pruebas nuevas (`EngineParametersAdminTests`). Sin la corrección, la prueba falla igual que V-25. La suite base de `origin/develop` fue 90/90.
- **Hallazgos nuevos:** DT-80, DT-81 y DT-82; N-05 ampliada (pregunta también para la empresa); evidencia nueva en DT-01 y DT-74.
- **Siguiente:** repetir V-33..V-42 y registrar evidencia humana; aclarar la diferencia de mayúsculas en email (DT-95), decidir la propuesta de base de datos de Sebas, **POR CONFIRMAR** (DT-96) (corregido por Pablo, 2026-11-03) y revisar los mensajes 401 (DT-97). La PR #9 ya existe. HU-04, HU-06 y HU-08 completas: **POR CONFIRMAR** (C-02 y θ v1 provisionales, pendientes del tutor).

### Estado anterior (2026-10-30, tarde) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades`

- **PR #7 (motor) fusionada** en `develop` (`9801bc9`).
- **EP-5, primer corte (FX-19)** en la rama `feat/URB-30-34-HU-27-HU-34-oportunidades` (desde `develop` `9801bc9`), en 4 commits:
  - `257ba1c`: commit 1, modelos y migración de `apps.opportunities`;
  - `4282a87`: commit 2, servicio, API y pruebas;
  - `199294a`: commit 3, pantallas I-07 e I-06;
  - el commit de documentación (este registro).
- **Pruebas:** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → **125/125 OK** (2026-10-30); `makemigrations --check` sin cambios; `tsc`, `eslint` de los archivos nuevos y `next build` exit 0; `eslint .` con los mismos 2 errores y 4 avisos previos de DT-24.
- **Migraciones nuevas:** `opportunities.0001_initial`. **Endpoints nuevos:** `POST` y `GET /api/opportunities/`, `GET /api/opportunities/eligible-properties/` y `GET /api/opportunities/agents/`.
- **Decisiones aprobadas:** DS-26 (EP-5 antes de la tarea 4), DS-27 (`apps.opportunities`; §1 y §7 del contexto maestro corregidos en `docs/handoff/`) y DS-28 (reglas del corte).
- **Hallazgos nuevos:** DT-100 (la copia de la raíz del contexto maestro está obsoleta), DT-101 (sin enlace en el menú), DT-102 ("sector" = `location`), DT-103 (filtro de propiedad limitado) y DT-104 (sin auditoría RF-14). DT-31 al día.
- **Archivos compartidos (GPS §3):** una línea en `backend/config/settings.py` y una en `backend/config/urls.py`. **No se tocaron** `backend/apps/users/`, `dashboard/page.tsx`, `SiteNav.tsx` ni `lib/api.ts`.
- **Pendiente:** validación de Pablo (V-26 a V-32); el commit 4 (enlace en el menú) solo con su orden. La rama **ya tiene push** (`origin/feat/URB-30-34-HU-27-HU-34-oportunidades`); **la PR todavía no existe** (la abre Pablo). Al integrar HU-44, revisar DT-105.
- **Avisar a Sebas:** ejecutar `migrate` (`opportunities.0001`); el cambio en `settings.py` es una línea en `INSTALLED_APPS`.

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
  - verificar que la base sea SQLite local antes de `migrate`; ejecutar `setup_comparables_demo` solo en desarrollo;
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
7. **Tarea 4:** filtros del catálogo P-02 (HU-10 / URB-16, adelantada) solo con los campos existentes (DS-16). **Se pospone hasta después del motor (DS-22).** **(2026-10-30) Se pospone otra vez, hasta después del primer corte de EP-5 (DS-26).**
8. **EP-5 "Seguimiento de oportunidades", primer corte (DS-26, 2026-10-30):** HU-27 (I-07) y HU-34 (I-06) en `feat/URB-30-34-HU-27-HU-34-oportunidades`. La máquina de estados de RF-06 (HU-29, HU-31, I-06A) va en un corte posterior.

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
3. ~~Abrir las PR en orden: URB-15 → `develop`~~ (fusionada el 2026-10-27) y después URB-13 (DS-09). Tras fusionar, cada copia verifica la base seleccionada antes de aplicar migraciones locales; nunca contra Supabase. **Avisar a Sebas** de que la fase 3 modificó `dashboard/page.tsx`.
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
- Migración `appraisals/0001_initial`. **Aplicada en la BD local de Pablo el 2026-10-24** (`showmigrations appraisals` → `[X] 0001_initial`). Su `db.sqlite3` cambió pero **no se sube** (DT-02). Antes de `migrate`, verificar que el motor sea SQLite local; nunca ejecutar contra Supabase. Si una copia local carece de la tabla, aplicar allí las migraciones para que `/api/appraisals/` y la publicación funcionen (DT-43).
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
- **DT-42:** formato del `folio` POR CONFIRMAR. **DT-43:** migración aplicada en la copia SQLite local de Pablo; cada copia verifica el motor antes de aplicar migraciones y nunca las ejecuta contra Supabase.

### Validaciones pendientes (requieren a una persona)
Movidas a la sección **"Validaciones pendientes de Pablo"** al inicio de este archivo (V-01, V-02, V-11 y V-12).

### Bloqueos
- **D-04** (fórmula del motor) sigue abierta: bloquea HU-06 y el cálculo de HU-08.
- HU-53 y HU-01 ya no tienen bloqueos técnicos de backend; falta validación en la UI (DT-40) y DT-39.

### Próxima tarea (de esa sesión; la vigente está en "Estado actual")
1. **Abrir el PR** de `feat/URB-15-HU-53-proceso-publicacion` (ya en `origin`) hacia `develop`, revisarlo y fusionarlo con autorización del responsable de integración. Tras fusionar, cada copia verifica el motor y aplica migraciones solo a su base local de desarrollo, nunca a Supabase.
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
5. **🧪 Ronda 3 (motor DS-21):** V-20 a V-25. Antes, verificar el motor; `migrate` y `setup_comparables_demo` se ejecutan solo en SQLite local de desarrollo. *(Sigue pendiente al archivar: ver "Pendiente ahora".)*

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
