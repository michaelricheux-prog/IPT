from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/blocs", tags=["Blocs"])

@router.get("/", response_model=List[schemas.Bloc])
def read_blocs(
    q: Optional[str] = None,
    est_realisee: Optional[bool] = None,
    centre_charge_id: Optional[int] = None,
    ordre_fabrication_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order_by: str = "id",
    order_dir: str = "asc",
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des blocs avec filtres, tri et pagination.
    """
    query = db.query(models.Bloc)

    # --- FILTRES ---
    if q:
        query = query.filter(models.Bloc.nom.contains(q))
    if est_realisee is not None:
        query = query.filter(models.Bloc.est_realisee == est_realisee)
    if centre_charge_id:
        query = query.filter(models.Bloc.centre_charge_id == centre_charge_id)
    if ordre_fabrication_id:
        query = query.filter(models.Bloc.ordre_fabrication_id == ordre_fabrication_id)

    # --- TRI ---
    column = getattr(models.Bloc, order_by, models.Bloc.id)
    if order_dir == "desc":
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    # --- PAGINATION ---
    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()

@router.post("/", response_model=schemas.Bloc)
def create_bloc(bloc: schemas.BlocCreate, db: Session = Depends(get_db)):
    db_bloc = models.Bloc(**bloc.dict())
    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc)
    return db_bloc

@router.patch("/{bloc_id}", response_model=schemas.Bloc)
def update_bloc(bloc_id: int, bloc_update: schemas.BlocUpdate, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    if not db_bloc:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    
    update_data = bloc_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bloc, key, value)
    
    db.commit()
    db.refresh(db_bloc)
    return db_bloc

@router.delete("/{bloc_id}")
def delete_bloc(bloc_id: int, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    if not db_bloc:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    db.delete(db_bloc)
    db.commit()
    return {"message": "Bloc supprimé avec succès"}

@router.get("/{bloc_id}", response_model=schemas.Bloc)
def read_bloc(bloc_id: int, db: Session = Depends(get_db)):
    """
    Récupère un bloc unique par ID
    """
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    if not db_bloc:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    return db_bloc
