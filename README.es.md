# Urbanex - Plataforma Web Integrada
> **Capstone Projecto / Graduation Thesis** — Ingeniría en Software  
> **Universidad de Las Américas (UDLA)** — Quito, Ecuador   
> **Periodo Académico:** 2026
# Resúmen del Projecto 
**Urbanex** Es una plataforma web integrada diseñada para la comercialización de propiedades, la valoración comercial asistida mediante un motor paramétrico con intervención humana (HITL) y la trazabilidad de documentos legales. El sistema centraliza la captación de clientes potenciales, la gestión de cartera, la programación autónoma de visitas y la custodia digital de expedientes legales, en conformidad con la Ley Orgánica de Protección de Datos Personales (LOPDP) de Ecuador.

# Architectura de Software
La plataforma adopta una **arquitectura desacoplada** evaluada bajo el marco de calidad de software **ISO/IEC 25010:2023**:
* **Frontend:** Next.js (App Router, React, TypeScript) — Implementado en Vercel.
* **Backend:** Django REST Framework (Python, SimpleJWT, CORS) — Implementado en Render.
* **Base de datos y almacenamiento:** PostgreSQL y Supabase Storage (Archivos legales privados servidos a través de URL firmadas con límite de tiempo).
* **Gestión de medios:** Cloudinary (Optimización y entrega de imágenes de propiedades).

# ¿Cómo puedo probarlo?

### Backend

En PowerShell:

```powershell
cd backend
pipenv install
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
pipenv run python manage.py migrate
pipenv run python manage.py runserver
```

Por defecto, el backend usa SQLite en `backend\db.sqlite3`. Para conectarlo a Supabase PostgreSQL, configura en `backend\.env` las variables `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` y `DB_SSLMODE`, usando los datos que proporciona Supabase. No compartas ni subas el archivo `.env`.

Al cambiar de SQLite a PostgreSQL, `migrate` crea las tablas de los modelos implementados, pero no copia los registros existentes. La migración de datos debe hacerse por separado y conservar una copia de seguridad de SQLite.

El backend local estará en http://127.0.0.1:8000/.

En desarrollo, las invitaciones para activar cuentas se imprimen en la consola donde corre Django (backend de correo de consola). El enlace abre `/activate`, es de un solo uso y vence en 24 horas. La integración con un proveedor de correo real se configura aparte.

La gestión A-01 está en `/dashboard/users` y requiere un usuario autenticado con rol `admin`. La migración de HU-44 agrega los campos y restricciones necesarios; antes de usar esa pantalla con una base PostgreSQL existente, revisa y aplica las migraciones de forma deliberada. No restablece ni elimina los registros.

### Frontend

En otra ventana de PowerShell:

```powershell
cd frontend
npm ci
npm run dev
```

El frontend usa por defecto la API en `http://127.0.0.1:8000` y estará en http://localhost:3000/.

# Requisitos:
  --This project was made with:

  --python version: 3.14.16

  --django version: 6.1.1

  --npm: 10.9.8
  
  --pipenv: pipenv, version 2026.7.1
   
