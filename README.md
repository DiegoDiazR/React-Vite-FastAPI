# CoreRisk - Industrial Risk Management System

<a href="#" target="_blank"><img src="https://img.shields.io/badge/Status-Development-orange.svg" alt="Status Development"></a>
<a href="#" target="_blank"><img src="https://img.shields.io/badge/Backend-FastAPI-009688.svg" alt="Backend FastAPI"></a>
<a href="#" target="_blank"><img src="https://img.shields.io/badge/Frontend-React-61DAFB.svg" alt="Frontend React"></a>

**CoreRisk** es una plataforma avanzada de gestión y análisis de riesgo industrial diseñada para entornos de alta complejidad. Basado en el estándar **API 581**, el sistema permite la evaluación técnica, el seguimiento de activos y la visualización de datos críticos con una experiencia de usuario moderna y profesional.

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) para el backend API de alto rendimiento.
  - 📊 **Motor de Cálculo Científico** utilizando [Numpy](https://numpy.org/) y [Scipy](https://scipy.org/) para análisis de riesgo preciso.
  - 🔍 [Pydantic](https://docs.pydantic.dev) para validación de datos y esquemas de riesgo.
  - 💾 **SQLite** (rbi_system.db) como base de datos de motor de riesgo integrada.
- 🚀 [React](https://react.dev) para el frontend.
  - 💃 TypeScript, Vite y una arquitectura modular de componentes.
  - 🎨 **Paleta Premium Slate & Indigo** personalizada con [Tailwind CSS](https://tailwindcss.com).
  - 📑 **Ribbon Topbar** Estilo Office para una navegación intuitiva por herramientas.
  - 🌳 **Explorador de Activos** jerárquico (Sitios -> Instalaciones -> Equipos).
- 🐋 [Docker Compose](https://www.docker.com) para despliegue simplificado.
- 🔒 Autenticación segura mediante JWT (JSON Web Token).
- 🔑 Control de acceso por roles y rutas protegidas.
- 📞 [Traefik](https://traefik.io) como proxy inverso y balanceador de carga.
- 🚢 Despliegue listo para producción con certificados HTTPS automáticos.

### Dashboard - CoreRisk Home

[![Dashboard](img/dashboard.png)](#)

### Previsualización de Datos (Estilo Power Query)

CoreRisk incluye una potente herramienta de importación que permite previsualizar y validar archivos Excel antes de su inserción definitiva.

### Vista de Fluidos Genéricos

Gestión centralizada de propiedades químicas y físicas de fluidos industriales con interfaz tabular de alta densidad.

## How To Use It

Puedes clonar este repositorio y empezar a trabajar de inmediato en tu entorno local.

### Requisitos Previos

- [Docker](https://www.docker.com/get-started) y [Docker Compose](https://docs.docker.com/compose/install/).
- Python 3.10+ (opcional para desarrollo local fuera de Docker).

### Instalación Rápida

1. **Clona el repositorio**:
```bash
git clone <url-del-repositorio> corerisk
cd corerisk
```

2. **Configura el entorno**:
Crea un archivo `.env` basado en `.env.example` y actualiza las claves secretas.
```bash
cp .env.example .env
```

3. **Inicia la aplicación con Docker**:
```bash
docker compose up -d --build
```

✨ La aplicación estará disponible en `http://localhost:5173` ✨

## Desarrollo del Backend

El motor de riesgo está optimizado para cálculos pesados. Consulta [backend/README.md](./backend/README.md) para detalles sobre los modelos de la API 581 y la estructura de cálculos.

## Desarrollo del Frontend

La interfaz utiliza un sistema de diseño personalizado para aplicaciones industriales. Consulta [frontend/README.md](./frontend/README.md) para guías sobre componentes y temas.

## Despliegue

Consulta [deployment.md](./deployment.md) para instrucciones sobre cómo desplegar CoreRisk en servidores de producción utilizando Traefik y HTTPS.

## Licencia

CoreRisk se distribuye bajo los términos de la licencia MIT.
