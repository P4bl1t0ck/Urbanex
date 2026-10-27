# Urbanex — Estándares de código y Definition of Done

| Campo | Valor |
|---|---|
| Propósito | Contrato de calidad para cada HU nueva, la escriba una persona o una IA |
| Fecha | 2026-10-22 |
| Última actualización | 2026-10-27 · §4 (58 pruebas con el seeder). Antes: 2026-10-25 · §3 (`authFetch`, acciones irreversibles, `useParams` en Next 16) y §5 (reglas 8 y 9) |
| Alcance | Backend Django/DRF, frontend Next.js/TypeScript, pruebas y Git |
| Relación con documentos previos | **Complementa, no reemplaza**, `docs/DefinitionOfDone.es.md` (DoD del equipo: pruebas de caja negra + MVP funcional en la interfaz) y la §13 de `URBANEX_MASTER_CONTEXT.md` |

Principio rector (DoD del equipo): *"Ninguna funcionalidad se considera completa si solo funciona en Postman. Debe poder ejecutarse a través de la interfaz gráfica."* A esto se suma que **el software debe reflejar el proceso de la inmobiliaria**, no solo exponer un CRUD.

---

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
- **Acciones irreversibles** (aprobar un avalúo, y en el futuro validar o cerrar): pedir confirmación indicando que no se puede deshacer, y desactivar el botón mientras haya cambios sin guardar. Ejemplo: `handleApprove()` en la pantalla I-12.
- Next 16: en Client Components, `useParams()` devuelve el objeto de parámetros directamente (sin `await`); en Server Components, `params` es una `Promise`.

## 4. Pruebas y Definition of Done por HU

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
- [ ] Errores y casos límite comprobados (403 de otro asesor, 400 de datos inválidos, vacío)
- [ ] Flujo validado en la interfaz por una persona — quién, cuándo, qué se vio:
- [ ] Sin regresiones conocidas (pruebas previas siguen pasando)
- [ ] GPS, estado de procesos, avance de épicas y deuda actualizados (docs/handoff/)
- [ ] Evidencia registrada en PROJECT_PROGRESS.md (commit, pruebas, capturas)
- [ ] Listo para revisión por el otro desarrollador
```

**Comandos de prueba vigentes** (desde `backend/`; las etiquetas son obligatorias hasta corregir DT-06). Actualizado el 2026-10-24 con `apps.appraisals` (DT-41); resultado esperado: **58 pruebas OK** (52 + 6 del comando `setup_demo_data`, 2026-10-27):

```bash
pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests
pipenv run python manage.py makemigrations --check --dry-run
```

Cada app nueva agrega su etiqueta a este comando en el mismo cambio que la crea.

Desde `frontend/`:

```bash
npx tsc --noEmit -p .
npx eslint .
npx next build
```

Si una validación depende del usuario (por ejemplo, la visual), queda **Pendiente** hasta su confirmación. No se da por buena por inferencia.

## 5. GitFlow y colaboración

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
5. Ejecutar las pruebas pertinentes antes de integrar y pegar el resultado en el PR.
6. No hacer commit, push ni merge sin la autorización del responsable de la integración.
7. No hacer commit de `backend/.env`, `backend/private_media/` ni datos reales de clientes.
8. (2026-10-25) **Windows / PowerShell 5.1:** si el mensaje del commit tiene comillas dobles, escríbelo en un archivo y usa `git commit -F <archivo>`; con `-m @'…'@` PowerShell parte el mensaje y el commit falla (DT-49).
9. (2026-10-25) Si una HU toca una página nueva y un archivo compartido, van en **commits separados** (primero la página y después el compartido), para aislar regresiones (DS-13).
