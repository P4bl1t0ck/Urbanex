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

# How can i run it?:
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

# Requirements:
  --This project was made with:

  --python version: 3.14.16

  --django version: 6.1.1

  --npm: 10.9.8
  
  --pipenv: pipenv, version 2026.7.1
   

