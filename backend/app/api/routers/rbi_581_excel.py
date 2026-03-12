from __future__ import annotations

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.excel_rbi581 import load_rbi581_excel
from app.schemas.excel_results import ExcelIntakeResult

router = APIRouter(prefix="/rbi581", tags=["Data Load - RBI API 581"])

@router.post("/intake/excel", response_model=ExcelIntakeResult)
async def intake_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Solo se acepta .xlsx o .xlsm")

    content = await file.read()
    return load_rbi581_excel(db, content)

