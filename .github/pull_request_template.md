## Qué cambia

URB-__ / HU-__ — <una o dos frases>. Ficha de tarea: <enlace o "N/A">.

## Código y pruebas
- [ ] Rama desde `develop` actualizado y `git pull origin develop` hecho antes de este PR (conflictos resueltos)
- [ ] Suite completa (Estándares §4): **___ OK** (salida real pegada abajo)
- [ ] `makemigrations --check --dry-run` sin cambios
- [ ] Suite contra PostgreSQL (mayúsculas y tildes, unicidad, longitud, zona horaria DT-01), o "N/A + motivo"
- [ ] Si se tocó el frontend: `npm run build`, `npx tsc --noEmit -p .` y `npx eslint .`
- [ ] Solo se tocaron los archivos de la Fase 0; archivos compartidos avisados y en commit propio

## Archivos prohibidos y credenciales
- [ ] `git diff origin/develop...HEAD --name-only` revisado: sin `backend/db.sqlite3`, `.env`, `backend/media/` ni `backend/private_media/`
- [ ] Sin credenciales reales en código, documentos ni commits
- [ ] Sin migraciones ya fusionadas editadas

## Documentación
- [ ] Project_Progress.md (evidencia, V-xx pendientes y nota de cierre de sesión)
- [ ] Estado de procesos · Avance de épicas · Deuda técnica (DT/FX/DS con IDs de mi rango, buscados en `develop` y en las ramas remotas) · GPS
- [ ] Checklist DoD (Estándares §4) con evidencia o "N/A + motivo"
- [ ] Explicación en lenguaje simple de cada cambio y archivo (backend y frontend)

## Validaciones humanas
V-__ … — **Pendiente** (las marca solo una persona, con quién, fecha, hora, qué vio y la ruta de la captura).

## Auditoría
- [ ] Auditoría de solo lectura en un chat nuevo (prompt de `AGENTS.md` §11): resultado "Apto para PR"

## Evidencia
```
<salida real de las pruebas y de git>
```
