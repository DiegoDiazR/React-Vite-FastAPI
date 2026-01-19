# Proyecto Plataforma Web – Front-End React + FastAPI
## Stack Tecnológico

### Front-End

* ⚛️ **React 18**
* ⚡ **Vite** (entorno de desarrollo y build rápido)
* 🧠 **TypeScript**
* 🧭 **React Router DOM** (navegación SPA)
* 🗂 **Zustand** (gestión de estado global)
* 🌐 **Axios** (consumo de APIs)
* 🌍 **i18next** (internacionalización)

### Backend (referencia)

* 🚀 **FastAPI** (API REST)
* 🔐 **JWT** para autenticación
* 📦 Respuestas JSON normalizadas

> Nota: Este repositorio no contiene el backend. El frontend se integra mediante contratos HTTP definidos por el backend.

---

## Características Principales

* Arquitectura modular por dominios (`/modules`)
* Autenticación basada en JWT
* Persistencia de sesión en cliente
* Protección de rutas públicas y privadas
* Control básico de permisos (UI-level)
* Manejo centralizado de errores HTTP
* Soporte para múltiples idiomas
* Build de producción optimizado para hosting estático

---

## Estructura del Proyecto

```text
src/
├── app/
│   ├── common/
│   │   ├── core/
│   │   │   ├── adapters/        # Adaptadores de datos (API → Frontend)
│   │   │   ├── interceptors/    # Axios interceptors
│   │   │   ├── services/        # Servicios (Auth, API)
│   │   │   ├── store/           # Zustand stores
│   │   │   └── guards/          # Rutas protegidas
│   │   └── ui/                  # Componentes compartidos
│   ├── modules/                 # Módulos funcionales
│   ├── layouts/                 # Layouts principales
│   ├── routes/                  # Definición de rutas
│   └── utils/                   # Utilidades generales
├── assets/
│   └── i18n/                    # Archivos de idiomas
├── environments/                # Configuración por entorno
└── main.tsx
```

---

## Requisitos del Sistema

### Desarrollo Local

* Node.js **18.x LTS o superior**
* NPM
* Windows, macOS o Linux

### Producción

* Servidor web estático (Nginx, Apache)
* Hosting estático (Vercel, Netlify, AWS S3)
* Acceso HTTPS al backend FastAPI

---

## Configuración del Proyecto

1. Clonar el repositorio:

```bash
git clone <url-del-repositorio>
cd nombre-del-proyecto
```

2. Instalar dependencias:

```bash
npm install
```

3. Configurar variables de entorno:

Crear el archivo correspondiente en `environments/` con la URL del backend, por ejemplo:

```env
VITE_API_BASE_URL=https://api.ejemplo.com
```

4. Ejecutar en modo desarrollo:

```bash
npm run dev
```
1. Instalar el backend local
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
# If requirements.txt doesn't exist, run:
pip install "fastapi[standard]>=0.114.2" python-multipart email-validator "passlib[bcrypt]" tenacity pydantic emails jinja2 alembic httpx "psycopg[binary]" sqlmodel bcrypt==4.3.0 pydantic-settings "sentry-sdk[fastapi]" pyjwt
python -m fastapi dev app/main.py
---

## Autenticación y Seguridad

* Autenticación basada en **JWT**
* Validación de expiración del token en el cliente
* Limpieza automática de sesión cuando el token expira
* Protección de rutas mediante guards

> Importante: la validación final de permisos y reglas de negocio siempre se realiza en el backend.

---

## Manejo de Errores

El sistema implementa manejo centralizado de errores HTTP:

* **401** → Cierre de sesión automático
* **403** → Acceso denegado
* **500** → Error genérico

No se exponen errores técnicos sensibles al usuario final.

---

## Internacionalización (i18n)

* Soporte base para múltiples idiomas
* Archivos JSON por idioma
* Fallback automático

---

## Build y Despliegue

Para generar el build de producción:

```bash
npm run build
```

El resultado se genera en la carpeta `dist/` y puede ser servido desde cualquier servidor web estático.

---

## Alcance del Proyecto

Este proyecto proporciona:

* Base arquitectónica del frontend
* Seguridad base
* Integración con backend
* Documentación técnica

No incluye:

* Diseño UX/UI avanzado
* Pruebas automatizadas
* Soporte post-producción
* Hardening de seguridad avanzado

---
