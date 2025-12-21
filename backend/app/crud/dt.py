from sqlalchemy.orm import Session
from .. import models, schemas

def get_dts(db: Session):
    return db.query(models.DT).all()

def get_dt(db: Session, dt_id: int):
    return db.query(models.DT).filter(models.DT.id == dt_id).first()

def create_dt(db: Session, dt: schemas.DTCreate):
    db_dt = models.DT(**dt.dict())
    db.add(db_dt)
    db.commit()
    db.refresh(db_dt)
    return db_dt

def update_dt(db: Session, dt_id: int, dt: schemas.DTUpdate):
    db_dt = get_dt(db, dt_id)
    if not db_dt:
        return None
    for key, value in dt.dict(exclude_unset=True).items():
        setattr(db_dt, key, value)
    db.commit()
    db.refresh(db_dt)
    return db_dt

def delete_dt(db: Session, dt_id: int):
    db_dt = get_dt(db, dt_id)
    if not db_dt:
        return None
    db.delete(db_dt)
    db.commit()
    return True
