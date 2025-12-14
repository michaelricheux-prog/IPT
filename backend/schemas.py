from datetime import datetime
from pydantic import BaseModel, Field

# --- Schéma de Base (pour la création et la mise à jour) ---

class BlocBase(BaseModel):
    """Schéma de base représentant les données d'un bloc sans l'ID."""
    
    titre: str = Field(None, description="Titre du bloc d'événement")
    
    heure_debut: datetime = Field(
        ..., 
        description="Heure de début du bloc (format ISO 8601)",
        examples=["2025-12-15T09:00:00"]
    )
    heure_fin: datetime = Field(
        ..., 
        description="Heure de fin du bloc (format ISO 8601)",
        examples=["2025-12-15T11:00:00"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "titre": "Réunion Projet IPT",
                "heure_debut": "2025-12-15T14:00:00",
                "heure_fin": "2025-12-15T16:00:00"
            }
        }

# --- Schéma Complet (pour la lecture) ---

class Bloc(BlocBase):
    """Schéma complet d'un bloc, incluant l'ID généré automatiquement."""
    id: int = Field(..., description="ID unique du bloc")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "titre": "Développement API FastAPI",
                "heure_debut": "2025-12-15T09:00:00",
                "heure_fin": "2025-12-15T11:00:00"
            }
        }