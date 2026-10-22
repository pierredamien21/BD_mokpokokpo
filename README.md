# API Ferme Mokpokpo

API REST de gestion d'une exploitation agricole : produits, stocks par lots, commandes, livraisons, alertes de péremption et prévision des ventes. Elle est sécurisée par jeton JWT et chaque rôle a ses propres droits.

## Le problème

Une ferme qui vend des produits périssables doit savoir ce qu'elle a en stock, écouler d'abord ce qui expire en premier et anticiper la demande. Un tableur ne suffit plus dès que plusieurs personnes (vente, stock, livraison) travaillent sur les mêmes données.

## Fonctionnalités

- **Authentification et rôles** : connexion OAuth2 avec jeton JWT, mots de passe hachés, limitation du nombre de requêtes (slowapi). Quatre rôles : `ADMIN`, `GEST_COMMERCIAL`, `GEST_STOCK` et `CLIENT`.
- **Stock par lots en FEFO** (*First Expired, First Out*) : chaque vente prélève d'abord les lots qui périment le plus tôt (`services/fefo_service.py`).
- **Alertes de péremption** : un planificateur (APScheduler) analyse les lots chaque jour à 6 h et classe les alertes par criticité.
- **Commandes, réservations, ventes et livraisons**, avec suppression logique pour garder l'historique.
- **Prévision des ventes** : un modèle `RandomForestRegressor` (scikit-learn) estime les quantités à venir à partir de 15 variables (`/predictions/sales`).
- **Documents PDF** générés avec ReportLab.
- **Base PostgreSQL** décrite en SQL dans `tables_index_tiggers/` : tables, index, triggers, vues, permissions et migrations.

L'API expose 60 routes, documentées automatiquement par FastAPI sur `/docs`.

## Structure

```
main.py              application FastAPI
routers/             une route par ressource (produit, lot, commande, livraison, prediction…)
services/            logique métier : FEFO, alertes, prévision, PDF
security/            JWT, hachage, contrôle d'accès, limitation de débit
models/, schema/     modèles SQLAlchemy et schémas Pydantic
scheduler.py         tâches planifiées (alertes de péremption)
tables_index_tiggers/  SQL de la base
tests/               tests pytest
```

## Installation

Prérequis : Python 3.11 ou plus et une base PostgreSQL.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # renseigner DATABASE_URL et JWT_SECRET_KEY
uvicorn main:app --reload
```

La documentation interactive est ensuite sur http://127.0.0.1:8000/docs.

## Tests

```bash
pip install pytest
pytest
```

Les tests tournent sur une base SQLite en mémoire : ils n'ont pas besoin de PostgreSQL. 20 tests couvrent l'authentification, les droits par rôle, les principaux flux métier et la prévision. Le fichier `README_TESTS_IA.md` décrit les vérifications manuelles de la partie prévision sur le serveur déployé.

## Documentation

- `rapport.md` : routes par ressource, règles FEFO, alertes et diagramme des flux entre rôles.
- `ANALYSE_FAISABILITE_IA.md` : ce qu'il fallait ajouter côté API pour l'écran de prévision du frontend.

## Stack

Python · FastAPI · SQLAlchemy · PostgreSQL · Pydantic · JWT · slowapi · APScheduler · scikit-learn · ReportLab · pytest
