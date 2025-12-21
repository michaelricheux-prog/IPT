# backend/app/crud/cdc.py
from sqlalchemy.orm import Session
from .. import models, schemas

def get_cdcs(db: Session):
    return db.query(models.cdc).all()

def get_cdc(db: Session, cdc_id: int):
    return db.query(models.cdc).filter(models.cdc.id == cdc_id).first()

def create_cdc(db: Session, cdc: schemas.cdcCreate):
    db_cdc = models.cdc(**cdc.dict())
    db.add(db_cdc)
    db.commit()
    db.refresh(db_cdc)
    return db_cdc

def update_cdc(db: Session, cdc_id: int, cdc: schemas.cdcCreate):
    db_cdc = get_cdc(db, cdc_id)
    if not db_cdc:
        return None
    for key, value in cdc.dict().items():
        setattr(db_cdc, key, value)
    db.commit()
    db.refresh(db_cdc)
    return db_cdc

def delete_cdc(db: Session, cdc_id: int):
    db_cdc = get_cdc(db, cdc_id)
    if not db_cdc:
        return None
    db.delete(db_cdc)
    db.commit()
    return True
