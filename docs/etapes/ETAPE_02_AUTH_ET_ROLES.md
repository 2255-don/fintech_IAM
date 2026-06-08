# ETAPE 02 - AUTHENTIFICATION ET ROLES

## 1. Objectif de l'etape
Mettre en place une base d'authentification claire, stable et testee avec :
- un `CustomUser` ;
- les roles `ADMIN` et `AGENT` ;
- la connexion/deconnexion ;
- la redirection selon role ;
- un profil agent minimal ;
- les premieres restrictions d'acces.

## 2. Perimetre traite
Cette etape couvre :
- la creation du modele utilisateur personnalise ;
- l'ajout du champ `role` ;
- la declaration de `AUTH_USER_MODEL` ;
- la creation du modele `Agent` minimal ;
- les vues de connexion et deconnexion ;
- la route de redirection role-aware ;
- les dashboards de base `Admin` et `Agent` ;
- les controles d'acces par role ;
- les tests d'authentification et de permissions ;
- les migrations associees.

## 3. Decisions prises
- le projet utilise desormais `accounts.User` comme modele utilisateur officiel ;
- le role est gere par un champ `role` avec les valeurs `ADMIN` et `AGENT` ;
- la redirection post-connexion se fait selon le role ;
- les dashboards `Admin` et `Agent` sont separes des cette etape ;
- la protection d'acces est assuree par un decorateur `role_required` ;
- un modele `Agent` minimal est prepare pour rattacher un utilisateur agent a un profil metier ;
- la base de reference de l'etape est `PostgreSQL`, conformement a la documentation technique du projet.

## 4. Fichiers crees
- `apps/accounts/forms.py`
- `apps/accounts/permissions.py`
- `apps/accounts/urls.py`
- `apps/accounts/migrations/0001_initial.py`
- `apps/agents/migrations/0001_initial.py`
- `templates/accounts/login.html`
- `templates/accounts/admin_dashboard.html`
- `templates/accounts/agent_dashboard.html`
- `templates/403.html`
- `docs/etapes/ETAPE_02_AUTH_ET_ROLES.md`

## 5. Fichiers modifies
- `config/settings.py`
- `config/urls.py`
- `apps/accounts/models.py`
- `apps/accounts/views.py`
- `apps/accounts/admin.py`
- `apps/accounts/tests.py`
- `apps/agents/models.py`
- `apps/agents/admin.py`
- `apps/agents/tests.py`
- `apps/core/views.py`
- `apps/core/tests.py`
- `templates/base.html`
- `.gitignore`

## 6. Elements techniques ajoutes

### 6.1 Modele utilisateur personnalise
Ajout de `accounts.User` base sur `AbstractUser` avec :
- champ `role` ;
- proprietes `is_admin_role` et `is_agent_role` ;
- methode `get_display_name()`.

### 6.2 Enum de role
Ajout de `UserRole` pour centraliser les valeurs :
- `ADMIN`
- `AGENT`

Objectif :
- eviter les chaines magiques dans le code ;
- clarifier les tests et permissions.

### 6.3 Profil agent minimal
Ajout du modele `Agent` avec :
- relation `OneToOne` vers `User` ;
- `code` unique ;
- `telephone` ;
- `actif` ;
- horodatage minimal.

Objectif :
- preparer le futur rattachement metier des agents a leur portefeuille.

### 6.4 Authentification
Ajout de :
- `LoginForm`
- `UserLoginView`
- `UserLogoutView`
- `dashboard_redirect`

Objectif :
- permettre la connexion ;
- gerer une sortie propre ;
- orienter automatiquement chaque utilisateur vers son bon espace.

### 6.5 Permissions de base
Ajout du decorateur `role_required`.

Objectif :
- proteger les vues par role ;
- retourner un `403` quand un utilisateur authentifie tente d'acceder a un espace non autorise.

### 6.6 Dashboards de base
Ajout de :
- `admin_dashboard`
- `agent_dashboard`

Objectif :
- poser les points d'entree propres des espaces `Admin` et `Agent` avant les futures pages metier.

## 7. Pourquoi ces elements ont ete crees
- `accounts.User` : pour controler explicitement les roles des le depart.
- `Agent` : pour preparer le profil metier de l'agent sans attendre les etapes metier plus lourdes.
- `role_required` : pour centraliser la logique de restriction simple.
- `dashboard_redirect` : pour eviter les parcours ambigus apres connexion.
- `templates/accounts/*` : pour separer visuellement les espaces par role et poser une base coherent d'interface.
- `templates/403.html` : pour afficher un retour propre sur les acces refuses.
- migrations `accounts` et `agents` : pour versionner l'etat du schema des cette etape.

## 8. Routes mises en place
- `connexion/` -> `login`
- `deconnexion/` -> `logout`
- `tableau-de-bord/` -> `dashboard_redirect`
- `tableau-de-bord/admin/` -> `admin_dashboard`
- `tableau-de-bord/agent/` -> `agent_dashboard`

## 9. Regles metier et de realisation couvertes
Cette etape ne traite pas encore les calculs financiers, mais elle couvre les fondations de securite et de separation des responsabilites.

Regles couvertes :
- separation claire des espaces `Admin` et `Agent` ;
- base de permissions par role ;
- architecture centralisee et lisible ;
- preparation de la gestion des agents comme profils metier ;
- base defendable pour les futures restrictions de portefeuille.

## 10. Tests ajoutes
- disponibilite de la page de connexion ;
- redirection d'un admin vers son dashboard ;
- redirection d'un agent vers son dashboard ;
- refus d'acces d'un admin au dashboard agent ;
- refus d'acces d'un agent au dashboard admin ;
- obligation d'authentification pour la route de redirection ;
- role par defaut du `CustomUser` ;
- priorite du nom complet dans `get_display_name()` ;
- liaison d'un profil `Agent` a un utilisateur agent ;
- redirection de la page d'accueil pour un utilisateur authentifie.

## 11. Resultat des tests
Commandes executees :
- `.venv/bin/python manage.py makemigrations accounts agents`
- `.venv/bin/python manage.py check`
- `.venv/bin/python manage.py migrate`
- `.venv/bin/python manage.py test apps.accounts apps.agents apps.core`
- `.venv/bin/pytest`

Resultats observes :
- migrations `accounts` et `agents` generees avec succes ;
- `manage.py check` : succes, aucune erreur de configuration ;
- `migrate` : succes, schema auth + accounts + agents applique ;
- `manage.py test apps.accounts apps.agents apps.core` : `12 tests passes` ;
- `pytest` : `12 tests passes`.

## 12. Points restant a traiter dans les etapes suivantes
- enrichir le modele `Agent` selon les besoins metier ;
- creer les modeles `Client`, `Cycle`, `Depot`, `Retenue`, `Retrait`, `Mouvement` ;
- relier les permissions aux vraies ressources metier ;
- preparer les acces portefeuille agent ;
- integrer les parcours metier reels sur les dashboards.

## 13. Conclusion de l'etape
L'etape 2 installe une base d'authentification propre, testee et directement exploitable pour la suite.

Elle fournit :
- un utilisateur personnalise ;
- une separation claire `Admin` / `Agent` ;
- un premier niveau de securite d'acces ;
- un profil agent minimal ;
- une base UI d'authentification et de dashboards.
