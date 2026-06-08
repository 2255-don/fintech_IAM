# ETAPE 06 - RETRAITS, MONTANT RETIRABLE ET REPORTING FINANCIER

## 1. Objectif de l'etape
Implementer la logique de retrait et les calculs de consultation financiere a partir des mouvements deja produits par les cycles clotures.

## 2. Perimetre traite
Cette etape couvre :
- le calcul du montant retirable d'un client ;
- la synthese financiere d'un client ;
- la creation d'un retrait metier ;
- le refus de retrait si le montant disponible est insuffisant ;
- la creation automatique du mouvement `RETRAIT` ;
- les tests de coherence entre cloture de cycle, montant retirable et retrait.

## 3. Decisions prises
- le montant retirable est calcule a partir des mouvements, sans champ denormalise sur `Client` ;
- le calcul est centralise dans `ReportingService` pour rester reutilisable ;
- le retrait metier est centralise dans `RetraitService` pour separer calcul et orchestration ;
- la disponibilite financiere est verifiee juste avant creation du retrait ;
- les agregations sont faites par requetes ORM centralisees, en attendant l'etape 7 dediee aux vues/fonctions SQL PostgreSQL.

## 4. Fichiers crees
- `apps/transactions/services/reporting_service.py`
- `apps/transactions/services/retrait_service.py`
- `docs/etapes/ETAPE_06_RETRAITS_MONTANT_RETIRABLE_REPORTING.md`

## 5. Fichiers modifies
- `apps/core/exceptions.py`
- `apps/transactions/services/__init__.py`
- `apps/transactions/tests/test_services.py`

## 6. Elements techniques ajoutes

### 6.1 Exception metier
Ajout de :
- `InsufficientRetirableAmountError`

Objectif :
- rendre explicite le refus d'un retrait invalide ;
- permettre des tests metier precis ;
- preparer un branchement propre futur vers les messages UI.

### 6.2 ReportingService
Ajout de `ReportingService` dans `apps/transactions/services/reporting_service.py`.

Responsabilites :
- calculer le `montant_retirable` d'un client ;
- produire une synthese financiere exploitable ;
- centraliser les requetes d'agregation financiere ;
- preparer la transition future vers des vues SQL PostgreSQL si necessaire.

### 6.3 RetraitService
Ajout de `RetraitService` dans `apps/transactions/services/retrait_service.py`.

Responsabilites :
- verifier que le client existe ;
- verifier que le montant demande est strictement positif ;
- verifier que le montant demande ne depasse pas le montant retirable ;
- creer le `Retrait` ;
- creer automatiquement le mouvement `RETRAIT` associe.

## 7. Formules retenues
- `montantRetirable = somme(CREDIT_CLIENT) - somme(RETRAIT)`
- `totalCreditClient = somme(CREDIT_CLIENT)`
- `totalRetraits = somme(RETRAIT)`

Ces calculs sont volontairement bases sur les mouvements afin de garder une source de verite unique.

## 8. Regles metier effectivement couvertes
- un client ne peut retirer qu'un montant strictement positif ;
- un client ne peut pas retirer plus que son montant retirable ;
- un retrait valide cree un enregistrement `Retrait` ;
- un retrait valide cree un mouvement `RETRAIT` ;
- le montant retirable diminue immediatement apres un retrait ;
- le reporting financier reutilise les mouvements comme base de calcul.

## 9. Pourquoi ces elements ont ete crees
- `ReportingService` : pour separer clairement les calculs de consultation des services d'ecriture.
- `RetraitService` : pour garder une orchestration metier propre, testable et reutilisable.
- `InsufficientRetirableAmountError` : pour distinguer nettement les refus fonctionnels des erreurs techniques.

## 10. Tests ajoutes ou etendus
- verification que `ReportingService.get_montant_retirable()` retourne `30000` apres cloture d'un cycle a `31` collectes avec `mise=1000` ;
- verification que `ReportingService.get_client_financial_summary()` retourne les bons agregats ;
- verification qu'un retrait de `5000` cree :
  - un `Retrait`
  - un mouvement `RETRAIT`
  - et fait passer le montant retirable a `25000` ;
- refus d'un retrait superieur au montant disponible ;
- refus d'un retrait nul ou negatif.

## 11. Requetes centralisees et preparation SQL
Pour cette etape, les calculs critiques de reporting sont centralises dans `ReportingService` via des agregations ORM (`Case`, `When`, `Sum`, `Coalesce`).

Ce choix respecte le perimetre actuel tout en preparant l'etape 7, ou les vues SQL, fonctions SQL et triggers PostgreSQL seront formalises dans des migrations `RunSQL`.

## 12. Resultat des tests
Commandes de verification executees pour figer l'etape :
- `.venv/bin/python manage.py test apps.transactions`
- `.venv/bin/python -m pytest apps/transactions`

Resultats :
- `manage.py test apps.transactions --noinput` : `16 tests OK`
- `python -m pytest -p no:cacheprovider apps/transactions` : `16 tests passes`

Note d'execution :
- les suites PostgreSQL doivent etre lancees de maniere sequentielle, et non en parallele, car elles partagent la base de test `test_fintech_iam`.

## 13. Points restant a traiter dans les etapes suivantes
- transformer les requetes de reporting critiques en objets SQL PostgreSQL si le besoin de performance/traçabilite le justifie ;
- ajouter les vues SQL et fonctions SQL demandees dans la documentation technique enrichie ;
- exposer ensuite ces services dans les interfaces `Admin` et `Agent`.

## 14. Conclusion de l'etape
L'etape 6 ajoute le second noyau financier du projet :
- consultation fiable du disponible client ;
- retrait controle ;
- tracabilite par mouvements ;
- base propre pour le reporting et les futures interfaces.
