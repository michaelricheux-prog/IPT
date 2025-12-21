# backend/app/routers/dt.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..crud import dt as crud
from ...database import get_db

router = APIRouter(prefix="/dts", tags=["DT"])

@router.get("/", response_model=list[schemas.DT])
def read_dts(db: Session = Depends(get_db)):
    # On retourne les DT avec l'article lié
    return db.query(models.DT).all()

@router.get("/{dt_id}", response_model=schemas.DT)
def read_dt(dt_id: int, db: Session = Depends(get_db)):
    db_dt = crud.get_dt(db, dt_id)
    if not db_dt:
        raise HTTPException(status_code=404, detail="DT non trouvé")
    return db_dt

@router.post("/", response_model=schemas.DT)
def create_dt(dt: schemas.DTCreate, db: Session = Depends(get_db)):
    # Vérifie si le code DT existe déjà
    existing = db.query(models.DT).filter(models.DT.DTCode == dt.DTCode).first()
    if existing:
        raise HTTPException(status_code=400, detail="DTCode déjà existant")
    return crud.create_dt(db, dt)

@router.patch("/{dt_id}", response_model=schemas.DT)
def update_dt(dt_id: int, dt: schemas.DTUpdate, db: Session = Depends(get_db)):
    db_dt = crud.update_dt(db, dt_id, dt)
    if not db_dt:
        raise HTTPException(status_code=404, detail="DT non trouvé")
    return db_dt

@router.delete("/{dt_id}")
def delete_dt(dt_id: int, db: Session = Depends(get_db)):
    success = crud.delete_dt(db, dt_id)
    if not success:
        raise HTTPException(status_code=404, detail="DT non trouvé")
    return {"message": "DT supprimée"}
