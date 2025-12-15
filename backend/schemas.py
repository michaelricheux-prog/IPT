from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Schéma de base pour les données que l'utilisateur envoie
class BlocBase(BaseModel):
    nom: str = Field(..., description="Nom de l'Opération / Gamme.")

    # NOUVEAUX CHAMPS
    quantite_a_produire: Optional[float] = 0.0
    quantite_produite: Optional[float] = 0.0
    temps_prevu: Optional[float] = None
    temps_passe: Optional[float] = 0.0
    duree_prevue_semaine: Optional[float] = None
    centre_charge_id: Optional[int] = None
    ordre_fabrication_id: Optional[int] = None

    # Champs de Planification existants
    est_realisee: Optional[bool] = False 
    bloc_precedent_id: Optional[int] = None 

# Schéma utilisé pour la CRÉATION d'un bloc (hérite de BlocBase)
class BlocCreate(BlocBase):
    pass

# Schéma utilisé pour la MISE À JOUR d'un bloc (rend les champs optionnels)
class BlocUpdate(BaseModel):
    nom: Optional[str] = None
    quantite_a_produire: Optional[float] = None
    quantite_produite: Optional[float] = None
    temps_prevu: Optional[float] = None
    temps_passe: Optional[float] = None
    duree_prevue_semaine: Optional[float] = None
    centre_charge_id: Optional[int] = None
    ordre_fabrication_id: Optional[int] = None
    est_realisee: Optional[bool] = None
    bloc_precedent_id: Optional[int] = None


# Schéma utilisé pour la LECTURE d'un bloc (données sortantes)
# Il inclut l'ID et configure Pydantic pour lire les données des objets SQLAlchemy
class Bloc(BlocBase):
    id: int
    
    # 🔵 Dates planifiées en sortie
    date_debut_planifiee: Optional[datetime] = None
    date_fin_planifiee: Optional[datetime] = None

    class Config:
        orm_mode = True

