# Urbanex — instrucciones para GitHub Copilot

**Sigue `AGENTS.md` en la raíz del repositorio.** Es la única fuente de reglas: léelo completo y empieza siempre por la Fase 0 (resumir, listar archivos y dudas, y esperar el "ok" humano antes de escribir código).

Las 5 prohibiciones más graves:
1. Nunca push ni merge a `develop` o `master`, ni force push sin aprobación explícita de Pablo.
2. Nunca commitear `backend/db.sqlite3`, `.env`, `backend/media/` ni `backend/private_media/`.
3. Nunca copiar credenciales reales en código, documentos, prompts ni commits; si ves una, avisa y no la repitas.
4. Nunca marcar una validación como aprobada: solo lo hace una persona.
5. Nunca editar fuera del alcance acordado en la Fase 0 ni abrir un PR sin orden.

Si estas líneas y `AGENTS.md` no coinciden, manda `AGENTS.md`.
