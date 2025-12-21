sur l'architecture modulaire suivante:
frontend/
├─ index.html
├─ js/
│  ├─ main.js       # initialisation globale
│  ├─ articles.js   # module Article
│  ├─ dt.js         # module DT
│  └─ cdc.js        # module CDC
backend/
├─ app/
│  ├─ main.py            # FastAPI app
│  ├─ models.py          # SQLAlchemy models
│  ├─ schemas.py         # Pydantic schemas
│  ├─ crud/
│  │  ├─ __init__.py
│  │  ├─ articles.py
│  │  ├─ cdc.py
│  │  ├─ dt.py
│  │  ├─ opedt.py
│  │  ├─ of.py
│  │  └─ opeof.py
│  └─ routers/
│     ├─ __init__.py
│     ├─ articles.py
│     ├─ cdc.py
│     ├─ dt.py
│     ├─ opedt.py
│     ├─ of.py
│     └─ opeof.py
└─ database.py
je veux faire une application simple de type POC pour gérer:

ARTICLE:
- ArticleCode ==> FAIT
- Articledesignation ==> FAIT
+ Fonctions: Créer/editer/supprimer ==> FAIT

CDC (centre de charge):
- CdcCode
- CdcName
- Capacité (heures)
+ Fonctions: Créer/editer/supprimer

DT:
- DTcode ==> FAIT
- ArticleCode (depuis la classe article) ==> FAIT
+ Fonctions: Créer/editer/supprimer ==> FAIT

OPEDT:
- DTCode (depuis la classe DT)
- OpeDescription
- OpeOrder (unique)
- CdcCode (depuis la classe centre de charge)
- charge (en heures)
- durée (en semaine)
+ Fonctions: Créer/editer/supprimer

OF:
- OFcode
- DTCode (depuis la classe DT)
- StartDate (Calculé en fonction des autres paramètres)
- EndDate (Calculé en fonction des autres paramètres)
- ASAP/RETRO (au plus tôt ou au plus tard)
+ Fonctions: Créer/editer/supprimer
+ Fonctions: Générer OF à partir d'une DT
+ Fonction: Ajouter une OPE dans OF

OPEOF:
- OpeNumber
- OpeDescription (depuis la classe OpeDT)
- CdcCode (depuis la classe centre de charge)
- OpeOrder (unique)
- charge (en heures)
- durée (en semaine)
- StartDate (Calculé en fonction des autres paramètres)
- EndDate (Calculé en fonction des autres paramètres)
- ASAP/RETRO (au plus tôt ou au plus tard)
+ Fonctions: Créer/editer/supprimer

PLANOPE: (Planning des opérations servant à alimenter le gantt)
- OpeNumber (depuis la classe OPEOF)

PLANCHARGE: (Plan de charge calculé)

