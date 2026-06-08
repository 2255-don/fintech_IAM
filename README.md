# Fintech-IAM

Projet de gestion de tontine numerique construit selon une approche Spec-Driven avec Django, PostgreSQL et une interface web progressive.

## Demarrage rapide

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
cp .env.example .env
npm run build:css
python manage.py migrate
python manage.py runserver
```

## Documentation

La documentation projet se trouve dans `docs/`.

Documents principaux :
- `docs/DOCUMENTATION_TECHNIQUE_ENRICHIE.md`
- `docs/CONCEPTION_DETAILLEE_PROJET.md`
- `docs/PLAN_REALISATION_PAR_ETAPES.md`
- `docs/etapes/`

## Etat actuel

L'etape 1 met en place :
- l'ossature Django du projet ;
- les applications metier principales ;
- la configuration de base ;
- l'integration initiale de Tailwind CSS ;
- les premiers tests de demarrage ;
- la structure documentaire et logs.

## Base de donnees

La base de donnees officielle du projet est `PostgreSQL`.

Configuration locale attendue :
- `USE_POSTGRES=True`
- `POSTGRES_DB=fintech_iam`
- `POSTGRES_USER=postgres`
- `POSTGRES_PASSWORD=123456`
- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5432`
