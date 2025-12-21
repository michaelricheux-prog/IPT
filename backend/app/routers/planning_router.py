from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from ..database import get_db
from ..services import planning_service

router = APIRouter(prefix="/planning", tags=["Planning"])

@router.post("/run")
async def run_planning_calculation(
    mode: str = Query("asap", description="Mode de calcul : 'asap' ou 'retro'"),
    db: Session = Depends(get_db),
    # On utilise un corps de requête (Body) pour les dates
    # car les dates en Query String peuvent poser des problèmes de format
    payload: dict = {}
):
    """
    Déclenche le calcul de la planification.
    - ASAP : Nécessite 'start_date' (optionnel, sinon datetime.now())
    - RETRO : Nécessite 'due_date' (obligatoire)
    """
    try:
        if mode == "asap":
            # Extraction de la date de début du payload
            start_raw = payload.get("start_date")
            start_dt = None
            if start_raw:
                # Conversion du format ISO envoyé par le JS vers datetime Python
                start_dt = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            
            count = planning_service.run_asap_planning(db, start_dt)
            return {
                "status": "success", 
                "message": f"Calcul ASAP terminé : {count} opérations planifiées."
            }

        elif mode == "retro":
            due_raw = payload.get("due_date")
            if not due_raw:
                raise HTTPException(
                    status_code=400, 
                    detail="La date d'échéance (due_date) est requise pour le mode RETRO."
                )
            
            due_dt = datetime.fromisoformat(due_raw.replace("Z", "+00:00"))
            # count = planning_service.run_retro_planning(db, due_dt)
            return {
                "status": "warning", 
                "message": "Le mode RETRO est en cours de développement."
            }

        else:
            raise HTTPException(status_code=400, detail="Mode de planification non reconnu.")

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Format de date invalide : {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

@router.get("/status")
def get_planning_status(db: Session = Depends(get_db)):
    """
    Retourne des statistiques simples sur le planning actuel.
    """
    from ..models import Bloc
    total = db.query(Bloc).count()
    planned = db.query(Bloc).filter(Bloc.date_debut_planifiee != None).count()
    realized = db.query(Bloc).filter(Bloc.est_realisee == True).count()
    
    return {
        "total_operations": total,
        "operations_planifiees": planned,
        "operations_terminees": realized,
        "taux_avancement": (realized / total * 100) if total > 0 else 0
    }