from pydantic import BaseModel, Field
from typing import Optional

# Schéma de base pour les données que l'utilisateur envoie (POST, PUT)
class BlocBase(BaseModel):
    nom: str = Field(..., description="Nom du bloc ou ingrédient.")
    quantite: float = Field(..., description="Quantité du bloc.")
    unite: str = Field(..., description="Unité de mesure (ex: kg, litre, pièce).")
    categorie: str = Field(..., description="Catégorie du bloc (ex: Matière première, Produit Fini).")

# Schéma utilisé pour la CRÉATION d'un bloc (hérite de BlocBase)
class BlocCreate(BlocBase):
    pass

# Schéma utilisé pour la MISE À JOUR d'un bloc (rend les champs optionnels)
class BlocUpdate(BaseModel):
    nom: Optional[str] = None
    quantite: Optional[float] = None
    unite: Optional[str] = None
    categorie: Optional[str] = None


# Schéma utilisé pour la LECTURE d'un bloc (données sortantes)
# Il inclut l'ID et configure Pydantic pour lire les données des objets SQLAlchemy
class Bloc(BlocBase):
    id: int

    class Config:
        # Cette configuration est cruciale ! Elle dit à Pydantic de lire les données
        # des objets ORM (SQLAlchemy) au lieu d'un dictionnaire classique.
        from_attributes = True