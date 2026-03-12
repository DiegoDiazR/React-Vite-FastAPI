from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field

class RowError(BaseModel):
    sheet: str
    row: int
    key: Optional[str] = None
    message: str
    details: Optional[Any] = None

class ExcelIntakeResult(BaseModel):
    inserted_or_updated: int = 0
    failed: int = 0
    errors: list[RowError] = Field(default_factory=list)
