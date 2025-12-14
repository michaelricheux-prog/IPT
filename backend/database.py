from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de données SQLite. 
# Le fichier 'sqlite.db' sera créé à la racine du projet (là où se trouve main.py).
SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

# Le moteur est responsable de la communication avec la base de données.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # 'check_same_thread' est nécessaire uniquement pour SQLite.
    # Il permet à plusieurs threads de communiquer avec la base de données.
    connect_args={"check_same_thread": False}
)

# SessionLocal est la classe de session. Chaque fois que nous interagissons avec la BDD,
# nous allons créer une instance de cette session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base est la classe de base à partir de laquelle tous les modèles de BDD (tables) hériteront.
Base = declarative_base()

# Fonction pour obtenir une session de BDD (utilisée par FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()