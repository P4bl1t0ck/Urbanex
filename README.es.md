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

# ¿Comó puedo probarlo?
**--Backend--**
  cd backend/
  
  pipenv install 

  pipenv shell

  cp .env.example .env

  python manage.py migrate

  python manage.py runserver

  Backend server will run at: https://localhost:8000/

**--Frontend--**
  cd frontend
  
  npm install 
  
  cp .env.example .env.local

  npm run dev
  
  Backend server will run at: http://localhost:3000/

# Requisitos:
  --This project was made with:

  --python version: 3.14.16

  --django version: 6.1.1

  --npm: 10.9.8
  
  --pipenv: pipenv, version 2026.7.1
   

