# ETAPE 01 - CADRAGE ET OSSATURE

## 1. Objectif de l'etape
Mettre en place une base technique propre, documentee et testable pour lancer les prochaines etapes du projet Fintech-IAM.

## 2. Perimetre traite
Cette etape couvre :
- l'initialisation du projet Django ;
- la creation de l'environnement virtuel local ;
- l'installation des dependances initiales ;
- l'installation et la configuration initiale de Tailwind CSS ;
- la creation de la structure principale du projet ;
- l'ajout des apps de base ;
- la configuration initiale du projet ;
- la preparation du systeme de logs ;
- la mise en place d'une route d'accueil et d'un healthcheck ;
- l'ajout des premiers tests smoke ;
- la documentation de l'etape.

## 3. Decisions prises
- le projet est initialise avec `Django 6.0.6` ;
- les dependances Python sont isolees dans `.venv/` ;
- une configuration par variables d'environnement est mise en place ;
- `PostgreSQL` est la base officielle du projet ;
- un fallback `SQLite` reste seulement present dans le code comme solution technique locale de secours, pas comme base de reference ;
- les apps metier sont creees des l'etape 1 pour figer l'ossature ;
- Tailwind CSS est integre des l'etape 1 pour rester coherent avec la stack officielle ;
- un dossier `logs/` est prepare avec configuration logging des le depart.

## 4. Fichiers crees
- `manage.py`
- `config/__init__.py`
- `config/asgi.py`
- `config/settings.py`
- `config/urls.py`
- `config/wsgi.py`
- `apps/__init__.py`
- `apps/core/*`
- `apps/accounts/*`
- `apps/agents/*`
- `apps/clients/*`
- `apps/cycles/*`
- `apps/transactions/*`
- `logs/app.log`
- `logs/error.log`
- `logs/security.log`
- `theme/static_src/input.css`
- `static/css/tailwind.css`
- `templates/base.html`
- `templates/core/home.html`
- `requirements.txt`
- `.env.example`
- `pytest.ini`
- `README.md`
- `.gitignore`

## 5. Fichiers modifies
- `docs/` avec ajout du document d'etape ;
- fichiers `apps.py` des apps generees pour corriger leur namespace ;
- `apps/core/views.py`
- `apps/core/urls.py`
- `apps/core/tests.py`
- `config/settings.py`
- `config/urls.py`
- `package.json`
- `.gitignore`
- `README.md`
- `templates/base.html`
- `templates/core/home.html`

## 6. Elements techniques ajoutes

### 6.1 Ossature Django
- creation du projet Django central ;
- creation des apps `core`, `accounts`, `agents`, `clients`, `cycles`, `transactions`.

### 6.2 Configuration initiale
- chargement des variables d'environnement via `python-dotenv` ;
- configuration principale pour `PostgreSQL` via variables d'environnement ;
- fallback `SQLite` garde uniquement comme solution de secours locale ;
- configuration des templates globaux ;
- configuration des fichiers statiques et media ;
- configuration initiale du logging.

### 6.3 App core
- route `home` pour verifier que le projet repond ;
- route `healthcheck` pour verifier rapidement l'etat applicatif ;
- template de base minimal.

### 6.4 Qualite projet
- `requirements.txt` ;
- `pytest.ini` ;
- `.gitignore` ;
- `README.md` ;
- documentation d'etape.

### 6.5 Integration Tailwind CSS
- installation des dependances frontend `tailwindcss` et `@tailwindcss/cli` ;
- creation d'un fichier source CSS unique dans `theme/static_src/input.css` ;
- creation d'un build de sortie dans `static/css/tailwind.css` ;
- ajout de scripts `npm` pour compiler et surveiller le CSS ;
- branchement de Tailwind dans le layout global Django ;
- premiere mise en forme de la page d'accueil pour verifier l'integration.

## 7. Pourquoi ces elements ont ete crees
- `config/settings.py` : centraliser une configuration propre des le depart.
- `apps/*` : figer l'organisation technique avant le metier.
- `templates/base.html` : fournir un point de depart commun pour les prochaines interfaces.
- `home` : disposer d'une page de verification de base.
- `healthcheck` : disposer d'un point de controle simple pour les tests et la validation technique.
- `requirements.txt` : rendre l'installation reproductible.
- `.env.example` : encadrer la configuration locale.
- `.env` : activer la configuration locale reelle sur PostgreSQL.
- `pytest.ini` : preparer l'execution des tests des maintenant.
- `logs/` et logging : poser la base de l'observabilite des l'etape 1.
- `theme/static_src/input.css` : centraliser la source Tailwind du projet.
- `static/css/tailwind.css` : fournir la feuille CSS compilee servie par Django.
- `package.json` : declarer les dependances frontend et scripts de build CSS.
- `templates/base.html` : charger le CSS compile et preparer les prochaines interfaces.

## 8. Regles metier couvertes
Cette etape couvre surtout les regles de realisation et d'architecture, pas encore les regles metier financieres.

Regles indirectement soutenues :
- centralisation de l'architecture ;
- preparation a la separation `Admin` / `Agent` ;
- preparation du systeme de logs ;
- alignement de la stack reelle avec la documentation technique officielle ;
- preparation d'un projet sans dette technique initiale inutile.

## 9. Tests ajoutes
- test de disponibilite de la page d'accueil ;
- test de reponse du healthcheck.

## 10. Resultat des tests
Commandes executees :
- `.venv/bin/python manage.py check`
- `.venv/bin/python manage.py migrate`
- `.venv/bin/python manage.py test apps.core`
- `.venv/bin/pytest`
- `npm run build:css`

Resultats observes :
- `manage.py check` : succes, aucune erreur de configuration ;
- `migrate` : succes, migrations Django systeme appliquees ;
- `manage.py test apps.core` : `2 tests passes` ;
- `pytest` : `2 tests passes` ;
- `npm run build:css` : succes, feuille `static/css/tailwind.css` generee.

## 11. Points restant a traiter dans les etapes suivantes
- mise en place du `CustomUser` ;
- authentification et roles ;
- modeles metier ;
- logique financiere ;
- vues SQL ;
- fonctions SQL critiques ;
- interfaces `Admin` et `Agent`.

## 12. Conclusion de l'etape
L'etape 1 pose une base technique propre, lisible et exploitable. Elle prepare le terrain pour les prochaines etapes sans entrer encore dans les regles metier critiques.
