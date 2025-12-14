import sys
import os
from datetime import datetime

# Ajouter le répertoire courant (backend/) au sys.path pour permettre
# d'importer directement les modules locaux quand on exécute
# `python backend\test.py` depuis la racine du projet.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importations locales (sans import relatif, pour que le script puisse
# être exécuté directement en tant que fichier). Note: le module s'appelle
# `shemas.py` dans le dossier, d'où l'import ci-dessous.
from calculs_temporels import calculer_duree
from schemas import BlocBase

# Exemple d'utilisation du module calculs_temporels
def test_calcul_duree_simple():
    """Test unitaire pour vérifier le calcul de la durée."""
    # 09:00 à 11:00 donne 2.0 heures
    debut = datetime(2025, 12, 15, 9, 0, 0)
    fin = datetime(2025, 12, 15, 11, 0, 0)
    
    duree = calculer_duree(debut, fin)
    
    # Validation du résultat
    assert duree == 2.0
    print(f"Test 1 de durée OK: {duree} heures")

# Exécution du test (temporaire)
if __name__ == "__main__":
    test_calcul_duree_simple()