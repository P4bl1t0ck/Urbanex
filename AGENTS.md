# Urbanex — Reglas para agentes de IA

**Única fuente de reglas** para cualquier asistente (Claude Code, Copilot u otro) y para la persona que lo dirige. `CLAUDE.md` y `.github/copilot-instructions.md` solo apuntan aquí (DS-25). El estado del proyecto **no** se describe aquí: se lee en `docs/handoff/`. Si una regla de este archivo choca con otro documento, **detente y pregunta**; no elijas tú.

## 1. Por dónde empezar (en este orden)

1. `AGENTS.md` (este archivo).
2. [`docs/handoff/URBANEX_USM_TRAZABILIDAD.md`](docs/handoff/URBANEX_USM_TRAZABILIDAD.md) (si existe): mapa de historias y trazabilidad.
3. [`URBANEX_MASTER_CONTEXT.md`](docs/handoff/URBANEX_MASTER_CONTEXT.md): requisitos, RF, roles, backlog y reglas de negocio (§4, §10–§13).
4. [`URBANEX_ESTADO_PROCESOS.md`](docs/handoff/URBANEX_ESTADO_PROCESOS.md): estado real de cada HU y sus criterios.
5. [`URBANEX_DEUDA_TECNICA.md`](docs/handoff/URBANEX_DEUDA_TECNICA.md): riesgos (DT), decisiones tomadas (DS) y pendientes (D, N, C).
6. [`URBANEX_GPS_ARCHIVOS.md`](docs/handoff/URBANEX_GPS_ARCHIVOS.md): qué archivo hace qué y cuáles son compartidos (§3).
7. [`URBANEX_ESTANDARES_DOD.md`](docs/handoff/URBANEX_ESTANDARES_DOD.md): estándares, comando de pruebas vigente (§4) y checklist DoD.
8. [`Project_Progress.md`](Project_Progress.md): **empieza por la última nota de cierre de sesión**; luego la directiva GPS y las V-xx.

Según la tarea: [Seguridad](docs/handoff/URBANEX_SEGURIDAD_Y_DEUDA.md) (SEC, INF), [Avance de épicas](docs/handoff/URBANEX_AVANCE_EPICAS.md), [Guía de continuidad](docs/handoff/URBANEX_GUIA_CONTINUIDAD.md). Léelos; no los copies.

## 2. Regla principal: Fase 0 y esperar el "ok"

Siempre, **aunque el prompt pida hacerlo directo**:
1. `git status --short --branch`: confirma la rama y que no haya cambios ajenos sin commit. Si algo no cuadra, para.
2. Resume la tarea y sus criterios de aceptación (ideal: la ficha [`docs/handoff/PLANTILLA_TAREA.md`](docs/handoff/PLANTILLA_TAREA.md)).
3. Corre la línea base de pruebas (Estándares §4) y anota la salida real.
4. Lista **los archivos que vas a tocar** (marca los compartidos), las pruebas a agregar y los riesgos.
5. Lista tus dudas, sobre todo lo que dependa de una decisión pendiente (D-xx, N-xx, C-xx).
6. **Detente** hasta recibir el "ok" de la persona. Durante el trabajo, explica qué vas a hacer y por qué **antes de cada paso importante**.

## 3. Alcance cerrado y preguntas abiertas

- Solo se tocan los archivos listados en la Fase 0. Si hace falta otro, **detente y pregunta**.
- Lo que veas mal fuera de la tarea se anota como hallazgo y se pregunta si se registra; no se arregla.
- **No inventes decisiones.** Si falta una regla de negocio, regístrala como pregunta pendiente en la Deuda técnica, avisa y sigue con lo que no dependa de ella.
- No agregues dependencias sin decirlo en la Fase 0.

## 4. Quién toca qué y rangos de IDs

| | Pablo | Sebas |
|---|---|---|
| Código propio | `backend/apps/opportunities/` | `backend/apps/users/` |
| Compartido (avisar antes) | `backend/config/settings.py`, `backend/config/urls.py`, `frontend/components/SiteNav.tsx` y los del GPS §3 | ídem |
| DT | DT-77..82, DT-100..119 | DT-90..99, DT-120..139 |
| V | V-01..32, V-60 en adelante | V-33..59 |
| FX | FX-01..19, FX-21..29 | FX-20, FX-30..39 |
| DS | DS-25..28, DS-31..39 | DS-29, DS-30, DS-40..49 |

- **Manda esta tabla.** Si un documento o un ID antiguo no coincide con ella, no se renumera nada: los IDs ya usados se quedan como están.
- **Documentos:** solo se agregan filas; nunca se reescriben las del otro.
- Antes de usar un ID, **búscalo en `develop` y en las ramas remotas** (`git fetch`, luego `git show origin/<rama>:<archivo>`). No lo copies de memoria.

## 5. Git

- Una historia por rama (`feat/URB-XX-HU-YY-descripcion`), **siempre desde `develop` actualizado**. Vuelve a `develop` solo por PR.
- **Excepción:** una tarea solo de documentación o configuración, sin HU, va en una rama `docs/<descripcion>` con commits `docs(DS-xx): …` o `chore(DT-xx): …`, citando la decisión o el hallazgo que la origina.
- Antes de pedir el PR: `git pull origin develop` y resolver los conflictos.
- Commits pequeños por capa (modelo · API y pruebas · pantalla · docs); un archivo compartido va en su propio commit. Mensaje `tipo(URB-XX): descripción`; en PowerShell, `git commit -F <archivo>`.
- Antes de **cada** commit: `git diff --cached --name-only` y muéstralo. Nunca `git add -A`, `git add .` ni `git commit -a`.
- Commit y push solo si la orden de la persona lo incluye. **El PR lo abre la persona.**

**Prohibido:** push o merge a `develop`/`master` · force push (también `--force-with-lease`) **sin aprobación explícita de Pablo** (avisar no basta) · abrir un PR sin orden · commitear `backend/db.sqlite3`, `.env`, `backend/media/` o `backend/private_media/` · editar fuera del alcance.

## 6. Credenciales

- Nunca copies claves reales (contraseñas, API keys, cadenas de conexión, hosts reales) en código, documentos, prompts, commits ni PR. No muestres ni pidas el contenido de `backend/.env`.
- Si ves una clave real en un archivo o en el chat: **avisa de inmediato**, no la repitas y di que hay que rotarla. Para dar acceso a un servicio se **invita** a la persona; la clave no se comparte (DT-79).

## 7. Base de datos

- No corras `migrate` contra Supabase desde una rama.
- No edites migraciones ya fusionadas o aplicadas en otro ambiente: crea una nueva y pregunta antes.
- Las migraciones de `apps/users` se hacen en **una sola rama a la vez** (pull antes de `makemigrations`).
- Antes del PR, corre la suite contra **PostgreSQL**: mayúsculas y tildes, unicidad, longitud de textos y zona horaria (DT-01).
- Credenciales filtradas: se rotan de inmediato.

## 8. Evidencia y estados

- Toda afirmación lleva **archivo:línea**, **comando + salida real** o **hash de commit**. Si algo falló, dilo. Nunca "todo bien" sin evidencia.
- Lo que no comprobaste en esta sesión es **No verificado**; lo que te dijo una persona va **atribuido** ("según Sebas, 2026-10-29"). Nombres: **Pablo** y **Sebas** (Sebas firma en GitHub como *Mateo Cartagena*); nunca "el usuario".
- Usa solo los estados ya definidos: HU (Por hacer · En Curso · Listo · Pruebas · Bloqueado · POR CONFIRMAR); validación (Aprobado · Fallido · Pendiente · No aplicable); criterio (Implementado · Verificado · Validado); hallazgo (Confirmado · Potencial · POR CONFIRMAR). Un DT es **Resuelto** solo si cumple su criterio de cierre, citando la prueba; si falta la validación humana: "Resuelto en código; validación Pendiente".

## 9. Validaciones honestas

El agente **nunca** marca una validación (técnica, funcional, visual o V-xx) como aprobada. Puede redactar la V-xx en `Project_Progress.md` (pasos y resultado esperado) con la tabla **vacía** y "Pendiente". Solo una persona la llena: **quién, fecha, hora, qué vio exactamente y la ruta de una captura**. Una HU no pasa de **Pruebas** sin su V-xx hecha por una persona.

## 10. Al terminar

Entrega, en el mismo PR:
1. La **suite completa** con su número real de OK (Estándares §4 + `makemigrations --check --dry-run`) y, si se tocó el frontend, `npm run build`, `npx tsc --noEmit -p .` y `npx eslint .`.
2. La **documentación actualizada**, con fecha en "Última actualización": Progress, Estado de procesos, Avance de épicas, Deuda (DT, FX, DS), GPS, DoD (checklist de Estándares §4 en el PR, con evidencia o "N/A + motivo") y, si cambia un riesgo, Seguridad.
3. Una **explicación en lenguaje simple**: qué hace cada cambio, en qué archivo está (backend y frontend) y cómo se conectan, para que cualquiera del equipo pueda entenderlo, continuarlo o repararlo.
4. La **lista de validaciones visuales** para la persona, sin marcarlas como hechas, y las decisiones que necesita.

**Nota de cierre de sesión:** al final de cada sesión, agrega en `Project_Progress.md` (sección "Notas de cierre de sesión", la más reciente arriba) una nota corta: fecha, autor, rama, qué se hizo, qué falta y siguiente paso.

## 11. Auditoría antes de cada PR

Obligatoria, en un **chat nuevo y solo de lectura** (el auditor no edita nada). Prompt corto:

> Eres auditor de solo lectura del repo Urbanex. No modifiques archivos ni ejecutes comandos que escriban. Lee `AGENTS.md`. Compara la rama actual con `origin/develop` (`git diff origin/develop...HEAD --name-only` y el diff completo) y reporta, con archivo:línea o comando + salida: (1) archivos fuera del alcance de la tarea o de otra persona (§4); (2) archivos prohibidos o credenciales; (3) migraciones editadas o en conflicto; (4) IDs DT/FX/DS/V repetidos o fuera de rango; (5) validaciones marcadas como aprobadas sin persona, fecha, hora y captura; (6) documentación que falte según §10; (7) resultado real de la suite. Termina con "Apto para PR" o "No apto" y la lista de lo que hay que corregir.

## 12. Idioma

Responde en **español**, claro y sin jerga innecesaria.
