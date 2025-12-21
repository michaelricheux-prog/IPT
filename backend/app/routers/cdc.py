# backend/app/routers/cdc.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import cdc as crud
from ...database import get_db

router = APIRouter(prefix="/cdcs", tags=["cdc"])

@router.get("/", response_model=list[schemas.cdc])
def read_cdcs(db: Session = Depends(get_db)):
    return crud.get_cdcs(db)

@router.get("/{cdc_id}", response_model=schemas.cdc)
def read_cdc(cdc_id: int, db: Session = Depends(get_db)):
    db_cdc = crud.get_cdc(db, cdc_id)
    if not db_cdc:
        raise HTTPException(status_code=404, detail="cdc non trouvé")
    return db_cdc

@router.post("/", response_model=schemas.cdc)
def create_cdc(cdc: schemas.cdcCreate, db: Session = Depends(get_db)):
    return crud.create_cdc(db, cdc)

@router.patch("/{cdc_id}", response_model=schemas.cdc)
def update_cdc(cdc_id: int, cdc: schemas.cdcCreate, db: Session = Depends(get_db)):
    db_cdc = crud.update_cdc(db, cdc_id, cdc)
    if not db_cdc:
        raise HTTPException(status_code=404, detail="cdc non trouvé")
    return db_cdc

@router.delete("/{cdc_id}")
def delete_cdc(cdc_id: int, db: Session = Depends(get_db)):
    success = crud.delete_cdc(db, cdc_id)
    if not success:
        raise HTTPException(status_code=404, detail="cdc non trouvé")
    return {"message": "cdc supprimé"}
