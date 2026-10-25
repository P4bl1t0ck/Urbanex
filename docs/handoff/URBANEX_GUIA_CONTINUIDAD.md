# Urbanex — Guía de continuidad (punto de entrada para Sebas)

| Campo | Valor |
|---|---|
| Propósito | Retomar el desarrollo, empezando por Avalúos (HU-04, HU-06, HU-08), sin depender de explicaciones orales |
| Fecha de auditoría | 2026-10-22 · rama `develop` |
| Estado | Instantánea. **Actualízala** al cerrar cada HU (ver Paso 5) |
| Última actualización | 2026-10-25 · Pasos 1, 3 y 4: pantalla I-12 hecha (fases 1 y 2 de DT-40) en `feat/URB-13-HU-08-pantalla-avaluo`, que sale de la rama de URB-15 (DS-09). Antes: 2026-10-24, `apps.appraisals` y bloqueo de publicación. Regla obligatoria: [Directiva de continuidad (GPS)](../../PROJECT_PROGRESS.md) |

---

## Paso 0. Antes de que Sebas clone (responsabilidad de Pablo)

Estas condiciones se comprobaron como **no cumplidas** en la auditoría:

- [ ] Hacer commit del trabajo pendiente en `develop` (15 archivos modificados y 13 nuevos; DT-36).
- [ ] Hacer commit de `URBANEX_MASTER_CONTEXT.md` (hoy sin rastrear) y de `docs/handoff/`.
- [ ] Decidir cómo recibe Sebas la tesis: `ProyectoCapstoneV4 (3).md` está **ignorado** en `.gitignore` (DT-27).
- [ ] Hacer push de `develop`.

## Paso 1. Comprender el proyecto

Orden de lectura:

1. `URBANEX_MASTER_CONTEXT.md`: §1 visión, §4 RF-01/RF-10/RF-11, §7 modelos (sobre todo §7.3 `Appraisal`), §11 reglas de estado, §13 DoR/DoD, §14 decisiones pendientes.
2. `ProyectoCapstoneV4 (3).md`, Anexo 2: criterios de aceptación de HU-04 a HU-08 y HU-53.
3. [URBANEX_ESTADO_PROCESOS.md](URBANEX_ESTADO_PROCESOS.md): qué funciona y qué no, por HU, y las **contradicciones C-01 a C-08**.
4. [URBANEX_GPS_ARCHIVOS.md](URBANEX_GPS_ARCHIVOS.md) §2: **mapa de dependencias de Avalúos**.
5. [URBANEX_DEUDA_TECNICA.md](URBANEX_DEUDA_TECNICA.md): P0 y P1, y decisiones D-04, C-02, N-01 a N-03.
6. [URBANEX_ESTANDARES_DOD.md](URBANEX_ESTANDARES_DOD.md): checklist de DoD y convención de ramas.
7. [URBANEX_AUDITORIA_CODIGO.md](URBANEX_AUDITORIA_CODIGO.md): stack, endpoints y comandos.
8. [URBANEX_AVANCE_EPICAS.md](URBANEX_AVANCE_EPICAS.md): cómo se mide el avance.
9. `PROJECT_PROGRESS.md` y `docs/DefinitionOfDone.es.md`: registro diario y DoD previo del equipo.

**Resumen en 6 líneas:**
- Monorepo con `backend/` (Django 6.1, DRF, JWT, SQLite) y `frontend/` (Next.js 16, React 19, Tailwind 4).
- `Property` vive en `backend/apps/users/models.py` y el expediente en `backend/apps/documents/`.
- El proceso que importa: **captación → expediente + avalúo → publicación**.
- (2026-10-24) La captación y el expediente funcionan a nivel técnico; el avalúo existe como modelo inmutable **sin motor** (D-04); publicar exige foto + corretaje + avalúo aprobado.
- (2026-10-25) La pantalla I-12 (`/dashboard/properties/[id]/appraisal`) inicia, calibra y aprueba avalúos; todavía no se llega a ella desde el dashboard (fase 3) y su validación visual está pendiente.
- El catálogo ya no muestra la captación a anónimos (DT-07 resuelto) y `status` es de solo lectura (DT-09 resuelto): la única vía para publicar es `POST …/publish/`.
- Nada está desplegado; no hay CI.

## Paso 2. Preparar el entorno

Comandos confirmados con los archivos del proyecto y ejecutados en la auditoría, salvo los marcados con *(no ejecutado)*.

```bash
# 0. Estado de Git
git status --short --branch        # debe indicar develop; revisa qué no es tuyo antes de tocar nada
git pull origin develop

# 1. Backend (Python 3.14 + Pipenv)
cd backend
pipenv install                     # (no ejecutado en la auditoría; el entorno ya existía)
#   Crea backend/.env con las variables SECRET_KEY, DEBUG y ALLOWED_HOSTS
#   (pide los valores a Pablo; no hay .env.example — DT-21). Pipenv carga .env solo.
pipenv run python manage.py migrate                # crea también la tabla de avalúos (DT-43)
pipenv run python manage.py test apps.users.tests apps.documents.tests apps.appraisals.tests   # esperado: 52 tests OK (2026-10-24)
pipenv run python manage.py runserver          # (no ejecutado) http://127.0.0.1:8000

# 2. Frontend (Node 25 / npm 10)
cd ../frontend
npm install                        # (no ejecutado en la auditoría)
npx tsc --noEmit -p .              # esperado: sin errores
npm run dev                        # (no ejecutado) http://localhost:3000
```

- El frontend llama a `http://127.0.0.1:8000` (hardcodeado en el dashboard) y CORS permite `localhost:3000` y `127.0.0.1:3000`.
- **Comprobar la conexión:** abrir `/login`, entrar y ver "Mis propiedades". Pablo confirmó el 2026-10-22 que el dashboard carga datos.
- **Ojo:** `manage.py test` **sin etiquetas no encuentra pruebas** (DT-06). Usa siempre las etiquetas.

### Usuarios de prueba (necesarios: hoy todos los usuarios de la BD son `cliente`)

Comandos sugeridos, *no ejecutados en la auditoría*. El login es **por email**; las contraseñas se eligen localmente y no se versionan:

```bash
pipenv run python manage.py shell -c "from apps.users.models import User; User.objects.create_user(username='asesor_demo', email='asesor.demo@urbanex.test', password='CAMBIA-ESTA', role='asesor')"
pipenv run python manage.py shell -c "from apps.users.models import User; User.objects.create_user(username='admin_demo', email='admin.demo@urbanex.test', password='CAMBIA-ESTA', role='admin', is_staff=True)"
```

## Paso 3. Dependencias que Avalúos necesita conocer

Detalle completo en el [GPS §2](URBANEX_GPS_ARCHIVOS.md#2-mapa-de-dependencias-de-avalúos-hu-04-hu-06-hu-08).

| Necesitas | ¿Existe? | Dónde / qué falta |
|---|---|---|
| Propiedad sujeto del avalúo | Sí | `Property` en `backend/apps/users/models.py` → FK `'users.Property'` |
| Tipo de propiedad para no mezclar comparables | Sí | `property_type` (`casa`/`departamento`/`local`/`terreno`) |
| Precio y área para el precio por m² | Sí | `price` (Decimal), `area_m2` (Float): convertir explícitamente |
| Zona para segmentar comparables | **No** | Falta `zone` (DT-19, N-03) |
| Coordenadas | Sí, pero vacías | `latitude`/`longitude` existen; 0 de 28 propiedades las tienen |
| Antigüedad, conservación, área útil, operación | **No** | Dependen de D-04 (DT-19) |
| Fórmula y umbrales del motor | **No** | Decisión **D-04** abierta: **no la inventes** |
| Regla de 1–2 comparables | **Contradictoria** | C-02 |
| Permisos | Sí | Patrón `role == 'admin' or property.agent_id == user.id` |
| Autenticación desde el frontend | Sí | `sessionStorage.getItem("access")` + `Authorization: Bearer` |
| Contrato de corretaje para publicar | Sí (en uso) | `get_missing_publication_requirements()` en `backend/apps/users/views.py` (DS-04) |
| Patrón de registro inmutable | Sí | `backend/apps/documents/models.py` y `backend/apps/appraisals/models.py` |
| App `apps.appraisals`, modelo `Appraisal` y endpoints | **Sí (2026-10-24)** | `/api/appraisals/`; placeholder manual hasta D-04 (DS-02). Ver [GPS HU-08](URBANEX_GPS_ARCHIVOS.md) |
| `frontend/types/appraisal.ts` y `authFetch` | **Sí (2026-10-25)** | Ver [GPS HU-08](URBANEX_GPS_ARCHIVOS.md). Usa `authFetch` de `frontend/lib/api.ts` en pantallas nuevas |
| Pantalla I-12 | **Sí (2026-10-25)**, visual pendiente | `frontend/app/dashboard/properties/[id]/appraisal/page.tsx` |
| Pantalla I-11 (comparables) | **No** | Es tu trabajo (HU-04); ruta nueva bajo `/dashboard/properties/[id]/appraisal/` |
| Servicio de IA (HU-07) | **No** | Fuera de tu alcance; HU-08 debe aceptar la justificación manual |

## Paso 4. Siguiente paso seguro

Orden recomendado según las dependencias reales:

1. **Desbloquear decisiones (sin código).** Llevar al equipo y al tutor D-04 (fórmula, factores, umbrales), C-02 (1–2 comparables), N-02 (qué propiedades son comparables) y N-03 (cómo se define la zona). Registrar las respuestas en `URBANEX_MASTER_CONTEXT.md` §14 y en `PROJECT_PROGRESS.md`.
2. **Comprobar la línea base:** ejecutar las 52 pruebas y `tsc` (Paso 2) y anotar el resultado.
3. ~~Primer incremento: crear `apps.appraisals` con su inmutabilidad~~ **Hecho el 2026-10-24** (commit `58b968c`). ~~Cerrar DT-09~~ **Hecho el 2026-10-24** (FX-11).
   - ~~Siguiente incremento sin D-04: pantalla I-12 + `frontend/types/appraisal.ts`~~ **Fases 1 y 2 hechas el 2026-10-25** (commits `161f845`, `af9b416`). **Siguiente:** fase 3 en `dashboard/page.tsx` (archivo compartido: avisar antes), en su propio commit (DS-13).
4. **Campos de `Property` para HU-04/HU-05 (coordinar con Pablo):** una sola migración `users.0007` con los campos acordados. Actualizar `PropertySerializer`, `frontend/types/property.ts` y la pestaña "Datos generales" del dashboard.
5. **HU-04:** endpoint de candidatos a comparables (mismo tipo y zona) y selección de 3 a 5 con registro manual de respaldo. Pantalla I-11 en una **ruta nueva**, no dentro del modal, para evitar conflictos en `dashboard/page.tsx`.
6. **HU-06**, solo con D-04 aprobada: cálculo determinista en un servicio aislado y con pruebas para 0, 1–2 y 3+ comparables y para dispersión alta (contexto maestro §12.4).
7. **HU-08:** backend y pantalla I-12 hechos; faltan la fase 3 y la validación visual (ver paso 3).
8. ~~HU-53: exigir el avalúo aprobado y el corretaje en `PropertyPublishView`~~ **Hecho el 2026-10-24** (commit `cca371e`). Falta: `slug` + metaetiquetas (segundo criterio de HU-53) y mostrar `missing_requirements` en la UI.

**Validación funcional por incremento:** como asesor de prueba, crear una propiedad, abrir su avalúo, seleccionar comparables, ver el valor y calibrarlo. Registrar quién lo probó, cuándo y qué se vio.

**Evidencia por cambio:** commit, comando de pruebas con su resultado, capturas cuando haya UI, y la actualización de los documentos del Paso 5.

## Paso 5. Coordinar el trabajo y mantener la trazabilidad

- **Ramas:** una por HU desde `develop` (convención en [Estándares §5](URBANEX_ESTANDARES_DOD.md#5-gitflow-y-colaboración)). **Excepción vigente (DS-09):** `feat/URB-13-HU-08-pantalla-avaluo` sale de `feat/URB-15-HU-53-proceso-publicacion`; su PR se integra **después** de la de URB-15.
- **Asistentes de IA en `frontend/`:** `frontend/CLAUDE.md` apunta a `@AGENTS.md`, que ya no existe (DT-45). Hasta corregirlo, la IA del frontend no recibe instrucciones propias: dale tú la directiva GPS.
- **Aviso previo** en el canal del equipo antes de tocar `backend/apps/users/models.py`, `backend/apps/users/migrations/`, `backend/config/settings.py`, `frontend/types/property.ts` o `frontend/app/dashboard/page.tsx`.
- **Migraciones:** hacer pull antes de `makemigrations`. Si dos personas crean `users.0007`, resolver con `makemigrations --merge` y avisar.

### Reglas de mantenimiento (aplican a cada HU futura)
1. Antes de implementar una HU, consultar el contexto maestro, sus criterios de aceptación (Anexo 2) y sus dependencias en el GPS.
2. Antes de modificar un archivo compartido, revisar sus usos (`grep`) y los cambios pendientes (`git status`, PR abiertos).
3. Trabajar en incrementos pequeños y verificables.
4. Registrar qué pruebas se ejecutaron y cuáles pasaron (comando + resultado).
5. Solicitar validación visual y funcional del proceso cuando corresponda.
6. No confundir una implementación escrita con una HU validada.
7. Actualizar el estado de la HU y de sus criterios en `URBANEX_ESTADO_PROCESOS.md`.
8. Actualizar `URBANEX_GPS_ARCHIVOS.md` cuando se creen, modifiquen o eliminen archivos relevantes.
9. Registrar la deuda técnica y las decisiones nuevas en `URBANEX_DEUDA_TECNICA.md`.
10. Recalcular `URBANEX_AVANCE_EPICAS.md` con el método documentado (implementado / verificado / validado).
11. Registrar los bloqueos y las decisiones que necesiten aprobación humana; no resolverlos en silencio.
12. No declarar terminado un paso si depende de una comprobación todavía pendiente.

Si una persona no ha validado visualmente un flujo, la validación queda **Pendiente** y se hace una pregunta concreta. Por ejemplo: "¿Al subir un segundo contrato de corretaje ves v2 y desaparece v1 de la lista vigente?". Si el resultado de las pruebas ya está documentado en la tarea actual, no se vuelve a preguntar; solo se pregunta por la validación que falte.

Al cerrar cada HU, cambiar también la **fecha de auditoría** de los documentos actualizados, para que nadie confunda una instantánea vieja con el estado actual.

## Paso 6. Directiva obligatoria para la IA de Sebas

Instrucciones previas para el asistente:
- Las fuentes de requisitos mandan sobre el código; si se contradicen, documenta la contradicción y pregunta.
- No inventes D-04 ni ninguna otra decisión pendiente.
- Ejecuta las pruebas con etiquetas explícitas (DT-06) y reporta la salida real.

> Esta directiva se complementa con la **DIRECTIVA DE CONTINUIDAD (GPS)** de `PROJECT_PROGRESS.md`, que es obligatoria y prevalece.
>
> Directiva de IA: Antes de escribir código nuevo, lee el URBANEX_MASTER_CONTEXT.md y los 7 documentos en docs/handoff/. Trabaja en pasos pequeños, respeta los archivos ya estabilizados, y antes de avanzar pregúntame siempre: '¿Pasaron las pruebas unitarias y visuales del paso anterior antes de que procedamos a implementar esto?'.
