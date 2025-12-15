from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship 
from .database import Base

# ----------------------------------------------------------------------
# 1. TABLE D'ASSOCIATION (M:N) : Opération <-> Composant
# ----------------------------------------------------------------------
class AssociationComposantOperation(Base):
    __tablename__ = "association_composant_operation"

    # Clés étrangères vers les tables 'blocs' et 'composants'
    operation_id = Column(Integer, ForeignKey('blocs.id'), primary_key=True)
    composant_id = Column(Integer, ForeignKey('composants.id'), primary_key=True)

    # Champ spécifique à la relation
    quantite_requise = Column(Float, nullable=False) 

    # Relations définies plus tard
    operation = relationship("Bloc", back_populates="composants_requis")
    composant = relationship("Composant", back_populates="operations_assoc")


# ----------------------------------------------------------------------
# 2. MODÈLE COMPOSANT (Inventaire / Stock)
# ----------------------------------------------------------------------
class Composant(Base):
    __tablename__ = "composants"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True, unique=True)
    quantite_disponible = Column(Float)
    unite = Column(String)
    description = Column(String, nullable=True)

    # Relation vers la table d'association (par chaîne de caractères)
    operations_assoc = relationship(
        "AssociationComposantOperation", 
        back_populates="composant",
        cascade="all, delete-orphan"
    )


# ----------------------------------------------------------------------
# 3. MODÈLE BLOC (Opération) - Mise à jour et Complète
# ----------------------------------------------------------------------
class Bloc(Base):
    __tablename__ = "blocs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True) # Nom de l'Opération / Article

    # CHAMPS DE SUIVI ET CHARGE
    quantite_a_produire = Column(Float, default=0.0)
    quantite_produite = Column(Float, default=0.0)
    temps_prevu = Column(Float, nullable=True)
    temps_passe = Column(Float, default=0.0)
    duree_prevue_semaine = Column(Float, nullable=True)
    centre_charge_id = Column(Integer, nullable=True)
    ordre_fabrication_id = Column(Integer, nullable=True)

    # CHAMPS DE PLANIFICATION
    est_realisee = Column(Boolean, default=False)

    # 🔵 Nouvelles dates planifiées
    date_debut_planifiee = Column(DateTime, nullable=True)
    date_fin_planifiee   = Column(DateTime, nullable=True)

    # Dépendance sur un autre Bloc
    bloc_precedent_id = Column(Integer, ForeignKey('blocs.id'), nullable=True) 

    # Relation réflexive (par chaîne de caractères)
    bloc_precedent = relationship(
        'Bloc', 
        remote_side=[id], 
        uselist=False,
        backref="blocs_suivants"
    )

    # Relation pour les composants requis (par chaîne de caractères)
    composants_requis = relationship(
        "AssociationComposantOperation", 
        back_populates="operation", 
        cascade="all, delete-orphan" 
    )