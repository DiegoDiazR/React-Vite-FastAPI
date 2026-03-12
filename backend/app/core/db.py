from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base

# ======================================================
# DATABASE URL
# ======================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./rbi_system.db"

# ======================================================
# ENGINE
# ======================================================
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # SOLO para SQLite
    echo=False,  # pon True si quieres ver SQL en consola
)

# ======================================================
# SESSION
# ======================================================
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

# ======================================================
# DEPENDENCY (FastAPI)
# ======================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
