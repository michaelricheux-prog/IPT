
# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse

from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import List, Optional, Literal
from pathlib import Path
from datetime import datetime, timedelta

# --- Imports locaux ---
from . import models, schemas
from .database import engine, get_db

# -------------------------------------------------------------------
# Initialisation de l'application et de la base
# -------------------------------------------------------------------
app = FastAPI()

# Crée les tables si elles n'existent pas (NB: ne gère pas les migrations)
models.Base.metadata.create_all(bind=engine)

# CORS (origines explicites ; évite "*" avec allow_credentials=True)
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "null",  # si index est ouvert via file:// (à éviter ; préfère servir via "/")
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Fichiers statiques & index.html
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # racine: IPT/
STATIC_DIR   = PROJECT_ROOT / "static"
INDEX_FILE   = PROJECT_ROOT / "index.html"

# Logs de diagnostic au démarrage (vérifie que les chemins sont bons)
print(f"[DEBUG] PROJECT_ROOT = {PROJECT_ROOT}")
print(f"[DEBUG] STATIC_DIR   = {STATIC_DIR} (exists={STATIC_DIR.exists()})")
print(f"[DEBUG] INDEX_FILE    = {INDEX_FILE} (exists={INDEX_FILE.exists()})")

# Monte /static -> IPT/static
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Sert l'index (HTML) à la racine
@app.get("/", include_in_schema=False)
def serve_index():
    if not INDEX_FILE.exists():
        return PlainTextResponse(
            f"index.html introuvable à: {INDEX_FILE}\n"
            f"Place index.html à la racine du projet (IPT/).",
            status_code=500,
        )
    return FileResponse(str(INDEX_FILE))

# -------------------------------------------------------------------
# Utilitaires métier
# -------------------------------------------------------------------
def is_cyclic_dependency(db: Session, bloc_id: int, depend_on_id: int) -> bool:
    """
    Détecte un cycle de dépendance (bloc_id -> depend_on_id).
    """
    if bloc_id == depend_on_id:
        return True

    current_id = depend_on_id
    while current_id is not None:
        db_bloc = db.query(models.Bloc).filter(models.Bloc.id == current_id).first()
        if db_bloc is None:
            return False
        if db_bloc.bloc_precedent_id == bloc_id:
            return True
        current_id = db_bloc.bloc_precedent_id
    return False


def _bloc_duree_td(bloc: models.Bloc) -> timedelta:
    """
    Convertit la durée prévue en timedelta.
    - temps_prevu (heures) prioritaire
    - sinon duree_prevue_semaine (semaines -> heures)
    - sinon 0h
    """
    if getattr(bloc, "temps_prevu", None) is not None:
        return timedelta(hours=float(bloc.temps_prevu))
    if getattr(bloc, "duree_prevue_semaine", None) is not None:
        return timedelta(hours=float(bloc.duree_prevue_semaine) * 7.0 * 24.0)
    return timedelta(hours=0)

# -------------------------------------------------------------------
# ROUTES D'API (CRUD Blocs)
# -------------------------------------------------------------------

# 1) CRÉER un bloc
@app.post("/blocs/", response_model=schemas.Bloc, status_code=status.HTTP_201_CREATED)
def create_bloc(bloc: schemas.BlocCreate, db: Session = Depends(get_db)):
    # Gestion de la dépendance circulaire (si un précédent est fourni)
    if bloc.bloc_precedent_id is not None:
        db_bloc = models.Bloc(**bloc.dict())
        db.add(db_bloc)
        db.flush()  # obtention de l'ID du nouveau bloc
        if is_cyclic_dependency(db, db_bloc.id, bloc.bloc_precedent_id):
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Dépendance circulaire détectée : "
                    f"Le bloc {bloc.bloc_precedent_id} dépend déjà (directement ou indirectement) de ce nouveau bloc."
                ),
            )
        db.commit()
        db.refresh(db_bloc)
        return db_bloc

    # Cas sans dépendance
    db_bloc = models.Bloc(**bloc.dict())
    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc)
    return db_bloc


# 2) LIRE tous les blocs (filtrage, tri, pagination)
@app.get("/blocs/", response_model=List[schemas.Bloc], tags=["blocs"])
def read_blocs(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    est_realisee: Optional[bool] = None,
    centre_charge_id: Optional[int] = None,
    ordre_fabrication_id: Optional[int] = None,
    page: int = 1,
    size: int = 20,
    order_by: str = "id",
    order_dir: str = "asc",
):
    """
    Liste paginée des blocs avec filtrage/tri.
    Retourne toujours une LISTE (éventuellement vide).
    """
    # Bornes
    page = max(page, 1)
    size = max(min(size, 100), 1)
    offset = (page - 1) * size

    # Colonnes autorisées pour le tri (sécurité)
    allowed_sorts = {
        "id": models.Bloc.id,
        "nom": models.Bloc.nom,
        "quantite_a_produire": models.Bloc.quantite_a_produire,
        "quantite_produite": models.Bloc.quantite_produite,
        "temps_prevu": models.Bloc.temps_prevu,
        "temps_passe": models.Bloc.temps_passe,
        "duree_prevue_semaine": models.Bloc.duree_prevue_semaine,
        "centre_charge_id": models.Bloc.centre_charge_id,
        "ordre_fabrication_id": models.Bloc.ordre_fabrication_id,
        "est_realisee": models.Bloc.est_realisee,
    }
    sort_col = allowed_sorts.get(order_by, models.Bloc.id)

    # Construction de la requête
    query = db.query(models.Bloc)

    # Filtre texte (nom, case-insensitive compatible SQLite)
    if q:
        query = query.filter(func.lower(models.Bloc.nom).like(f"%{q.lower()}%"))

    # Filtres bool/num
    if est_realisee is not None:
        query = query.filter(models.Bloc.est_realisee == est_realisee)
    if centre_charge_id is not None:
        query = query.filter(models.Bloc.centre_charge_id == centre_charge_id)
    if ordre_fabrication_id is not None:
        query = query.filter(models.Bloc.ordre_fabrication_id == ordre_fabrication_id)

    # Tri
    query = query.order_by(sort_col.desc() if order_dir.lower() == "desc" else sort_col.asc())

    # Pagination
    blocs = query.offset(offset).limit(size).all()
    return blocs  # <- toujours une liste


# 3) LIRE un bloc par ID
@app.get("/blocs/{bloc_id}", response_model=schemas.Bloc, tags=["blocs"])
def read_bloc(bloc_id: int, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    return db_bloc


# 4) METTRE À JOUR un bloc
@app.patch("/blocs/{bloc_id}", response_model=schemas.Bloc, tags=["blocs"])
def update_bloc(bloc_id: int, bloc: schemas.BlocUpdate, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")

    update_data = bloc.dict(exclude_unset=True)

    # 1) Dépendances circulaires
    if "bloc_precedent_id" in update_data and update_data["bloc_precedent_id"] is not None:
        new_predecessor_id = update_data["bloc_precedent_id"]
        if is_cyclic_dependency(db, bloc_id, new_predecessor_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Dépendance circulaire détectée : "
                    f"Le bloc {new_predecessor_id} dépend déjà (directement ou indirectement) du bloc {bloc_id}."
                ),
            )

    # 2) Validation du prédécesseur avant clôture
    if "est_realisee" in update_data and update_data["est_realisee"] is True:
        predecessor_id_to_check = update_data.get("bloc_precedent_id") or db_bloc.bloc_precedent_id
        if predecessor_id_to_check:
            db_predecessor = (
                db.query(models.Bloc).filter(models.Bloc.id == predecessor_id_to_check).first()
            )
            if not db_predecessor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Opération précédente (ID {predecessor_id_to_check}) non trouvée.",
                )
            if db_predecessor.est_realisee is False:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"L'opération précédente (ID {predecessor_id_to_check}, Nom: {db_predecessor.nom}) "
                        f"doit être réalisée avant de pouvoir marquer l'opération actuelle comme terminée."
                    ),
                )

        # 3) Validation des quantités pour la clôture
        required_qty = update_data.get("quantite_a_produire", db_bloc.quantite_a_produire)
        produced_qty = update_data.get("quantite_produite", db_bloc.quantite_produite)
        if produced_qty < required_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Impossible de clôre l'opération : "
                    f"Quantité produite ({produced_qty}) inférieure à la quantité requise ({required_qty})."
                ),
            )

    # 4) Application des changements
    for key, value in update_data.items():
        setattr(db_bloc, key, value)

    db.add(db_bloc)
    db.commit()
    db.refresh(db_bloc)
    return db_bloc


# 5) SUPPRIMER un bloc
@app.delete("/blocs/{bloc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["blocs"])
def delete_bloc(bloc_id: int, db: Session = Depends(get_db)):
    db_bloc = db.query(models.Bloc).filter(models.Bloc.id == bloc_id).first()
    if db_bloc is None:
        raise HTTPException(status_code=404, detail="Bloc non trouvé")
    db.delete(db_bloc)
    db.commit()
    return {"ok": True}

# -------------------------------------------------------------------
# PLANNING (ASAP / RETRO) — optionnel (ne casse pas si colonnes manquantes)
# -------------------------------------------------------------------

@app.post("/planning/run", tags=["planning"])
def run_planning(
    db: Session = Depends(get_db),
    mode: Literal["asap", "retro"] = "asap",
    start_date: Optional[datetime] = Body(default=None),
    due_date: Optional[datetime] = Body(default=None),
):
    """
    Lance la planification :
    - mode='asap': au plus tôt, à partir de start_date (sinon maintenant)
    - mode='retro': au plus tard, à partir de due_date (obligatoire)

    Si les colonnes 'date_debut_planifiee' / 'date_fin_planifiee' n'existent pas
    encore dans le modèle, l'endpoint ne plante pas (il n'écrit pas ces champs).
    """
    blocs = db.query(models.Bloc).all()
    by_id = {b.id: b for b in blocs}

    has_dates = all(
        hasattr(b, "date_debut_planifiee") and hasattr(b, "date_fin_planifiee") for b in blocs
    )

    if mode == "asap":
        base = start_date or datetime.now()
        pending = {b.id for b in blocs if not b.est_realisee}
        guard = 0
        while pending and guard < 10000:
            progressed = False
            for bid in list(pending):
                b = by_id[bid]
                # ES = EF(prédecesseur) ou base
                if b.bloc_precedent_id:
                    pred = by_id.get(b.bloc_precedent_id)
                    if not pred:
                        continue
                    # si dates absentes, impossible de "propager" — on positionne séquentiellement
                    es = getattr(pred, "date_fin_planifiee", None) or base
                else:
                    es = base

                dt = _bloc_duree_td(b)
                if has_dates:
                    b.date_debut_planifiee = es
                    b.date_fin_planifiee = es + dt
                pending.discard(bid)
                progressed = True

            if not progressed:
                break
            guard += 1

        db.commit()
        return {
            "mode": "asap",
            "start_date": base.isoformat(),
            "updated": len(blocs),
            "dates_written": has_dates,
        }

    elif mode == "retro":
        if due_date is None:
            raise HTTPException(status_code=400, detail="due_date est obligatoire pour le mode RETRO.")

        has_next = lambda b: hasattr(b, "blocs_suivants") and len(b.blocs_suivants) > 0

        # Feuilles (sans suivants)
        feuilles = [b for b in blocs if not has_next(b) and not b.est_realisee]
        for b in feuilles:
            dt = _bloc_duree_td(b)
            if has_dates:
                b.date_fin_planifiee = due_date
                b.date_debut_planifiee = due_date - dt

        # Remonter vers les prédécesseurs
        remaining = [b for b in blocs if not b.est_realisee and (not has_dates or b.date_fin_planifiee is None)]
        guard = 0
        while remaining and guard < 10000:
            progressed = False
            for b in list(remaining):
                successors = [s for s in getattr(b, "blocs_suivants", []) if not s.est_realisee]
                # attendre que les suivants soient posés (si dates disponibles)
                if has_dates and any(getattr(s, "date_debut_planifiee", None) is None for s in successors):
                    continue

                lf = None
                if has_dates and successors:
                    lf = min(s.date_debut_planifiee for s in successors if s.date_debut_planifiee is not None)
                elif not successors:
                    # pas de suivants -> déjà traité en feuilles
                    remaining.remove(b)
                    continue

                dt = _bloc_duree_td(b)
                if has_dates and lf is not None:
                    b.date_fin_planifiee = lf
                    b.date_debut_planifiee = lf - dt

                remaining.remove(b)
                progressed = True

            if not progressed:
                break
            guard += 1

        db.commit()
        return {
            "mode": "retro",
            "due_date": due_date.isoformat(),
            "updated": len(blocs),
            "dates_written": has_dates,
        }

    else:
        raise HTTPException(status_code=400, detail="mode doit être 'asap' ou 'retro'")

@app.get("/planning", response_model=List[schemas.Bloc], tags=["planning"])
def get_planning(db: Session = Depends(get_db)):
    """
    Retourne les blocs (les dates planifiées sont présentes si le modèle les expose).
    """
    return db.query(models.Bloc).order_by(models.Bloc.nom).all()

# -------------------------------------------------------------------
# HEALTHCHECK
# -------------------------------------------------------------------
@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

   
