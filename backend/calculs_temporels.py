from datetime import datetime, timedelta
from typing import List

from schemas import BlocBase  # Importation locale (évite l'import relatif quand on exécute le fichier directement)



def calculer_duree(debut: datetime, fin: datetime) -> float:
    """Calcule la durée d'un bloc en heures (float)."""
    duree: timedelta = fin - debut
    return duree.total_seconds() / 3600.0

def verifier_chevauchement(nouveau_bloc: BlocBase, blocs_existants: List[BlocBase]) -> bool:
    """Vérifie si le nouveau bloc chevauche l'un des blocs existants."""
    
    nouveau_start = nouveau_bloc.heure_debut
    nouveau_end = nouveau_bloc.heure_fin
    
    # Vérification simple : la fin d'un bloc doit être après le début de l'autre
    # ET le début d'un bloc doit être avant la fin de l'autre
    for bloc in blocs_existants:
        existant_start = bloc.heure_debut
        existant_end = bloc.heure_fin

        if nouveau_start < existant_end and nouveau_end > existant_start:
            # Chevauchement détecté
            return True
            
    # Aucun chevauchement
    return False