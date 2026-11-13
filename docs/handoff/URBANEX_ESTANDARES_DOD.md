# Urbanex — Estándares de código y Definition of Done

| Campo | Valor |
|---|---|
| Última actualización · estados tras los merges | 2026-11-12 · Pablo (con Claude Code) · rama `docs/DT-157-estados-hu-listo`: §4, línea base en `c64b41a` (332 pruebas OK en SQLite; `makemigrations --check` exit 1 por DT-92) |
| Última actualización lote 3 · integración de develop | 2026-11-11 · Pablo (con Claude Code) · fusión de `origin/develop` `97f0e0c` (PR #20 y #23) en la rama del lote 3; §4: 277 pruebas OK en SQLite |
| Última actualización de corrección HU-09 | 2026-11-11 · suite completa 253 pruebas OK en SQLite; regresión de privacidad reproducida antes de corregir; migraciones exit 1 por DT-92 |
| Última actualización aditiva HU-09 | 2026-11-11 · `origin/develop` `47d09ed` integrado; V-45 aprobada; suite integrada 251/251 OK en SQLite |
| Última actualización HU-46 · precisión JWT | 2026-11-09 · Corrección posterior a auditoría PR #20; resultados técnicos en Estándares §4 |
| Última actualización · registro humano V-44 | 2026-11-09 · Fila incorporada por Sebas; auditoría y revisión pendientes |
| Última actualización HU-46 · desbloqueo | 2026-11-09 · 241 pruebas backend OK; comprobación visual del comportamiento nuevo Pendiente |
| Última actualización de integración HU-46 | 2026-11-09 · Línea base y revisión aislada de D-05; resultados registrados en §4 |
| Última actualización aditiva HU-46 | 2026-11-06 · Evidencia de suite y validaciones HU-46; V-44 Pendiente |
| Propósito | Contrato de calidad para cada HU nueva, la escriba una persona o una IA |
| Fecha | 2026-10-22 |
| Última actualización | 2026-11-09 (noche) · Pablo (con Claude Code) · rama `feat/URB-20-21-35-36-HU-15-HU-16-HU-29-HU-30-contactos-crm` (lote 4): §4, ejecución registrada del lote 4 (318 OK; `npm test` 22/22). Antes: 2026-11-09 · Pablo (con Claude Code) · rama `feat/URB-23-24-28-HU-19-HU-20-HU-25-solicitud-visitas` (PR #21): §4, ejecución registrada del lote 3 (263 OK). Antes: 2026-11-08 (noche) · Pablo (con Claude Code) · rama `docs/post-merge-pr15` (PR #18): §4, comando con `apps.visits.tests`, ejecución registrada de `develop` `e19a5df` (229 OK) y **Niveles 1 y 2 de la definición de acabado (DS-35, decisión aplicada por Pablo)**. Historial completo en [Historial de actualizaciones](#historial-de-actualizaciones). |
| Alcance | Backend Django/DRF, frontend Next.js/TypeScript, pruebas y Git |
| Relación con documentos previos | **Complementa, no reemplaza**, `docs/DefinitionOfDone.es.md` (DoD del equipo: pruebas de caja negra + MVP funcional en la interfaz) y la §13 de `URBANEX_MASTER_CONTEXT.md` |
| Evidencia HU-45 | 2026-11-03 · Backend 120/120 OK en SQLite en memoria; build y TypeScript exit 0; ESLint exit 0 con 2 avisos preexistentes; `makemigrations --check --dry-run` exit 1 por `documents/0002_alter_document_file.py`; V-43 Pendiente; PostgreSQL no verificado |
| Evidencia HU-45 interfaz | 2026-11-04 · Backend 120/120, build y TypeScript exit 0; ESLint exit 0 con 2 avisos previos; `makemigrations --check --dry-run` exit 1 por la diferencia previa de `documents/0002`; según Sebas, V-43 completada después del último ajuste |
| Evidencia HU-46 | 2026-11-06 · Backend 165/165 OK en SQLite; `npm test` 9/9; TypeScript y `npm run build` exit 0; ESLint exit 0 con 2 avisos preexistentes. `makemigrations --check --dry-run` exit 1 por la diferencia preexistente `documents/0002_alter_document_file.py` (DT-92), sin generarla ni aplicarla. PostgreSQL No ejecutado; el intento con la configuración del `.env` se detuvo porque ya existía `test_postgres`; no se borró ni reutilizó. V-44 Pendiente |

Principio rector (DoD del equipo): *"Ninguna funcionalidad se considera completa si solo funciona en Postman. Debe poder ejecutarse a través de la interfaz gráfica."* A esto se suma que **el software debe reflejar el proceso de la inmobiliaria**, no solo exponer un CRUD.

---

### Registro humano de ampliación V-44 — 2026-11-09

Sebas incorporó personalmente en `Project_Progress.md`, ampliación V-44, su comprobación del 2026-11-09 a las 15:13:56: recuperación válida con desbloqueo, reinicio de intentos e inicio de sesión con la contraseña nueva. Evidencia local: `evidence/ResetPasswordUsuarioBloqueado.png`; la fecha y hora fueron confirmadas por Sebas en la conversación. La fila humana supersede las menciones anteriores que dejaban esa comprobación o su transcripción Pendiente. El agente conserva ese registro sin emitir una aprobación nueva ni recalcular porcentajes. HU-46 permanece en Pruebas; auditoría de solo lectura y revisión para el merge pendientes. DT-92, DT-68 y los riesgos de seguridad no se cierran con esta nota.

## 1. Clean Code y arquitectura

- **Una HU por cambio.** Cada commit o PR se relaciona con una HU (`URB-XX` / `HU-XX`). No mezclar refactors generales con funcionalidad.
- **Responsabilidades separadas:**
  - *Modelo:* invariantes de datos (restricciones, inmutabilidad). Ejemplo: `backend/apps/documents/models.py`.
  - *Servicio de dominio / método de clase:* operaciones con varios pasos o transacciones. Ejemplo: `Document.upload_new_version()`.
  - *Serializer:* validación de entrada y forma de la salida.
  - *Vista:* permisos, enrutamiento y códigos HTTP.
  - *Componente React:* presentación y estado de UI; la llamada HTTP, idealmente en `frontend/lib/`.
- **Las transiciones de estado no son un `PATCH` genérico** (contexto maestro §11 y §12.1). Publicar, reservar o cerrar son acciones explícitas con sus precondiciones verificadas en el servidor.
- **SOLID donde aporte**, sin abstracciones especulativas: no crear una "capa de servicios" para un `if`.
- **Errores explícitos:** no tragar excepciones; traducir los errores de dominio (`ValidationError` de Django) a 400/409 de DRF. Ejemplo: `DocumentUploadSerializer.create()`.
- **Respetar la estructura existente:** `Property` vive en `apps.users`. Avalúos va en una app nueva (`apps.appraisals`) con FK a `'users.Property'`; no mover modelos dentro de una HU.
- **Decisiones que afectan a otros módulos** (campos nuevos en `Property`, zona horaria, permisos por defecto) se registran en `PROJECT_PROGRESS.md` y en [Deuda técnica](URBANEX_DEUDA_TECNICA.md) antes del merge.

## 2. Backend y validaciones

- **Toda regla de negocio se valida en el backend.** El frontend solo valida para dar una mejor experiencia. Contraejemplo actual: la foto obligatoria (DT-34).
- **Serializers de DRF** para tipos, formatos y coherencia entre campos (por ejemplo, vigencia ≥ emisión).
- **Restricciones de base de datos** para invariantes que no deben romperse aunque falle el código: `UniqueConstraint`, `CheckConstraint` y restricciones condicionales.
- **Permisos por objeto, no solo por rol** (RNF-04, contexto maestro §12.2). Patrón vigente: `role == 'admin' or property.agent_id == user.id`.
- **Inmutabilidad** (documentos, avalúos, historiales): bloquear `save` de campos protegidos, `delete`, `QuerySet.update/delete`, no exponer PUT/PATCH/DELETE y usar un admin de solo lectura.
- **Transacciones** (`transaction.atomic`, `select_for_update`) cuando una operación toca varias filas o compite con otra.
- **Archivos:** validar el tipo real por contenido, no por `content_type`; tamaño en bytes; nombres generados por el servidor; almacenamiento privado para documentos.
- **Migraciones:** nunca editar una ya aplicada en un ambiente compartido; ejecutar `makemigrations --check --dry-run` antes del commit.

## 3. TypeScript y frontend

- Tipado estricto; **sin `any`** salvo justificación en un comentario.
- **No duplicar tipos:** `frontend/types/property.ts` es la fuente para `Property`. Los nuevos contratos van en `frontend/types/<recurso>.ts` y deben reflejar el serializer correspondiente.
- **Contratos verificados:** no escribir el frontend contra un endpoint supuesto (contexto maestro §12.1). Primero el endpoint con sus pruebas; después la UI.
- **Estados de UI obligatorios:** carga, éxito, error y vacío. Ejemplo: el dashboard muestra "Cargando…", la lista, el error o "Aún no tienes propiedades".
- **Nunca simular éxito:** la UI solo confirma lo que el servidor aceptó. Ejemplo: tras guardar, el modal informa qué imágenes o documentos rechazó el servidor.
- **Accesibilidad básica:** `label` asociado, `role="alert"` en errores, `aria-selected` en pestañas, botones con `type` explícito dentro de formularios.
- URL de la API desde `NEXT_PUBLIC_API_URL` (DT-22). (2026-10-25) En pantallas nuevas, usar `authFetch` de `frontend/lib/api.ts`: añade el token y lanza `ApiError` con el cuerpo de DRF para mostrar los errores por campo.
- (2026-10-27) **Sin `alert()` ni `confirm()` nativos:** usar `frontend/components/Dialog.tsx` para confirmar (con `onCancel`) o avisar (sin `onCancel`), y mostrar los errores de un formulario dentro del propio formulario. Ejemplo: el dashboard (FX-16).
- **Acciones irreversibles** (aprobar un avalúo, y en el futuro validar o cerrar): pedir confirmación indicando que no se puede deshacer, y desactivar el botón mientras haya cambios sin guardar. Ejemplo: `handleApprove()` en la pantalla I-12.
- Next 16: en Client Components, `useParams()` devuelve el objeto de parámetros directamente (sin `await`); en Server Components, `params` es una `Promise`.

## 4. Pruebas y Definition of Done por HU

**Ejecución registrada (2026-11-11, rama `feat/URB-09-HU-09-actualizar-propiedad`, correcciones locales de auditoría sobre `f2312a5`):** línea base ejecutada en esta sesión antes de editar, con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y `VIRTUAL_ENV` apuntando al entorno backend instalado: `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 251 tests in 112.667s`, `OK`, exit 0. El primer intento previo sin seleccionar el entorno instalado terminó exit 1 por `ModuleNotFoundError: No module named 'django'`; no se instalaron dependencias. Regresiones añadidas antes del ajuste: `pipenv run python manage.py test apps.users.tests.PropertyWithdrawalApiTests --verbosity 1` → `Ran 10 tests in 0.708s`, `FAILED (failures=4)`, exit 1, reproduciendo la exposición del motivo. Después de corregir el serializer, mismo comando → `Ran 10 tests in 0.679s`, `OK`, exit 0. Suite completa final, con `PYTHONDONTWRITEBYTECODE=1` y motor `sqlite` confirmado de nuevo → `Ran 253 tests in 110.251s`, `OK`, exit 0. `pipenv run python manage.py makemigrations --check --dry-run` → exit 1; detecta únicamente `apps/documents/migrations/0002_alter_document_file.py` (DT-92), sin generar ni aplicar migraciones. En el frontend, ejecución de revisión de esta misma sesión sobre `f2312a5`: `npm test` → 17/17, 0 fallos, exit 0; `npx tsc --noEmit -p .` → sin diagnósticos; `npx eslint .` → exit 0, 0 errores y 2 avisos conocidos DT-24; `npm run build` → exit 0, 15/15 páginas generadas. Frontend sin cambios en esta corrección: no se repiten esos comandos. La suite backend emite los avisos conocidos de longitud de clave de respaldo y el rechazo Resend simulado. `git diff --check` → sin errores, exit 0; comparación del bloque histórico de EP-2 con `origin/develop` → idéntico y todas las filas base conservadas. Suite contra PostgreSQL: **No ejecutado** (DT-68, Nivel 1). No se modifica V-45 ni se aprueba una validación humana nueva.

> Las reglas de trabajo (Fase 0, alcance, entrega, validaciones y auditoría) están en [`AGENTS.md`](../../AGENTS.md) (DS-25). Esta sección detalla el DoD y los comandos; si algo no coincide, manda `AGENTS.md`. Cada PR usa la plantilla [`.github/pull_request_template.md`](../../.github/pull_request_template.md).

Copiar este checklist en el PR o en el registro de la HU. **No marcar una casilla sin evidencia**; si no aplica, escribir "N/A" y el motivo.

```md
### DoD — URB-__ / HU-__
- [ ] Criterios de aceptación identificados (Anexo 2 de la tesis) y citados aquí
- [ ] Implementación fiel al proceso de negocio (RF y reglas del contexto maestro §11)
- [ ] Contrato frontend↔backend verificado (serializer ↔ types/*.ts)
- [ ] Reglas validadas en el servidor (no solo en la UI)
- [ ] Pruebas unitarias pertinentes ejecutadas y aprobadas — comando + resultado:
- [ ] Pruebas de integración / API pertinentes ejecutadas y aprobadas — comando + resultado:
- [ ] `npx tsc --noEmit -p .` y `npx eslint .` sin errores nuevos
- [ ] `npx next build` aprobado (si se tocó el frontend)
- [ ] `manage.py makemigrations --check --dry-run` sin cambios pendientes
- [ ] Suite contra PostgreSQL antes del PR (mayúsculas y tildes, unicidad, longitud de textos, zona horaria DT-01), o "N/A + motivo"
- [ ] Plantilla de PR (`.github/pull_request_template.md`) completa, con la auditoría de solo lectura (`AGENTS.md` §11)
- [ ] Errores y casos límite comprobados (403 de otro asesor, 400 de datos inválidos, vacío)
- [ ] Flujo validado en la interfaz por una persona — quién, cuándo, qué se vio:
- [ ] Sin regresiones conocidas (pruebas previas siguen pasando)
- [ ] GPS, estado de procesos, avance de épicas y deuda actualizados (docs/handoff/)
- [ ] Evidencia registrada en PROJECT_PROGRESS.md (commit, pruebas, capturas)
- [ ] Listo para revisión por el otro desarrollador
```

### Niveles de la definición de acabado (DS-35, 2026-11-08; decisión aplicada por Pablo)

El checklist de arriba se llena según el nivel del PR. Si una regla de este archivo pide más para un PR de Nivel 1, manda DS-35.

| | **Nivel 1: PR de desarrollo diario** | **Nivel 2: cierre de lote o entrega** |
|---|---|---|
| Pruebas automáticas | En verde: suite backend (comando de abajo), `npx tsc --noEmit -p .`, `npx eslint .` y `npm run build` (más `npm test`) | Las mismas, en verde |
| Evidencia de la validación humana | **Una sola por criterio de aceptación** del Anexo 2: captura local en `evidence/` si el criterio es visual; si lo cubre una prueba automática, basta su salida (comando + resultado). Se registra en la V-xx: quién, fecha, hora, qué vio y la ruta `evidence/...` | Además, un **video o GIF corto (1-2 min) del flujo completo**, guardado en `evidence/` |
| Auditoría de solo lectura (`AGENTS.md` §11) | **Una sola por PR** | Una sola por PR |
| Suite contra PostgreSQL | Puede quedar **"No ejecutado"**, con su DT registrado (DT-68) | **Obligatoria**, contra un PostgreSQL **local o desechable**; nunca Supabase |

**No cambia:** toda HU requiere validación humana para contar en el 60 % ([USM §2](URBANEX_USM_TRAZABILIDAD.md)), y nada entra a `develop` sin PR. La carpeta `evidence/` está en `.gitignore` y nunca se sube al repo (`AGENTS.md` §6).

**Comandos de prueba vigentes** (desde `backend/`; las etiquetas son obligatorias hasta corregir DT-06). Actualizado el 2026-10-31 con HU-44 (FX-20); resultado esperado: **116 pruebas OK** (53 users + 19 documents + 44 appraisals; 90 en `origin/develop` + 26 nuevas):

(2026-11-03) En la rama de oportunidades, con `apps.opportunities.tests` en el comando: **155 pruebas OK** (55 users + 19 documents + 44 appraisals + 37 opportunities; FX-25). Antes: 151 al fusionar `develop` (116 + 35, FX-19); sin `develop`, 125 (2026-10-30).

```bash
pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests
pipenv run python manage.py makemigrations --check --dry-run
```

En Windows, fija antes de la suite `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite` y `EMAIL_PROVIDER=console`; comprueba el motor activo. La validación manual reportada por Sebas en Supabase PostgreSQL es independiente de esta suite. La suite local contra PostgreSQL: **No ejecutado**. Nunca ejecutes `migrate` contra Supabase. La comprobación de migraciones actualmente detecta `documents/0002_alter_document_file.py` (DT-92), por lo que su resolución sigue pendiente.

**Ejecución registrada (2026-11-02):** `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests` → 116 pruebas, **OK** (exit 0; SQLite). `pipenv run python manage.py makemigrations --check --dry-run` → exit 1; detecta `apps/documents/migrations/0002_alter_document_file.py`; no se generó ni aplicó migración. En `frontend/`: `npm run build` → exit 0; `npx tsc --noEmit -p .` → exit 0; `npx eslint .` → exit 0, 0 errores y 2 avisos ya registrados en DT-24. Suite local contra PostgreSQL: **No ejecutado**.

**Ejecución registrada (2026-11-04, rama `feat/URB-30-34-HU-27-HU-34-oportunidades` tras fusionar `develop` `5fb3910`):** con `connection.vendor` = `sqlite`, el comando de arriba (con `apps.opportunities.tests`) → `Ran 155 tests`, **OK** (exit 0); `makemigrations --check --dry-run` → "No changes detected", exit 0 (en la carpeta principal; el `documents/0002` de DT-92 solo aparece en un worktree, DT-77). En `frontend/`: `npm test` → 9/9; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0, 0 errores y 2 avisos (DT-24); `npm run build` exit 0. Suite local contra PostgreSQL: **No ejecutado**.

**Ejecución registrada (2026-11-08, `develop` `e19a5df` tras el PR #19; lote 2: HU-22, HU-18 y HU-24):** con `connection.vendor` = `sqlite`, el comando de arriba (con `apps.visits.tests`) → `Ran 229 tests`, **OK** (exit 0); `makemigrations --check --dry-run` → exit 1, detecta `apps/documents/migrations/0002_alter_document_file.py` (DT-92; repetido el 2026-11-08 en el worktree `Urbanex-visitas` al fusionar `develop` en `docs/post-merge-pr15`). En `frontend/`: `npm test` → 17/17; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0, 0 errores y 2 avisos (DT-24); `npm run build` exit 0. Suite local contra PostgreSQL: **No ejecutado**.

**Ejecución registrada (2026-11-09, rama `feat/URB-09-HU-09-actualizar-propiedad`, worktree `.worktrees/hu09`, base `origin/develop` `966cc50` más cambios locales de HU-09):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y `VIRTUAL_ENV` apuntando al entorno backend instalado, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0. Línea base: `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 229 tests in 121.721s`, `OK`, exit 0. Pruebas focalizadas `pipenv run python manage.py test apps.users.tests.PropertyWithdrawalApiTests --verbosity 1`: primer intento → 7 pruebas, 1 fallo por esperar `approved_appraisal` en vez del código existente `appraisal`, exit 1; expectativa corregida → 7 pruebas OK, exit 0; tras agregar republicación exitosa → `Ran 8 tests in 0.698s`, `OK`, exit 0. Suite completa final, mismo comando de línea base → `Ran 237 tests in 130.318s`, `OK`, exit 0. `pipenv run python manage.py makemigrations --check --dry-run`, tanto en línea base como al terminar → exit 1, detecta `documents/0002_alter_document_file.py` (DT-92), sin generar ni aplicar migraciones; motor `sqlite` confirmado nuevamente. En `frontend/`: `npm test` → 17/17, 0 fallos, exit 0; `npx eslint .` → exit 0, 0 errores y 2 avisos preexistentes por SiteNav sin usar en app/page.tsx y app/properties/page.tsx (DT-24); `npm run build` → primer intento exit 1 al descargar Geist/Geist Mono de Google Fonts por restricción de red, repetición con acceso autorizado exit 0, 13/13 páginas generadas; `npx tsc --noEmit -p .` → exit 0. Se reutilizaron copias locales de las dependencias instaladas después de comprobar que los lockfiles son idénticos al normalizar saltos de línea (la primera comparación de hashes crudos difería por CRLF/LF y detuvo la copia); no cambian versiones ni lockfile. La suite emite el aviso de longitud de la clave de respaldo y el rechazo Resend simulado; npm test emite avisos sobre tipo de módulo. `git diff --check` → sin errores, exit 0; `git ls-files -u` → vacío. Suite contra PostgreSQL: **No ejecutado** (DT-68, Nivel 1; no se prueba concurrencia real con SQLite). Validación humana V-45: **Aprobada por Sebas el 2026-11-10 a las 14:59 (Bogotá)**; observación y rutas de evidencia local en `Project_Progress.md`, V-45.

**Ejecución registrada (2026-11-11, rama `feat/URB-09-HU-09-actualizar-propiedad`, cierre documental de V-45):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y `VIRTUAL_ENV` apuntando al entorno backend instalado, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor); print(connection.settings_dict['NAME'])"` → `sqlite` y `C:\Users\mateo\Documents\Urbanex\.worktrees\hu09\backend\db.sqlite3`, exit 0. `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 237 tests in 114.739s`, `OK`, exit 0. `pipenv run python manage.py makemigrations --check --dry-run` → exit 1; detecta `apps/documents/migrations/0002_alter_document_file.py` (DT-92), sin generar ni aplicar la migración. No se modificó código en este cierre; frontend conserva la ejecución completa del 2026-11-09. Suite contra PostgreSQL: **No ejecutado** (DT-68, Nivel 1).

**Ejecución registrada (2026-11-11, rama `feat/URB-09-HU-09-actualizar-propiedad`, después de integrar `origin/develop` `47d09ed` en `048341a`):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y `VIRTUAL_ENV` apuntando al entorno backend instalado, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor); print(connection.settings_dict['NAME'])"` → `sqlite` y `C:\Users\mateo\Documents\Urbanex\.worktrees\hu09\backend\db.sqlite3`, exit 0. `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 251 tests in 129.578s`, `OK`, exit 0. `pipenv run python manage.py makemigrations --check --dry-run` → exit 1; detecta `apps/documents/migrations/0002_alter_document_file.py` (DT-92), sin generar ni aplicar la migración. En `frontend/`: `npm test` → 17/17, exit 0; `npx tsc --noEmit -p .` → exit 0; `npx eslint .` → exit 0, 0 errores y 2 avisos conocidos en `app/page.tsx` y `app/properties/page.tsx` (DT-24); `npm run build` → primer intento exit 1 únicamente por no poder descargar Geist/Geist Mono, repetición con acceso autorizado → exit 0, 15/15 páginas generadas. `git diff --check` → sin errores. Suite contra PostgreSQL: **No ejecutado** (DT-68, Nivel 1).
**Ejecución registrada (2026-11-09, rama `feat/URB-04-HU-46-recuperar-contrasena`, `867159e` con fusión pendiente de `966cc50`, línea base en la carpeta principal):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite` y `EMAIL_PROVIDER=console`, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 235 tests`, `OK`, exit 0; `pipenv run python manage.py makemigrations --check --dry-run` → detecta `documents/0002_alter_document_file.py`, exit 1 (DT-92), sin generar ni aplicar migraciones. En `frontend/`, `npm test` → 17/17, exit 0; `npm run build` → exit 0; `npx tsc --noEmit -p .` → exit 0; `npx eslint .` → exit 0, 0 errores y 2 avisos por imports de SiteNav sin usar (DT-24). Suite contra PostgreSQL: **No ejecutado** (DT-68; Nivel 1, DS-35).

**Ejecución registrada (2026-11-09, revisión HU-46 en `.worktrees/hu46-review`, HEAD separado `867159e` más copia de la fusión pendiente y tres pruebas nuevas):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y `VIRTUAL_ENV` apuntando al entorno backend ya instalado, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 238 tests`, `OK`, exit 0; `pipenv run python manage.py makemigrations --check --dry-run` → detecta `documents/0002_alter_document_file.py`, exit 1 (DT-92), sin generar ni aplicar migraciones. En `frontend/`, `npm test` → 17/17, exit 0; `npx tsc --noEmit -p .` → exit 0; `npx eslint .` → exit 0, 0 errores y 2 avisos preexistentes (DT-24); `npm run build` → exit 0, 15/15 páginas generadas, tras permitir acceso de red para las fuentes. Intentos anteriores: la suite focalizada `pipenv run python manage.py test apps.users.tests.PasswordResetAndRefreshApiTests --verbosity 1` ejecutó 9 pruebas y falló con 1 error por una ruta de activación mal escrita en el test nuevo (exit 1); se corrigió a `/api/auth/users/activate/` antes de la suite completa de 238. El primer build aislado falló por un enlace de node_modules fuera de la raíz de Turbopack (exit 1); se sustituyó por una copia local de las dependencias instaladas, sin cambios de versiones. El siguiente build falló por acceso de red a Google Fonts (exit 1); la repetición con acceso autorizado terminó exit 0. La suite emite un aviso sobre la longitud de la clave de respaldo local y un mensaje de rechazo de correo Resend provocado por una prueba; no se usaron ni mostraron credenciales reales ni se cargó `.env` en estas pruebas. Suite contra PostgreSQL: **No ejecutado** (DT-68; Nivel 1, DS-35). La revisión del agente no constituye aprobación humana de V-44.

**Ejecución registrada (2026-11-09, revisión final HU-46 en `.worktrees/hu46-review`, mismos archivos trasladados a la rama actual):** con `connection.vendor=sqlite` comprobado en la ejecución anterior y las mismas variables de aislamiento, `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 238 tests in 122.762s`, `OK`, exit 0, tras reforzar las pruebas para comprobar que access y refresh son válidos antes del cambio manual o la activación y rechazados después. Comparación SHA-256 de los ocho archivos autorizados entre worktree y carpeta principal → 8/8 coinciden. En la carpeta principal, `git diff --check` y `git diff --cached --check` → sin errores, exit 0; `git ls-files -u` → sin entradas, exit 0; MERGE_HEAD y origin/develop → `966cc50`. Frontend y migraciones no se repitieron porque no cambiaron después de sus ejecuciones anteriores. La fusión sigue pendiente de commit por falta de orden de commit; no se inició otro merge sobre ella. Suite contra PostgreSQL: **No ejecutado** (DT-68).

**Ejecución registrada (2026-11-09, HU-46, ampliación de desbloqueo en `.worktrees/hu46-review` sobre `867159e` con la integración pendiente de `966cc50`):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y el entorno backend ya instalado seleccionado mediante `VIRTUAL_ENV`, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 241 tests in 116.602s`, `OK`, exit 0. Incluye tres pruebas nuevas: desbloqueo al completar recuperación y login con la contraseña nueva; enlaces inválidos, vencidos o usados no cambian el bloqueo ni los intentos; reinicio de intentos de una cuenta aún no bloqueada. `pipenv run python manage.py makemigrations --check --dry-run` → exit 1 por `documents/0002_alter_document_file.py` (DT-92), sin generar ni aplicar migraciones. Frontend no modificado en esta ampliación: no se repiten las comprobaciones anteriores de esta sesión (17/17, build/TypeScript/ESLint exit 0, dos avisos conocidos). Suite contra PostgreSQL: **No ejecutado** (DT-68; Nivel 1, DS-35). La decisión de desbloqueo y la confirmación de las evidencias previas se atribuyen a Sebas en la conversación del 2026-11-09; la comprobación visual del comportamiento nuevo sigue Pendiente, con pasos y tabla vacía bajo V-44.

**Ejecución registrada (2026-11-09, rama `feat/URB-04-HU-46-recuperar-contrasena`, base `00dd676` más corrección local posterior a auditoría PR #20):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite` y `EMAIL_PROVIDER=console`, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0. Línea base: `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 241 tests in 110.178s`, `OK`, exit 0; `pipenv run python manage.py makemigrations --check --dry-run` → detecta `documents/0002_alter_document_file.py`, exit 1 (DT-92). En `frontend/`, `npm test` → 17 pruebas, 17 correctas, 0 fallos, exit 0; emite el aviso de tipo de módulo no especificado en package.json. Tras la corrección, `pipenv run python manage.py test apps.users.tests.PasswordResetAndRefreshApiTests --verbosity 1` → `Ran 14 tests in 6.050s`, `OK`, exit 0; suite completa con el mismo comando de línea base → `Ran 243 tests in 117.040s`, `OK`, exit 0; motor `sqlite` comprobado nuevamente, exit 0; `pipenv run python manage.py makemigrations --check --dry-run` → exit 1 por la misma diferencia DT-92, sin generar ni aplicar migraciones. La suite emite el aviso de longitud de la clave de respaldo local y el rechazo Resend simulado por una prueba; no se cargó `.env` mediante Pipenv. Build, TypeScript y ESLint: No ejecutados en esta corrección exclusivamente backend/documentación; se conserva como antecedente el registro anterior de esta rama, no como ejecución nueva. Suite contra PostgreSQL: **No ejecutado** (DT-68; Nivel 1, DS-35). No se emite aprobación humana de V-44.

**Ejecución registrada (2026-11-09, rama `feat/URB-23-24-28-HU-19-HU-20-HU-25-solicitud-visitas`, worktree `Urbanex-lote3`; lote 3: HU-19, HU-20 y HU-25):** con `PIPENV_DONT_LOAD_ENV=1` y `DB_ENGINE=sqlite`, el comando de arriba → `Ran 263 tests`, **OK** (exit 0; 229 de `develop` + 34 nuevas en `apps.visits.tests`). La línea "Resend rejected activation email…" que aparece en la salida es de una prueba existente de `apps.users` que simula el rechazo de Resend; no hubo llamadas reales. `makemigrations --check --dry-run` → exit 1, solo `apps/documents/migrations/0002_alter_document_file.py` (DT-92, ruta absoluta de DT-77); `opportunities.0002` y `visits.0003` ya están creadas. En `frontend/`: `npm test` → 17/17; `npm run build` exit 0 (con `ƒ /visits/[token]`); `npx tsc --noEmit -p .` exit 0 después del build (antes del build falla por `LayoutProps` en `app/layout.tsx`, DT-78); `npx eslint .` exit 0, 0 errores y 2 avisos (DT-24). Suite local contra PostgreSQL: **No ejecutado** (DT-68, DT-143).

**Ejecución registrada (2026-11-09, noche, rama `feat/URB-20-21-35-36-HU-15-HU-16-HU-29-HU-30-contactos-crm`, worktree `Urbanex-lote4`, sobre el lote 3; lote 4: HU-15, HU-16, HU-29 y HU-30):** con `PIPENV_DONT_LOAD_ENV=1` y `DB_ENGINE=sqlite`, en `9b83b4b` (último commit de código) el comando de arriba → `Ran 318 tests`, **OK** (exit 0; 263 del lote 3 + 55 nuevas en `apps.opportunities.tests`). `makemigrations --check --dry-run` → exit 1, solo `apps/documents/migrations/0002_alter_document_file.py` (DT-92, DT-77); `opportunities.0003` ya está creada. En `frontend/`: `npm test` → 22/22 (5 nuevas en `lib/opportunityPipeline.test.mjs`); `npm run build` exit 0 (con `ƒ /dashboard/opportunities/[id]`); `npx tsc --noEmit -p .` exit 0 después del build (DT-78); `npx eslint .` exit 0, 0 errores y 2 avisos (DT-24). Suite local contra PostgreSQL: **No ejecutado** (DT-68; DS-35, Nivel 1).

**Ejecución registrada (2026-11-11, rama `feat/URB-23-24-28-HU-19-HU-20-HU-25-solicitud-visitas`, `0c0f0a7` con la fusión de `origin/develop` `97f0e0c` (PR #20 HU-46 y PR #23) antes de su commit; worktree `Urbanex-lote3`):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite` y `EMAIL_PROVIDER=console`, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 277 tests in 568.202s`, **OK**, exit 0 (263 del lote 3 + 14 de HU-46); `pipenv run python manage.py makemigrations --check --dry-run` → exit 1, solo `apps/documents/migrations/0002_alter_document_file.py` (DT-92). La salida incluye el aviso `InsecureKeyLengthWarning` de la clave local de pruebas y el rechazo Resend simulado por una prueba; no se cargó `.env`. Comprobación adicional fuera del repo (script en el scratchpad, base de pruebas en memoria): con un JWT emitido antes de cambiar la contraseña enviado como `Bearer`, `GET /api/visits/public/<token>/` (P-08) → 404 y `POST /api/visits/properties/<id>/request/` → 404 (las vistas públicas tienen `authentication_classes = []`, por lo que `PasswordChangedJWTAuthentication` no las afecta), y `GET /api/visits/agenda/` como control → 401 `password_changed`. Los conflictos solo fueron documentales (Progress, Deuda y Estándares) y se resolvieron conservando las dos partes. Frontend (`npm test`, build, tsc, eslint): **No ejecutado** en esta integración. Suite contra PostgreSQL: **No ejecutado** (DT-68, DT-143).

**Ejecución registrada (2026-11-11, rama `feat/URB-20-21-35-36-HU-15-HU-16-HU-29-HU-30-contactos-crm`, fusión de `origin/develop` `5ed0e3b` (PR #21, lote 3) antes de su commit; worktree `Urbanex-lote4`):** con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite` y `EMAIL_PROVIDER=console`, `pipenv run python manage.py shell -c "from django.db import connection; print(connection.vendor)"` → `sqlite`, exit 0; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests --verbosity 1` → `Ran 332 tests in 717.576s`, **OK**, exit 0 (318 del lote 4 + 14 de HU-46); `pipenv run python manage.py makemigrations --check --dry-run` → exit 1, solo `apps/documents/migrations/0002_alter_document_file.py` (DT-92). Antes, `migrate` con `DB_ENGINE=sqlite` en la base local del worktree aplicó solo `users.0009_password_reset_and_password_changed_at` (exit 0). La salida incluye el aviso `InsecureKeyLengthWarning` de la clave local de pruebas y el rechazo Resend simulado por una prueba; no se cargó `.env`. Los conflictos solo fueron documentales (Progress y Estándares) y se resolvieron conservando las dos partes. Frontend (`npm test`, build, tsc, eslint): **No ejecutado** en esta integración. Suite contra PostgreSQL: **No ejecutado** (DT-68; DS-35, Nivel 1).

**Ejecución registrada (2026-11-12, rama `feat/URB-20-21-35-36-HU-15-HU-16-HU-29-HU-30-contactos-crm`, `5af3eb6`; worktree `Urbanex-lote4`; frontend después de la fusión de `origin/develop` `5ed0e3b`):** en `frontend/`, `npm run build` → exit 0 y `npx tsc --noEmit -p .` → exit 0, **según la auditoría del PR #22** (2026-11-12; no se repitieron en esta sesión); `npx eslint .` → exit 0, 0 errores y 2 avisos (`SiteNav` sin usar en `app/page.tsx` y `app/properties/page.tsx`, DT-24); `npm test` → `tests 22`, `pass 22`, `fail 0`, exit 0. Backend: sin cambios de código desde la ejecución anterior (332 OK en SQLite). Suite contra PostgreSQL: **No ejecutado** (DT-68; DS-35, Nivel 1).

**Ejecución registrada (2026-11-12, rama `docs/DT-157-estados-hu-listo`, base `origin/develop` `c64b41a`; worktree `Urbanex-docs-dt157`; línea base de un cambio solo de documentación):** desde `backend/`, con `PIPENV_DONT_LOAD_ENV=1`, `DB_ENGINE=sqlite`, `EMAIL_PROVIDER=console` y el entorno backend ya instalado seleccionado mediante `VIRTUAL_ENV`: `connection.vendor` → `sqlite`; `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests apps.visits.tests` → `Found 332 test(s)`, **OK**, exit 0; `pipenv run python manage.py makemigrations --check --dry-run` → exit 1, detecta `documents/0002_alter_document_file.py` (DT-92, preexistente; no se generó ni aplicó). Frontend: **N/A**, el cambio no toca `frontend/`. Suite contra PostgreSQL: **No ejecutado** (DT-68; DS-35, Nivel 1).

Cada app nueva agrega su etiqueta a este comando en el mismo cambio que la crea.

**Roles en las pruebas (C-08, ~~2026-11-01~~ 2026-10-31, DS-30) (corregido por Pablo, 2026-11-03):** el sistema solo tiene dos roles de usuario, `admin` y `asesor`. El cliente **no es usuario**: no inicia sesión y llega como visitante anónimo. **No crees pruebas con `role='cliente'`.** Para probar que alguien sin cuenta no entra, usa un cliente de pruebas sin `force_authenticate` (401). Para probar la regla de dueño, usa un segundo asesor que no sea el dueño (403). Mientras HU-44 no se fusione, el modelo todavía admite `cliente` y es el valor por defecto (DT-105, DT-106 y DT-107). **(corregido por Pablo, 2026-11-03)** HU-44 ya está fusionada: `User.Role` solo tiene `admin` y `asesor`. Las únicas pruebas que pueden escribir `cliente` son las que prueban el **valor heredado** de C-08 (`users.0007` y el 403 de DT-106), siempre con `update()` y nunca como rol válido (criterio de DT-107).

**Ojo (DT-06):** usa la etiqueta del **módulo** de pruebas (`apps.appraisals.tests`), no la del paquete. `pipenv run python manage.py test apps.appraisals` falla con `ImportError: attempted relative import with no known parent package`, porque falta `backend/apps/__init__.py` y `tests.py` importa con `from .engine import …`. Verificado el 2026-10-29: con `apps.appraisals.tests`, 42 OK.

Desde `frontend/`:

```bash
npm test
npx tsc --noEmit -p .
npx eslint .
npx next build
```

`npm test` (desde 2026-11-01, HU-12, FX-24) ejecuta `node --test "lib/**/*.test.mjs"`, sin dependencias nuevas. Resultado esperado: **9 pruebas OK**. Necesita un Node que ejecute TypeScript sin flags (v22.18+ o v23.6+). Cubre solo lógica pura de `frontend/lib/`; no hay pruebas de componentes ni E2E (DT-37).

Si una validación depende del usuario (por ejemplo, la visual), queda **Pendiente** hasta su confirmación. No se da por buena por inferencia.

## 5. GitFlow y colaboración

> Resumen; la fuente de reglas de Git (ramas, commits, prohibiciones y quién toca qué) es [`AGENTS.md`](../../AGENTS.md) §4 y §5. Si algo no coincide, manda `AGENTS.md`.

**Situación real** (2026-10-22): ramas `master` (principal; `origin/HEAD`), `develop` (integración) y `test` (uso POR CONFIRMAR). No hay CI ni reglas de protección comprobadas.

**Convención:** el contexto maestro define `feat/URB-XX-descripcion`, y el prompt de auditoría propone `feature/HU-XX-…`. **El equipo debe elegir una** (contradicción C-06). Propuesta que combina ambas trazas:

```
feat/URB-10-HU-04-comparables
feat/URB-11-HU-06-valor-sugerido
feat/URB-13-HU-08-calibracion
fix/URB-05-HU-01-catalogo-publico
```

Reglas mínimas:
1. No trabajar directamente sobre `master`; las ramas de HU salen de `develop` y vuelven a `develop` por PR.
2. `git status` y `git pull` antes de empezar; no descartar ni sobrescribir cambios ajenos (`git checkout -- .`, `git reset --hard` y `git stash drop` solo con acuerdo).
3. Revisar `git diff` antes de cada commit; commits pequeños con el mensaje `tipo(URB-XX): descripción`.
4. **Coordinar antes de tocar** `backend/apps/users/models.py`, `backend/apps/users/migrations/`, `backend/config/settings.py`, `frontend/types/property.ts` y `frontend/app/dashboard/page.tsx` (ver [GPS](URBANEX_GPS_ARCHIVOS.md#3-archivos-compartidos-que-requieren-coordinación)).
5. Ejecutar las pruebas pertinentes antes de integrar (la suite de §4, `makemigrations --check --dry-run` y la suite contra PostgreSQL) y pegar el resultado en la plantilla de PR (`.github/pull_request_template.md`).
6. No hacer commit, push ni merge sin la autorización del responsable de la integración.
7. No hacer commit de `backend/.env`, `backend/db.sqlite3`, `backend/media/`, `backend/private_media/` ni datos reales de clientes. `backend/.env.example` es una plantilla sin secretos y sí se puede versionar; revisar `git diff --cached --name-only` antes de cada commit.
8. (2026-10-25) **Windows / PowerShell 5.1:** si el mensaje del commit tiene comillas dobles, escríbelo en un archivo y usa `git commit -F <archivo>`; con `-m @'…'@` PowerShell parte el mensaje y el commit falla (DT-49).
9. (2026-10-25) Si una HU toca una página nueva y un archivo compartido, van en **commits separados** (primero la página y después el compartido), para aislar regresiones (DS-13).

## Evidencia DoD — URB-03 / HU-45 (2026-11-03)

| Criterio | Evidencia y resultado |
|---|---|
| Desbloqueo admin-only y reinicio del contador | Implementado en `POST /api/auth/users/<id>/unlock/`; pruebas nuevas y prueba de login comprueban permisos, estado persistido, `failed_attempts=0` y respuesta genérica |
| Suite backend | `apps.users.tests`, `apps.documents.tests`, `apps.appraisals.tests`: **120 pruebas OK**, exit 0, SQLite en memoria aislada. La orden exacta y el contexto de la configuración están en la nota HU-45 de `Project_Progress.md` |
| Migraciones | `makemigrations --check --dry-run` exit 1: sigue detectando `documents/0002_alter_document_file.py`, diferencia previa a HU-45. No se generó ni aplicó migración |
| Frontend | `npm run build` exit 0; `npx tsc --noEmit -p .` exit 0; `npx eslint .` exit 0, 2 avisos preexistentes de `SiteNav` sin usar |
| Suite PostgreSQL | No verificada. La configuración de Pipenv seleccionó PostgreSQL en un intento previo y el destino del servidor no se confirmó; no repetir hasta confirmar un entorno autorizado |
| Validación visual humana | V-43 completada por Sebas el 2026-11-04, después del último ajuste; ver registro en `Project_Progress.md` |

### Actualización de evidencia HU-45 — interfaz de login (2026-11-04)

La pantalla limpia la contraseña para respuestas `401` y muestra «No se pudo iniciar sesión. Revisa tus credenciales.» ante credenciales incorrectas o cuenta bloqueada. `npm run build` y `npx tsc --noEmit -p .` terminaron exit 0; `npx eslint .` terminó exit 0 con 2 avisos preexistentes. Según Sebas, la validación visual V-43 se completó después del último ajuste; los registros que la marcaban pendiente quedan supersedidos.

### Ejecución tras integrar PR #15 en la rama HU-45 (2026-11-04)

| Comprobación | Comando / resultado |
|---|---|
| Suite backend | Desde `backend/`, con `DB_ENGINE=sqlite` y `PIPENV_DONT_LOAD_ENV=1` (sin cargar `.env`; `EMAIL_PROVIDER` quedó en el valor por defecto `console`): `pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests apps.opportunities.tests` → 159 pruebas, **OK**, exit 0 |
| Migraciones | Desde `backend/`, con SQLite aislado: `pipenv run python manage.py makemigrations --check --dry-run` → exit 1; detecta `apps/documents/migrations/0002_alter_document_file.py` (DT-92). No creó ni aplicó migraciones |
| Pruebas frontend | Desde `frontend/`, `npm test` → 9/9, exit 0 |
| TypeScript | `npx tsc --noEmit -p .` → exit 0 |
| ESLint | `npx eslint .` → exit 0; 2 avisos conocidos por `SiteNav` sin usar |
| Build | `npm run build` → exit 0; Next.js compiló y generó 11/11 páginas |
| Validación humana | Según Sebas, V-43 se ejecutó después del último ajuste y cubrió los dos criterios de HU-45; ver evidencia detallada en `Project_Progress.md` |
| PostgreSQL | **No verificado**. El intento por defecto abortó antes de ejecutar pruebas porque `test_postgres` ya existía; no se borró ni reutilizó. Suite final ejecutada en SQLite |

## Historial de actualizaciones

Entradas anteriores de la celda "Última actualización" de la cabecera, movidas aquí sin cambios el 2026-11-08 (paso 5 del PR #18, `docs/post-merge-pr15`). La más reciente arriba; el texto es el mismo que estaba en la celda.

- Antes: 2026-11-08 · Pablo · validación visual del lote 2 (V-65 a V-77) registrada sin cambios de código ni incorporación de capturas a Git; no se ejecuta `migrate` contra Supabase y la batería de validación se ejecuta sobre el worktree local con SQLite.
- Antes: 2026-11-04 (después del merge) · §4: ejecución registrada tras el merge (155 OK; `npm test` 9/9).
- Antes: 2026-11-04 · Pablo (con Claude Code) · rama `feat/URB-30-34-HU-27-HU-34-oportunidades`: merge de `origin/develop` (`5fb3910`, con los PR #14 y #16); se conservan las entradas de ambos lados.
- Antes (develop): 2026-11-02 · suite backend 116/116 en SQLite; build y TypeScript exit 0; ESLint exit 0 con 2 avisos; `makemigrations --check --dry-run` detecta `documents/0002_alter_document_file.py` (DT-92); suite local PostgreSQL **No ejecutado**.
- Antes: 2026-10-31 · §4 y §5 remiten a `AGENTS.md` (DS-25); §4 registra la suite de 116 pruebas, `makemigrations --check --dry-run`, los requisitos PostgreSQL y la plantilla de PR; §5 documenta archivos prohibidos.
- Antes: 2026-10-30 · §4: 90 pruebas (FX-18).
- Antes: 2026-10-29 · aviso de DT-06 sobre la etiqueta `apps.appraisals`.
- Antes: 2026-10-28 · §4 (88 pruebas, motor DS-21).
- Antes: 2026-10-27 · §3 (sin `alert`/`confirm`: usar `Dialog`) y §4 (64 pruebas).
- Antes: 2026-10-25 · §3 (`authFetch`, acciones irreversibles, `useParams` en Next 16) y §5 (reglas 8 y 9) · Rama HU-12: 2026-11-01 · §4: `npm test` en el frontend (9 pruebas, HU-12, FX-24).
- Antes: 2026-10-31 · §4 y §5 remiten a `AGENTS.md` (DS-25); §4: suite contra PostgreSQL y plantilla de PR; §5: `makemigrations --check` y archivos prohibidos.
- Antes: 2026-10-30 · §4: 90 pruebas (FX-18).
- Antes: 2026-10-29 · §4: aviso de DT-06 sobre la etiqueta `apps.appraisals`.
- Antes: 2026-10-28 · §4 (88 pruebas, motor DS-21).
- Antes: 2026-10-27 · §3 (sin `alert`/`confirm`: usar `Dialog`) y §4 (64 pruebas).
- Antes: 2026-10-25 · §3 (`authFetch`, acciones irreversibles, `useParams` en Next 16) y §5 (reglas 8 y 9) · Rama de oportunidades: 2026-11-03 (noche) · §4: C-08 con fecha 2026-10-31 (DS-30) y regla del valor heredado `cliente` en las pruebas (DT-106, DT-107).
- Antes: 2026-11-03 (tarde) · §4: **155 pruebas OK** en la rama de oportunidades (FX-25: +2 en `opportunities` y +2 en `users`).
- Antes: 2026-11-03 · Pablo (con Claude Code), rama `feat/URB-30-34-HU-27-HU-34-oportunidades`: merge de `origin/develop` (`a071b97`, con los PR #9 y #13); se conservan las entradas de ambos lados.
- Antes (rama de oportunidades, sin develop): 2026-11-01 · §4: regla de roles en las pruebas (solo `admin` y `asesor`; el cliente es anónimo; sin `role='cliente'`; C-08, FX-23).
- Antes: 2026-10-30 (tarde) · §4: `apps.opportunities.tests` en el comando y 125 pruebas (FX-19).
