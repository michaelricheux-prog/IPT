from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .. import models

def run_asap_planning(db: Session, start_date: datetime = None):
    """
    Calcule les dates au plus tôt (ASAP) en respectant :
    1. Les dépendances (bloc précédent)
    2. La disponibilité des machines (Centre de Charge)
    """
    if not start_date:
        start_date = datetime.now()

    # Récupérer tous les blocs non réalisés
    blocs = db.query(models.Bloc).filter(models.Bloc.est_realisee == False).all()
    
    # On vide les dates actuelles pour repartir de zéro
    for b in blocs:
        b.date_debut_planifiee = None
        b.date_fin_planifiee = None

    planned_ids = {}      # {bloc_id: date_fin}
    machine_free_at = {}  # {machine_id: date_prochaine_dispo}

    # Liste de travail
    pending = list(blocs)
    
    # Sécurité pour éviter les boucles infinies (dépendances circulaires)
    max_iterations = len(pending) * 2
    iterations = 0

    while pending and iterations < max_iterations:
        iterations += 1
        for b in pending[:]:
            # Vérifier si le prédécesseur est prêt
            can_start = True
            predecessor_finish_date = start_date

            if b.bloc_precedent_id:
                if b.bloc_precedent_id in planned_ids:
                    predecessor_finish_date = planned_ids[b.bloc_precedent_id]
                else:
                    can_start = False # Le parent n'est pas encore planifié

            if can_start:
                # 1. Date de début potentielle (max entre début projet et fin du parent)
                debut_theorique = predecessor_finish_date

                # 2. Prendre en compte la machine (Centre de Charge)
                # Si la machine est déjà occupée, on commence après la fin du bloc précédent sur cette machine
                if b.centre_charge_id:
                    m_id = b.centre_charge_id
                    if m_id in machine_free_at:
                        debut_theorique = max(debut_theorique, machine_free_at[m_id])

                # 3. Calcul de la fin
                # On utilise temps_prevu (en heures)
                duree_h = b.temps_prevu if b.temps_prevu else 0
                
                # Optionnel : si vous avez une quantité, on multiplie
                # duree_h = (b.temps_prevu * b.quantite_a_produire) 

                fin_theorique = debut_theorique + timedelta(hours=duree_h)

                # 4. Enregistrement
                b.date_debut_planifiee = debut_theorique
                b.date_fin_planifiee = fin_theorique

                # Mise à jour des index de suivi
                planned_ids[b.id] = fin_theorique
                if b.centre_charge_id:
                    machine_free_at[b.centre_charge_id] = fin_theorique
                
                pending.remove(b)

    db.commit()
    return len(planned_ids)

def run_retro_planning(db: Session, due_date: datetime):
    """
    Calcule les dates au plus tard (RETRO) à partir d'une date de livraison.
    Logique inverse de l'ASAP.
    """
    # À implémenter selon le même principe mais en remontant la chaîne
    pass