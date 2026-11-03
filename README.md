# Urbanex - Integrated Real Estate Web Plataform 
> **Capstone Project / Graduation Thesis** — Software Engineering  
> **Universidad de Las Américas (UDLA)** — Quito, Ecuador  
> **Academic Term:** 2026
# Project Overview: 
**Urbanex** is an integrated web platform designed for property commercialization, assisted commercial valuation using a Human-in-the-Loop (HITL) parametric engine, and legal document traceability. The system centralizes lead capture, portfolio management, autonomous visit scheduling, and digital legal file custody compliant with Ecuador's Personal Data Protection Law (LOPDP).

*Read this document in [Español](README.es.md).*

# Software Architecture
The platform adopts a **decoupled architecture** evaluated under the **ISO/IEC 25010:2023** software quality framework:
* **Frontend:** Next.js (App Router, React, TypeScript) — Deployed on Vercel.
* **Backend:** Django REST Framework (Python, SimpleJWT, CORS) — Deployed on Render.
* **Database & Storage:** PostgreSQL and Supabase Storage (Private legal files served via time-limited signed URLs).
* **Media Management:** Cloudinary (Property image optimization and delivery).


# Urbanex:
This is our project for our titulation, end of career on
Software Ingeneering, Where we use Django.py and Next.js
as our frameworks.

# Tests & Another Stuff tuff
This project was tested with postman due, its more easy and intuitive

# How can I run it?

### Backend

In PowerShell:

```powershell
cd backend
pipenv install
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}
pipenv run python manage.py migrate
pipenv run python manage.py runserver
```

By default, the backend uses SQLite at `backend\db.sqlite3`. To connect it to Supabase PostgreSQL, configure `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_SSLMODE` in `backend\.env` with the values provided by Supabase. Do not share or commit `.env`.

When switching from SQLite to PostgreSQL, `migrate` creates tables for the implemented models, but does not copy existing records. Data transfer must be done separately; keep a backup of SQLite.

The local backend runs at http://127.0.0.1:8000/.

During development, account activation invitations are printed in the console running Django. To use Resend, set `EMAIL_PROVIDER=resend`, `RESEND_API_KEY`, and `DEFAULT_FROM_EMAIL` to a sender on a verified domain in `backend\.env`. In test mode, Resend only allows sending to the account's authorized email address; do not commit the API key. The link opens `/activate`, is single-use, and expires after 24 hours.

The A-01 user-management screen is at `/dashboard/users` and requires an authenticated `admin` role. HU-44 adds fields and constraints through a migration; review and deliberately apply migrations before using this screen with an existing PostgreSQL database. The migration does not reset or delete records.

### Frontend

In another PowerShell window:

```powershell
cd frontend
npm ci
npm run dev
```

The frontend defaults to the API at `http://127.0.0.1:8000` and runs at http://localhost:3000/.

# Requirements:
  --This project was made with:

  --python version: 3.14.16

  --django version: 6.1.1

  --npm: 10.9.8
  
  --pipenv: pipenv, version 2026.7.1
   
