import sqlite3
import os

DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sqlite.db')

if not os.path.exists(DB):
    print('Fichier sqlite.db introuvable à :', DB)
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("PRAGMA table_info('blocs')")
cols = cur.fetchall()
col_names = [c[1] for c in cols]
print('Colonnes actuelles:', col_names)

if 'est_realisee' not in col_names:
    print('Ajout de la colonne est_realisee')
    cur.execute("ALTER TABLE blocs ADD COLUMN est_realisee INTEGER DEFAULT 0")
else:
    print('est_realisee existe déjà')

if 'bloc_precedent_id' not in col_names:
    print('Ajout de la colonne bloc_precedent_id')
    cur.execute("ALTER TABLE blocs ADD COLUMN bloc_precedent_id INTEGER")
else:
    print('bloc_precedent_id existe déjà')

conn.commit()
cur.execute("PRAGMA table_info('blocs')")
print('Colonnes après modification:', [c[1] for c in cur.fetchall()])
conn.close()
print('Mise à jour du schéma terminée.')
