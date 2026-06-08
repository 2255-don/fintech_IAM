# ETAPE 05 - DEPOTS ET CLOTURE AUTOMATIQUE DES CYCLES

## 1. Objectif de l'etape
Implementer la logique critique autour :
- des depots ;
- du calcul du montant du depot ;
- de l'incrementation des collectes ;
- du refus de depassement ;
- du refus sur cycle cloture ;
- de la cloture automatique a `31` collectes ;
- de la creation de la retenue et des mouvements financiers de cloture.

## 2. Perimetre traite
Cette etape couvre :
- la creation d'un module explicite de calculs metier financiers ;
- la creation d'un `DepotService` ;
- la creation d'un `CloseCycleService` ;
- les exceptions metier de depot et de cloture ;
- le calcul du montant de depot ;
- la creation du mouvement `MISE` ;
- la mise a jour du cycle apres depot ;
- la creation automatique de :
  - `Retenue`
  - mouvement `RETENUE`
  - mouvement `COM_AGENT`
  - mouvement `COM_INSTITUTION`
  - mouvement `CREDIT_CLIENT`
- la fermeture automatique du cycle a `31` collectes.

## 3. Decisions prises
- la logique de depot est centralisee dans `DepotService` ;
- la logique de cloture est centralisee dans `CloseCycleService` ;
- les deux services sont executes dans une transaction atomique pour eviter les ecritures partielles ;
- le mouvement `MISE` est cree a chaque depot valide ;
- la cloture se declenche exactement quand `nb_collectes == 31` ;
- les commissions sont calculees avec un partage `50/50` ;
- le credit client est cree comme mouvement `CREDIT_CLIENT`.

## 4. Fichiers crees
- `apps/transactions/calculations.py`
- `apps/transactions/services/__init__.py`
- `apps/transactions/services/depot_service.py`
- `apps/transactions/services/close_cycle_service.py`
- `apps/transactions/tests/__init__.py`
- `apps/transactions/tests/test_calculations.py`
- `apps/transactions/tests/test_models.py`
- `apps/transactions/tests/test_services.py`
- `docs/etapes/ETAPE_05_DEPOTS_ET_CLOTURE_AUTOMATIQUE.md`

## 5. Fichiers modifies
- `apps/core/exceptions.py`
- `apps/transactions/models.py`
- `docs/PLAN_REALISATION_PAR_ETAPES.md`

## 6. Elements techniques ajoutes

### 6.1 Exceptions metier
Ajout de :
- `CycleClosedError`
- `InvalidNbMisesError`
- `CollecteLimitExceededError`

Objectif :
- rendre les refus de depot explicites ;
- permettre des tests precis ;
- preparer des retours utilisateur propres.

### 6.2 DepotService
Ajout de `DepotService` dans `apps/transactions/services/depot_service.py`.

Responsabilites :
- valider `nb_mises > 0` ;
- verrouiller le cycle avec `select_for_update()` ;
- refuser les depots sur cycle cloture ;
- refuser les depassements au-dela de `31` collectes ;
- calculer `montant = mise * nb_mises` ;
- creer le `Depot` ;
- creer le mouvement `MISE` ;
- incrementer `nb_collectes` ;
- declencher la cloture automatique si `31`.

### 6.3 Fonctions de calcul associees
Ajout dans `apps/transactions/calculations.py` de :
- `calculate_montant_depot`
- `calculate_close_cycle_distribution`
- `CloseCycleCalculation`

Objectif :
- materialiser explicitement les calculs metier annonces dans le cadre documentaire ;
- separer les calculs purs de l'orchestration transactionnelle ;
- rendre les formules directement testables.

### 6.4 CloseCycleService
Ajout de `CloseCycleService` dans `apps/transactions/services/close_cycle_service.py`.

Responsabilites :
- calculer `total_collecte` ;
- calculer `retenue = mise` ;
- calculer `commission_agent` ;
- calculer `commission_institution` ;
- calculer `credit_client` ;
- creer la `Retenue` ;
- creer les mouvements :
  - `RETENUE`
  - `COM_AGENT`
  - `COM_INSTITUTION`
  - `CREDIT_CLIENT`
- passer le cycle a `CLOTURE` ;
- renseigner `date_fermeture`.

## 7. Regles metier effectivement couvertes
- un depot doit avoir un nombre de mises strictement positif ;
- un cycle cloture n'accepte plus aucun depot ;
- un cycle ne peut jamais depasser `31` collectes ;
- un depot cree un mouvement `MISE` ;
- un cycle atteignant `31` collectes est cloture automatiquement ;
- la retenue de cloture est egale a une mise ;
- la retenue est partagee `50/50` entre agent et institution ;
- un mouvement `CREDIT_CLIENT` est cree a la cloture.

## 8. Formules implementees
- `montantDepot = mise * nbMises`
- `totalCollecte = mise * nb_collectes`
- `retenue = mise`
- `commissionAgent = retenue / 2`
- `commissionInstitution = retenue / 2` avec ajustement du reste sur l'institution si necessaire
- `creditClient = totalCollecte - retenue`

## 9. Pourquoi ces elements ont ete crees
- `DepotService` : pour centraliser l'orchestration metier du depot.
- `calculations.py` : pour isoler les formules metier pures et rendre le livrable explicite.
- `CloseCycleService` : pour isoler clairement la logique critique de cloture.
- transaction atomique : pour garantir l'absence d'ecritures partielles.
- exceptions metier : pour rendre les refus previsibles et testables.

## 10. Tests ajoutes ou etendus
- verification qu'un depot valide :
  - calcule correctement le montant ;
  - incremente les collectes ;
  - cree un mouvement `MISE`.
- verification directe des fonctions de calcul metier extraites ;
- refus si `nb_mises <= 0`
- refus si depassement des `31` collectes
- cloture automatique a `31`
- verification de la retenue `1000`
- verification des commissions `500 / 500`
- verification du mouvement `CREDIT_CLIENT = 30000`
- refus de depot sur cycle cloture

## 11. Resultat des tests
Commandes executees :
- `.venv/bin/python manage.py test apps.transactions --keepdb`
- `.venv/bin/python -m pytest apps/transactions`

Resultats observes :
- `manage.py test apps.transactions --keepdb` : `11 tests passes` ;
- `python -m pytest apps/transactions` : `11 tests passes`.

## 12. Points restant a traiter dans les etapes suivantes
- implementer le calcul du montant retirable ;
- implementer les retraits via service dedie ;
- brancher ensuite le reporting financier sur les mouvements ;
- renforcer plus tard avec les vues SQL et fonctions SQL critiques.

## 13. Conclusion de l'etape
L'etape 5 met en place le premier noyau financier critique du projet.

Elle fournit :
- une creation de depot controlee ;
- une protection contre les depassements ;
- une cloture automatique fiable ;
- les premieres ecritures financieres metier coherentes ;
- et une preuve de fonctionnement par tests.
