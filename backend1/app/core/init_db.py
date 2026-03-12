from app.core.db import engine
from app.models import asset  # importa TODOS los modelos
from app.models.base import Base
import app.models  # noqa: F401

from app.models.asset import Asset  # si existe y quieres registrarlo
from app.models.rbi581_thinning_result import RBI581ThinningResult
from app.models.rbi581_cof_result import RBI581COFResult
from app.models.rbi581_external_result import RBI581ExternalResult
from app.models.rbi581_external_cracking_result import RBI581ExternalCrackingResult


def init_db():
    Base.metadata.create_all(bind=engine)
