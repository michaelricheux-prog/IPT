from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Importations des fichiers locaux pour la BDD et les schémas
from . import models, schemas
from .database import engine, get_db
from .models import Bloc

# Crée les tables dans la base de données (si elles n'existent pas)
# C'est ce qui génère le fichier sqlite.db au démarrage
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
# Configuration CORS (permet au frontend d'accéder à l'API)
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Ajoutez l'origine "null" pour autoriser l'accès depuis le fichier local index.html
    "null", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------------------------------------------------
# ROUTES D'API (CRUD)
# ----------------------------------------------------------------------

# 1. CRÉER un nouveau bloc (POST)
# Utilise get_db() pour obtenir une session de BDD
@app.post("/blocs/", response_model=schemas.Bloc, status_code=status.HTTP_201_CREATED)
def create_bloc(bloc: schemas.BlocCreate, db: Session = Depends(get_db)):
    """
    Crée un nouveau bloc dans la base de données.
    """
    # Crée une instance du modèle SQLAlchemy à partir des données Pydantic
    db_bloc = models.Bloc(**bloc.model_dump())
    
    # Ajoute l'objet à la session, l'enregistre dans la BDD et rafraîchit l'objet
    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc) # Récupère l'ID généré par la BDD
    
    return db_bloc

# 2. LIRE tous les blocs (GET)
@app.get("/blocs/", response_model=List[schemas.Bloc])
def read_blocs(db: Session = Depends(get_db)):
    """
    Récupère la liste complète de tous les blocs.
    """
    # Interroge la BDD pour obtenir tous les blocs
    blocs = db.query(models.Bloc).all()
    return blocs

# 3. LIRE un bloc spécifique par ID (GET)
@app.get("/blocs/{bloc_id}", response_model=schemas.Bloc)
def read_bloc(bloc_id: int, db: Session = Depends(get_db)):
    """
    Récupère un bloc spécifique basé sur son ID.
    """
    # Interroge la BDD pour obtenir un bloc par ID
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    
    return db_bloc

# 4. METTRE À JOUR un bloc (PATCH)
@app.patch("/blocs/{bloc_id}", response_model=schemas.Bloc)
def update_bloc(bloc_id: int, bloc_update: schemas.BlocUpdate, db: Session = Depends(get_db)):
    """
    Met à jour un ou plusieurs champs d'un bloc existant.
    """
    # 1. Trouver le bloc
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    
    # 2. Mettre à jour les champs (uniquement ceux qui sont fournis)
    # model_dump(exclude_unset=True) exclut les champs qui n'ont pas été fournis dans le body de la requête
    update_data = bloc_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bloc, key, value)
        
    # 3. Enregistrer les changements dans la BDD
    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc)
    
    return db_bloc

# 5. SUPPRIMER un bloc (DELETE)
@app.delete("/blocs/{bloc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bloc(bloc_id: int, db: Session = Depends(get_db)):
    """
    Supprime un bloc de la base de données.
    """
    # 1. Trouver le bloc
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    
    # 2. Supprimer l'objet
    db.delete(db_bloc)
    db.commit()
    
    # 3. Retourner une réponse de succès (204 No Content)
    return {"ok": True}