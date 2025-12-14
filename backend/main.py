from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

# Middleware CORS : autorise les requêtes depuis le frontend (adapter allow_origins en prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # <-- changer pour autoriser uniquement vos domaines en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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


# Nouvelle fonction pour vérifier les dépendances circulaires
def is_cyclic_dependency(db: Session, bloc_id: int, depend_on_id: int) -> bool:
    """
    Vérifie si la dépendance (bloc_id -> depend_on_id) crée un cycle.
    """
    if bloc_id == depend_on_id:
        # Un bloc ne peut pas dépendre de lui-même
        return True

    current_id = depend_on_id

    # Parcourir la chaîne de dépendances à partir du bloc prédécesseur
    while current_id is not None:
        # Trouver l'objet bloc dans la BDD
        db_bloc = db.query(models.Bloc).filter(models.Bloc.id == current_id).first()

        if db_bloc is None:
            # La dépendance pointe vers un bloc inexistant (ce n'est pas un cycle, mais c'est une erreur que nous pourrions gérer plus tard)
            return False 

        # Si nous retombons sur le bloc original, il y a un cycle !
        if db_bloc.bloc_precedent_id == bloc_id:
            return True 

        # Passer au bloc précédent dans la chaîne
        current_id = db_bloc.bloc_precedent_id

    return False # Aucune boucle détectée

# ----------------------------------------------------------------------
# ROUTES D'API (CRUD)
# ----------------------------------------------------------------------

# 1. CRÉER un nouveau bloc (POST)
# Utilise get_db() pour obtenir une session de BDD
@app.post("/blocs/", response_model=schemas.Bloc, status_code=status.HTTP_201_CREATED)
def create_bloc(bloc: schemas.BlocCreate, db: Session = Depends(get_db)):

    # 1. Gestion de la Dépendance Circulaire
    if bloc.bloc_precedent_id is not None:

        # Nous devons d'abord créer le bloc pour obtenir son ID
        # HACK: Pour la création, nous utilisons temporairement une vérification simple sur l'ID du prédécesseur,
        # car nous n'avons pas encore l'ID du nouveau bloc. 
        # Pour la VRAIE robustesse, cette logique devrait être déplacée dans un service.

        db_bloc = models.Bloc(**bloc.dict())
        db.add(db_bloc)
        db.flush() # Flusher donne l'ID au db_bloc SANS commiter

        if is_cyclic_dependency(db, db_bloc.id, bloc.bloc_precedent_id):
            db.rollback() # Annuler les changements
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dépendance circulaire détectée : Le bloc {bloc.bloc_precedent_id} dépend déjà (directement ou indirectement) de ce nouveau bloc."
            )

        db.commit() # Si tout est bon, on commite
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
def update_bloc(bloc_id: int, bloc: schemas.BlocUpdate, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()

    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")

    update_data = bloc.dict(exclude_unset=True)

    # 1. Gestion de la Dépendance Circulaire LORS DE LA MODIFICATION
    if 'bloc_precedent_id' in update_data and update_data['bloc_precedent_id'] is not None:
        new_predecessor_id = update_data['bloc_precedent_id']

        if is_cyclic_dependency(db, bloc_id, new_predecessor_id):
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dépendance circulaire détectée : Le bloc {new_predecessor_id} dépend déjà (directement ou indirectement) du bloc {bloc_id}."
            )

    # 2. Application des changements si pas de cycle
    for key, value in update_data.items():
        setattr(db_bloc, key, value)

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



