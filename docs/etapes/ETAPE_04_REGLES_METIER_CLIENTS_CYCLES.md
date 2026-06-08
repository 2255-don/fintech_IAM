# ETAPE 04 - REGLES METIER DE BASE DES CLIENTS ET CYCLES

## 1. Objectif de l'etape
Mettre en place les premieres vraies regles metier explicites autour :
- de la creation client ;
- de l'ouverture de cycle ;
- de la validation de la mise ;
- des exceptions metier de base ;
- des services applicatifs `ClientService` et `CycleService`.

## 2. Perimetre traite
Cette etape couvre :
- la creation de services metier pour `Client` et `Cycle` ;
- l'ajout d'exceptions metier dediees ;
- la validation explicite de la mise ;
- la creation controlee d'un client ;
- la creation controlee d'un cycle ;
- les tests de ces regles metier ;
- la documentation des comportements.

## 3. Decisions prises
- les regles metier de base sont implementees dans des services explicites, pas dans les vues ;
- les erreurs metier sont portees par des exceptions dediees ;
- la validation de la mise est centralisee dans `CycleService.validate_mise()` ;
- la creation client verifie explicitement l'existence de l'agent responsable ;
- la creation cycle verifie explicitement l'existence du client cible ;
- les valeurs initiales du cycle (`nb_collectes=0`, `statut=EN_COURS`) sont garanties par le service metier.

## 4. Fichiers crees
- `apps/core/exceptions.py`
- `apps/clients/services.py`
- `apps/cycles/services.py`
- `docs/etapes/ETAPE_04_REGLES_METIER_CLIENTS_CYCLES.md`

## 5. Fichiers modifies
- `apps/clients/tests.py`
- `apps/cycles/tests.py`

## 6. Elements techniques ajoutes

### 6.1 Exceptions metier
Ajout dans `apps/core/exceptions.py` de :
- `BusinessRuleError`
- `AgentNotFoundError`
- `ClientNotFoundError`
- `InvalidMiseError`

Objectif :
- separer clairement les erreurs metier des erreurs techniques ;
- preparer un futur mapping propre vers des messages UI.

### 6.2 ClientService
Ajout de `ClientService` dans `apps/clients/services.py`.

Responsabilites prises en charge :
- verification de l'existence de l'agent ;
- creation d'un client avec valeurs transmettees ;
- renseignement de `created_by` et `updated_by` si disponibles.

### 6.3 CycleService
Ajout de `CycleService` dans `apps/cycles/services.py`.

Responsabilites prises en charge :
- validation de la mise ;
- verification de l'existence du client ;
- creation d'un cycle avec :
  - `nb_collectes=0`
  - `statut=EN_COURS`
  - champs d'audit.

## 7. Regles metier effectivement couvertes

### Cote client
- un client doit etre rattache a un agent existant ;
- la creation d'un client echoue si l'agent responsable est introuvable.

### Cote cycle
- une mise doit etre strictement positive ;
- une mise doit etre un multiple de `100 FCFA` ;
- un cycle cree demarre avec `0 collecte` ;
- un cycle cree demarre avec le statut `EN_COURS` ;
- la creation d'un cycle echoue si le client cible est introuvable.

## 8. Pourquoi ces elements ont ete crees
- `ClientService` : pour ne pas laisser la creation client partir directement de l'ORM sans controle metier.
- `CycleService` : pour centraliser les regles de la mise et l'initialisation correcte du cycle.
- exceptions metier : pour rendre les erreurs previsibles, testables et lisibles.

## 9. Tests ajoutes ou etendus

### Tests client
- creation d'un client via service ;
- verification de l'affectation agent ;
- verification de l'affectation `created_by` / `updated_by` ;
- erreur si l'agent n'existe pas.

### Tests cycle
- validation d'une mise correcte ;
- refus d'une mise nulle ;
- refus d'une mise non multiple de 100 ;
- creation d'un cycle avec valeurs metier initiales attendues ;
- erreur si le client n'existe pas.

## 10. Resultat des tests
Commandes executees :
- `.venv/bin/python manage.py test apps.clients apps.cycles --keepdb`
- `.venv/bin/python -m pytest apps/clients apps/cycles`

Resultats observes :
- `manage.py test ... --keepdb` : `10 tests passes` ;
- `python -m pytest ...` : `10 tests passes`.

Note :
- le mode `--keepdb` a ete utilise pour eviter l'interaction PostgreSQL sur une base de test deja existante.

## 11. Points restant a traiter dans les etapes suivantes
- ajouter les services metier de depot et de retrait ;
- implementer la cloture automatique ;
- implementer les mouvements financiers lors des operations ;
- brancher ces services sur de vraies vues/formulaires metier ;
- renforcer ensuite avec les vues SQL et fonctions critiques PostgreSQL.

## 12. Conclusion de l'etape
L'etape 4 fait passer le projet d'un simple schema de donnees a une vraie couche metier explicite sur les cas d'usage de base.

Elle fournit :
- des services metier clairs ;
- des exceptions dediees ;
- des regles testees pour la creation client et cycle ;
- et une base saine pour les etapes financieres critiques a venir.
