from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

# Imports des modules locaux du package 'backend' (imports relatifs)
from .schemas import Bloc, BlocBase
from .calculs_temporels import verifier_chevauchement, calculer_duree

# --- Initialisation de l'API et Données Simples ---

app = FastAPI(title="API Planificateur Temporel")

# Base de données simulée (remplacée par une BDD réelle plus tard)
db_blocs: List[Bloc] = []
bloc_id_counter = 1

# --- Fonction élémentaire de lecture (CRUD: R) ---

@app.get("/blocs", response_model=List[Bloc])
def lire_blocs():
    """Récupère la liste de tous les blocs enregistrés."""
    return db_blocs

@app.get("/blocs/duree/{bloc_id}", response_model=float)
def lire_duree_bloc(bloc_id: int):
    """Calcule et récupère la durée en heures d'un bloc par son ID."""
    for bloc in db_blocs:
        if bloc.id == bloc_id:
            return calculer_duree(bloc.heure_debut, bloc.heure_fin)
    raise HTTPException(status_code=404, detail="Bloc non trouvé")

# --- Fonction élémentaire de création (CRUD: C) ---

@app.post("/blocs", response_model=Bloc, status_code=201)
def creer_bloc(bloc: BlocBase):
    """Crée un nouveau bloc après vérification de l'heure et du chevauchement."""
    global bloc_id_counter

    # 1. Logique métier modulaire : Vérification du chevauchement
    if verifier_chevauchement(bloc, db_blocs):
        raise HTTPException(
            status_code=400, 
            detail="Le nouveau bloc chevauche un événement existant."
        )

    # 2. Création du bloc avec un ID unique
    nouveau_bloc = Bloc(id=bloc_id_counter, **bloc.model_dump())
    
    # 3. Sauvegarde dans la "base de données"
    db_blocs.append(nouveau_bloc)
    bloc_id_counter += 1
    
    return nouveau_bloc

# --- Fonction élémentaire de mise à jour (CRUD: U) ---

@app.put("/blocs/{bloc_id}", response_model=Bloc)
def modifier_bloc(bloc_id: int, bloc_data: BlocBase):
    """Met à jour un bloc existant par son ID, vérifie le chevauchement."""
    
    # 1. Vérification de l'existence du bloc
    bloc_index = -1
    for i, bloc in enumerate(db_blocs):
        if bloc.id == bloc_id:
            bloc_index = i
            break
            
    if bloc_index == -1:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")

    # 2. Préparation de la vérification de chevauchement
    # Crée une liste de tous les blocs SAUF celui que l'on modifie
    blocs_a_verifier = [b for i, b in enumerate(db_blocs) if i != bloc_index]
    
    # 3. Préparation des données mises à jour
    bloc_actuel = db_blocs[bloc_index]
    
    # Création d'un modèle temporaire pour les vérifications
    champs_a_mettre_a_jour = bloc_data.model_dump(exclude_unset=True)
    temp_bloc = Bloc(id=bloc_id, **bloc_actuel.model_dump(), **champs_a_mettre_a_jour)

    # 4. Logique métier modulaire : Vérification du chevauchement
    if verifier_chevauchement(temp_bloc, blocs_a_verifier):
        raise HTTPException(
            status_code=400, 
            detail="La nouvelle position chevauche un autre bloc."
        )

    # 5. Application de la mise à jour (si validation réussie)
    db_blocs[bloc_index] = temp_bloc
    
    return temp_bloc

# --- Fonction élémentaire de suppression (CRUD: D) ---

@app.delete("/blocs/{bloc_id}", status_code=204)
def supprimer_bloc(bloc_id: int):
    """Supprime un bloc existant par son ID."""
    global db_blocs
    
    bloc_index = -1
    for i, bloc in enumerate(db_blocs):
        if bloc.id == bloc_id:
            bloc_index = i
            break
            
    if bloc_index == -1:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")

    # Suppression du bloc de la liste
    db_blocs.pop(bloc_index)
    
    # Retourne 204 (No Content)
    return