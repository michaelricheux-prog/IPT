import pandas as pd
import io
from sqlalchemy.orm import Session
from .. import models

def export_blocs_to_excel(db: Session):
    # Récupérer les données de la DB
    blocs = db.query(models.Bloc).all()
    
    # Transformer en liste de dictionnaires
    data = []
    for b in blocs:
        data.append({
            "ID": b.id,
            "Nom": b.nom,
            "Quantité à produire": b.quantite_a_produire,
            "Quantité produite": b.quantite_produite,
            "Temps prévu (h)": b.temps_prevu,
            "Réalisé": "Oui" if b.est_realisee else "Non"
        })
    
    df = pd.DataFrame(data)
    
    # Créer un flux mémoire pour le fichier Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Blocs')
    
    return output.getvalue()

def import_blocs_from_excel(db: Session, file_content: bytes):
    # Lire le fichier Excel depuis les bytes
    df = pd.read_excel(io.BytesIO(file_content))
    
    # Pour chaque ligne, créer ou mettre à jour un bloc
    for _, row in df.iterrows():
        # Exemple de mapping (à adapter selon vos colonnes Excel)
        new_bloc = models.Bloc(
            nom=str(row.get("Nom", "Sans nom")),
            quantite_a_produire=row.get("Quantité à produire", 0),
            temps_prevu=row.get("Temps prévu (h)", 0),
            est_realisee=False
        )
        db.add(new_bloc)
    
    db.commit()
    return len(df)

def export_blocs_to_csv(db: Session):
    blocs = db.query(models.Bloc).all()
    
    data = []
    for b in blocs:
        data.append({
            "id": b.id,
            "nom": b.nom,
            "quantite": b.quantite_a_produire,
            "temps": b.temps_prevu,
            "realise": b.est_realisee
        })
    
    df = pd.DataFrame(data)
    # On retourne le CSV sous forme de chaîne de caractères (utf-8)
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig')

def import_blocs_from_csv(db: Session, file_content: bytes):
    # On décode les bytes en texte. 'utf-8-sig' gère les fichiers Excel/CSV français avec accents
    text_data = file_content.decode('utf-8-sig')
    
    # On lit le CSV. sep=None avec engine='python' permet de détecter automatiquement ; ou ,
    df = pd.read_csv(io.StringIO(text_data), sep=None, engine='python')
    
    count = 0
    for _, row in df.iterrows():
        new_bloc = models.Bloc(
            nom=str(row.get("nom", "Sans nom")),
            quantite_a_produire=int(row.get("quantite", 0)),
            temps_prevu=float(row.get("temps", 0)),
            est_realisee=False
        )
        db.add(new_bloc)
        count += 1
    
    db.commit()
    return count