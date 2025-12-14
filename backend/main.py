from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path

# Importations des fichiers locaux pour la BDD et les schémas
from . import models, schemas
from .database import engine, get_db
from .models import Bloc

# ----------------------------------------------------------------------
# CHEMINS ABSOLUS POUR FICHIERS STATIQUES
# ----------------------------------------------------------------------
# Remonte à la racine du projet (du dossier 'backend/' à '/')
BASE_DIR = Path(__file__).resolve().parent.parent 
# ----------------------------------------------------------------------

# Crée les tables dans la base de données (si elles n'existent pas)
models.Base.metadata.create_all(bind=engine)


app = FastAPI()

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "null", 
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Nouvelle fonction pour vérifier les dépendances circulaires
def is_cyclic_dependency(db: Session, bloc_id: int, depend_on_id: int) -> bool:
    """
    Vérifie si la dépendance (bloc_id -> depend_on_id) crée un cycle.
    """
    if bloc_id == depend_on_id:
        return True

    current_id = depend_on_id

    # Parcourir la chaîne de dépendances à partir du bloc prédécesseur
    while current_id is not None:
        db_bloc = db.query(models.Bloc).filter(models.Bloc.id == current_id).first()

        if db_bloc is None:
            return False 

        # Si nous retombons sur le bloc original (bloc_id), il y a un cycle !
        if db_bloc.bloc_precedent_id == bloc_id:
            return True 

        # Passer au bloc précédent dans la chaîne
        current_id = db_bloc.bloc_precedent_id

    return False

# ----------------------------------------------------------------------
# ROUTES D'API (CRUD)
# ----------------------------------------------------------------------

# 1. CRÉER un nouveau bloc (POST)
@app.post("/blocs/", response_model=schemas.Bloc, status_code=status.HTTP_201_CREATED)
def create_bloc(bloc: schemas.BlocCreate, db: Session = Depends(get_db)):

    # Gestion de la Dépendance Circulaire
    if bloc.bloc_precedent_id is not None:
        
        db_bloc = models.Bloc(**bloc.dict())
        db.add(db_bloc)
        db.flush() # Obtient l'ID du nouveau bloc

        if is_cyclic_dependency(db, db_bloc.id, bloc.bloc_precedent_id):
            db.rollback() # Annuler les changements
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dépendance circulaire détectée : Le bloc {bloc.bloc_precedent_id} dépend déjà (directement ou indirectement) de ce nouveau bloc."
            )

        db.commit()
        db.refresh(db_bloc)
        return db_bloc

    # Cas sans dépendance :
    db_bloc = models.Bloc(**bloc.dict())
    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc)
    return db_bloc

# 2. LIRE tous les blocs (GET)
@app.get("/blocs/", response_model=List[schemas.Bloc])
def read_blocs(db: Session = Depends(get_db)):
    """ Récupère la liste complète de tous les blocs. """
    blocs = db.query(models.Bloc).all()
    return blocs

# 3. LIRE un bloc spécifique par ID (GET)
@app.get("/blocs/{bloc_id}", response_model=schemas.Bloc)
def read_bloc(bloc_id: int, db: Session = Depends(get_db)):
    """ Récupère un bloc spécifique basé sur son ID. """
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    
    return db_bloc

# 4. METTRE À JOUR un bloc (PATCH)
@app.patch("/blocs/{bloc_id}", response_model=schemas.Bloc)
def update_bloc(bloc_id: int, bloc: schemas.BlocUpdate, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()

    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")

    update_data = bloc.dict(exclude_unset=True)

    # 1. Gestion de la Dépendance Circulaire
    if 'bloc_precedent_id' in update_data and update_data['bloc_precedent_id'] is not None:
        new_predecessor_id = update_data['bloc_precedent_id']

        if is_cyclic_dependency(db, bloc_id, new_predecessor_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dépendance circulaire détectée : Le bloc {new_predecessor_id} dépend déjà (directement ou indirectement) du bloc {bloc_id}."
            )

    # 2. 🛡️ Validation de l'état du prédécesseur avant de réaliser la tâche
    if 'est_realisee' in update_data and update_data['est_realisee'] is True:

        predecessor_id_to_check = update_data.get('bloc_precedent_id') or db_bloc.bloc_precedent_id

        if predecessor_id_to_check:
            db_predecessor = db.query(models.Bloc).filter(models.Bloc.id == predecessor_id_to_check).first()

            if not db_predecessor:
                raise HTTPException(
                     status_code=status.HTTP_400_BAD_REQUEST,
                     detail=f"Opération précédente (ID {predecessor_id_to_check}) non trouvée."
                   )

            if db_predecessor.est_realisee is False:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"L'opération précédente (ID {predecessor_id_to_check}, Nom: {db_predecessor.nom}) doit être réalisée avant de pouvoir marquer l'opération actuelle comme terminée."
                )

    # 3. 🛡️ Validation des quantités pour la clôture
    if 'est_realisee' in update_data and update_data['est_realisee'] is True:
        
        required_qty = update_data.get('quantite_a_produire') if 'quantite_a_produire' in update_data else db_bloc.quantite_a_produire
        produced_qty = update_data.get('quantite_produite') if 'quantite_produite' in update_data else db_bloc.quantite_produite

        if produced_qty < required_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Impossible de clôre l'opération : Quantité produite ({produced_qty}) inférieure à la quantité requise ({required_qty})."
            )

    # 4. ✅ APPLICATION DES CHANGEMENTS FINALE ET COMMITS
    for key, value in update_data.items():
        setattr(db_bloc, key, value)
        
    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc)
    return db_bloc

# 5. SUPPRIMER un bloc (DELETE)
@app.delete("/blocs/{bloc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bloc(bloc_id: int, db: Session = Depends(get_db)):
    """ Supprime un bloc de la base de données. """
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    
    db.delete(db_bloc)
    db.commit()
    
    return {"ok": True}

# ----------------------------------------------------------------------
# SERVIR LES FICHIERS STATIQUES (FRONTEND)
# ----------------------------------------------------------------------

# 1. Montage du répertoire statique (CSS, JS, images).
# Le chemin est basé sur BASE_DIR pour pointer vers le dossier 'static' à la racine.
app.mount(
    "/static", 
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# 2. Route racine pour servir l'index.html
@app.get("/", include_in_schema=False)
async def serve_index():
    # Le chemin est basé sur BASE_DIR pour pointer vers le fichier 'index.html' à la racine.
    return FileResponse(BASE_DIR / "index.html")