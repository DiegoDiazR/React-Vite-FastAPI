from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from .crud import crud
from .models.base import Base
from .schemas import schema
from .core import db

from app.core.init_db import init_db

# Routers
from app.api.routers.rbi_581_excel import router as rbi_581_excel_router
from app.api.routers.rbi581_thinning import router as thinning_router
from app.api.routers.rbi581_cof import router as cof_router
from app.api.routers.rbi581_external import router as rbi581_external
from app.api.routers.rbi581_externalcracking import router as rbi581_externalcracking_router

# Crear las tablas en la BD (solo para desarrollo rápido, luego usaremos Alembic)
Base.metadata.create_all(bind=db.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (si luego necesitas cerrar pools, etc. va aquí)

app = FastAPI(
    title="RBI Risk Engine (API 581)",
    description="Backend de Evaluación de Riesgo basado en API 581",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Registrar routers
app.include_router(rbi_581_excel_router)
app.include_router(cof_router)
app.include_router(thinning_router)
app.include_router(rbi581_external)
app.include_router(rbi581_externalcracking_router)

