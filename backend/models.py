from sqlalchemy import Column, Integer, String, Float
from .database import Base

# Classe de modèle (représente la table 'blocs' dans la BDD)
class Bloc(Base):
    __tablename__ = "blocs"

    # Colonnes de la table
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    quantite = Column(Float)  # Utilisation de Float pour les quantités décimales
    unite = Column(String) 
    categorie = Column(String) 

    # Note : Nous n'ajoutons pas de relation ici, 
    # car ce modèle représente une simple table indépendante.