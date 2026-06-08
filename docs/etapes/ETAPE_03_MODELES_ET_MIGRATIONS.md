# ETAPE 03 - MODELES METIER ET MIGRATIONS INITIALES

## 1. Objectif de l'etape
Mettre en place les entites principales du domaine Fintech-IAM et leurs relations structurelles, avec :
- les modeles ORM metier ;
- les champs d'audit essentiels ;
- les contraintes structurelles de base ;
- les migrations initiales ;
- les tests de coherence des relations.

## 2. Perimetre traite
Cette etape couvre :
- l'ajout d'un modele d'audit abstrait reutilisable ;
- l'enrichissement du modele `Agent` ;
- la creation du modele `Client` ;
- la creation du modele `Cycle` ;
- la creation des modeles `Depot`, `Retenue`, `Retrait`, `Mouvement` ;
- l'ajout d'enums de statut et de type utiles ;
- les relations entre les entites ;
- les migrations ORM associees ;
- les tests de structure et de liaison entre modeles.

## 3. Decisions prises
- les entites metier sont reparties par domaines applicatifs : `agents`, `clients`, `cycles`, `transactions` ;
- les champs d'audit communs sont centralises dans `core.AuditModel` ;
- `Client` appartient a un `Agent` ;
- `Cycle` appartient a un `Client` ;
- `Depot` est rattache a un `Cycle`, un `Client` et un `Agent` ;
- `Retenue` est rattachee une seule fois a un `Cycle` via `OneToOneField` ;
- `Retrait` est rattache au `Client` et peut etre lie ou non a un `Agent` ;
- `Mouvement` sert de trace financiere generique rattachee a un contexte minimal ;
- des contraintes structurelles de base sont mises en place des maintenant, sans attendre les fonctions SQL critiques.

## 4. Fichiers crees
- `apps/core/models.py`
- `apps/clients/models.py`
- `apps/transactions/models.py`
- `apps/clients/tests.py`
- `apps/cycles/tests.py`
- `apps/transactions/tests.py`
- `apps/clients/migrations/0001_initial.py`
- `apps/cycles/migrations/0001_initial.py`
- `apps/transactions/migrations/0001_initial.py`
- `apps/agents/migrations/0002_agent_adresse_agent_created_by_agent_deleted_at_and_more.py`
- `docs/etapes/ETAPE_03_MODELES_ET_MIGRATIONS.md`

## 5. Fichiers modifies
- `apps/agents/models.py`
- `apps/cycles/models.py`
- `apps/clients/admin.py`
- `apps/cycles/admin.py`
- `apps/transactions/admin.py`

## 6. Elements techniques ajoutes

### 6.1 AuditModel
Ajout dans `apps/core/models.py` d'un modele abstrait `AuditModel` contenant :
- `created_at`
- `updated_at`
- `deleted_at`
- `created_by`
- `updated_by`
- `deleted_by`

Objectif :
- factoriser les champs d'audit ;
- preparer la tracabilite metier et technique ;
- eviter la duplication dans chaque entite.

### 6.2 Modele Agent enrichi
Le modele `Agent` a ete complete avec :
- `email`
- `adresse`
- heritage de `AuditModel`

Objectif :
- rapprocher le profil agent de la documentation technique ;
- preparer les futures pages de gestion agent.

### 6.3 Modele Client
Ajout de `Client` avec :
- `code`
- `agent`
- `nom`
- `prenom`
- `genre`
- `date_naissance`
- `telephone`
- `email`
- `adresse`
- `actif`
- champs d'audit

Objectif :
- representer le portefeuille client gere par un agent.

### 6.4 Modele Cycle
Ajout de `Cycle` avec :
- `code`
- `client`
- `mise`
- `nb_collectes`
- `statut`
- `date_ouverture`
- `date_fermeture`
- champs d'audit

Ajout de `CycleStatus` :
- `EN_COURS`
- `CLOTURE`

Contraintes de base :
- `mise > 0`
- `0 <= nb_collectes <= 31`

Objectif :
- porter la structure de base du cycle d'epargne.

### 6.5 Modeles transactions
Ajout de :
- `Depot`
- `Retenue`
- `Retrait`
- `Mouvement`

Ajout des enums :
- `MouvementType`
- `MouvementSens`

Objectif :
- modeliser les objets financiers principaux du projet ;
- preparer la traçabilite future des operations.

## 7. Relations mises en place
- `Agent 1 -> N Client`
- `Client 1 -> N Cycle`
- `Cycle 1 -> N Depot`
- `Cycle 1 -> 0..1 Retenue`
- `Client 1 -> N Retrait`
- `Client 1 -> N Mouvement`
- `Cycle 1 -> N Mouvement`
- `Agent 1 -> N Depot`
- `Agent 1 -> N Retenue`
- `Agent 1 -> N Retrait`
- `Agent 1 -> N Mouvement`

## 8. Ce qui est stocke et ce qui ne l'est pas

### Donnees stockees
- mise ;
- nb_collectes ;
- statut du cycle ;
- montant d'un depot ;
- montant d'une retenue ;
- montant d'un retrait ;
- montant d'un mouvement ;
- references de relation entre agent, client, cycle et transactions.

### Donnees non stockees comme source de verite
- `montant_retirable`

Raison :
- il devra etre recalcule a partir des mouvements financiers dans les etapes suivantes.

## 9. Pourquoi ces elements ont ete crees
- `AuditModel` : pour normaliser l'audit des entites metier.
- `Client` : pour porter le portefeuille agent -> client.
- `Cycle` : pour representer la structure du cycle d'epargne.
- `Depot` : pour historiser les versements.
- `Retenue` : pour materialiser la retenue de cloture.
- `Retrait` : pour historiser les sorties de disponible client.
- `Mouvement` : pour servir de base future des calculs financiers et historiques.
- enums : pour eviter les valeurs textuelles libres non controlees.

## 10. Contraintes structurelles ajoutees
- `Cycle.mise > 0`
- `Cycle.nb_collectes` borne entre `0` et `31`
- `Retenue` unique par `Cycle`
- `Mouvement` doit etre relie a au moins un contexte (`client`, `cycle` ou `agent`)
- unicite des codes metier sur toutes les entites principales

## 11. Tests ajoutes
- creation d'un client rattache a un agent ;
- verification des valeurs par defaut d'un cycle ;
- verification du refus d'une mise nulle ;
- verification des relations `Depot` ;
- verification du rattachement unique d'une `Retenue` a un cycle ;
- verification qu'un `Retrait` peut exister sans agent ;
- verification du contexte minimal d'un `Mouvement` ;
- verification de l'affichage metier de l'agent via ses nouvelles donnees.

## 12. Resultat des tests
Commandes executees :
- `.venv/bin/python manage.py check`
- `.venv/bin/python manage.py makemigrations core agents clients cycles transactions`
- `.venv/bin/python manage.py migrate`
- `.venv/bin/python manage.py test apps.clients apps.cycles apps.transactions apps.agents`
- `.venv/bin/python -m pytest apps/clients apps/cycles apps/transactions apps/agents`

Resultats observes :
- `manage.py check` : succes ;
- migrations step 3 generees avec succes ;
- migrations appliquees avec succes sur PostgreSQL ;
- `manage.py test ...` : `8 tests passes` ;
- `python -m pytest ...` : `8 tests passes`.

## 13. Points restant a traiter dans les etapes suivantes
- ajouter les services metier `ClientService` et `CycleService` ;
- mettre en place les regles metier explicites sur la mise multiple de 100 ;
- implementer la logique de depot et de cloture automatique ;
- commencer la logique de calcul et de mouvements metier ;
- ajouter plus tard les vues SQL et fonctions SQL critiques.

## 14. Conclusion de l'etape
L'etape 3 pose le vrai squelette metier du projet.

Elle fournit :
- les entites principales ;
- les relations structurantes ;
- les champs d'audit communs ;
- les contraintes ORM de base ;
- les migrations PostgreSQL ;
- et une premiere preuve de coherence via les tests modeles.
