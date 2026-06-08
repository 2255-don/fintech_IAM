# ETAPE 07 - RENFORCEMENT POSTGRESQL

## 1. Objectif de l'etape
Ajouter les mecanismes PostgreSQL critiques demandes dans la documentation technique :
- contraintes SQL complementaires ;
- vues SQL de reporting ;
- fonctions SQL critiques ;
- triggers de protection ;
- migrations versionnees `RunSQL`.

## 2. Perimetre traite
Cette etape couvre :
- le renforcement des invariants PostgreSQL autour des cycles et mouvements ;
- la creation des vues SQL de reporting principales ;
- la creation des fonctions SQL critiques retenues ;
- la protection de certaines operations directes en base ;
- l'integration des nouveaux objets SQL dans les services Django ;
- les tests d'integration base de donnees.

## 3. Decisions prises
- les objets SQL sont crees dans des migrations `RunSQL` dediees et versionnees ;
- les calculs de consultation sont centralises en base via des vues et une fonction SQL ;
- la logique de retrait utilise maintenant une fonction PostgreSQL dediee ;
- la logique `DepotService` / `CloseCycleService` reste cote Django pour eviter une duplication forte de l'orchestration critique ;
- a la place, des triggers PostgreSQL servent de second niveau de defense sur les depots et l'historique des mouvements ;
- les tests PostgreSQL sont lances de maniere sequentielle, jamais en parallele, car ils partagent `test_fintech_iam`.

## 4. Fichiers crees
- `apps/transactions/migrations/0002_postgresql_constraints.py`
- `apps/transactions/migrations/0003_postgresql_views.py`
- `apps/transactions/migrations/0004_postgresql_functions.py`
- `apps/transactions/migrations/0005_postgresql_triggers.py`
- `apps/transactions/tests/test_postgresql_integration.py`
- `docs/etapes/ETAPE_07_RENFORCEMENT_POSTGRESQL.md`

## 5. Fichiers modifies
- `apps/transactions/services/reporting_service.py`
- `apps/transactions/services/retrait_service.py`

## 6. Objets SQL ajoutes

### 6.1 Contraintes et index
Ajouts principaux :
- contrainte `cycle_mise_multiple_100`
- contrainte `mouvement_type_valid`
- contrainte `mouvement_sens_valid`
- index partiels sur `transactions_mouvement`
- index partiel sur `cycles_cycle(statut)`

Objectif :
- renforcer les invariants metier directement en base ;
- accelerer les lectures frequentes sur mouvements et cycles actifs.

### 6.2 Vues SQL creees

#### `v_client_montant_retirable`
Responsabilite :
- calculer par client :
  - `total_credit_client`
  - `total_retraits`
  - `montant_retirable`

Formule :
- `sum(CREDIT_CLIENT) - sum(RETRAIT)`

#### `v_agent_commissions`
Responsabilite :
- calculer le total des commissions agent a partir des mouvements `COM_AGENT`.

#### `v_cycle_resume`
Responsabilite :
- exposer un resume lisible des cycles avec :
  - client
  - agent
  - mise
  - nb_collectes
  - statut
  - total collecte courant

### 6.3 Fonctions SQL creees

#### `transactions_get_montant_retirable(p_client_id)`
Responsabilite :
- retourner le montant retirable calcule d'un client depuis la vue SQL.

#### `transactions_create_retrait(p_client_id, p_montant, p_user_id, p_motif)`
Responsabilite :
- verifier que le montant est strictement positif ;
- verifier que le client existe ;
- verifier que le montant retirable est suffisant ;
- creer le `Retrait` ;
- creer le mouvement `RETRAIT` associe ;
- retourner l'identifiant du retrait cree.

### 6.4 Triggers de protection crees

#### `trg_transactions_prevent_depot_on_closed_cycle`
But :
- interdire tout depot direct sur un cycle cloture.

#### `trg_transactions_validate_depot_limit`
But :
- interdire toute tentative directe qui ferait depasser `31` collectes.

#### `trg_transactions_prevent_mouvement_update`
But :
- empecher la modification d'un mouvement financier historique.

#### `trg_transactions_prevent_mouvement_delete`
But :
- empecher la suppression physique d'un mouvement financier historique.

## 7. Integration Django des objets SQL

### 7.1 ReportingService
`ReportingService` utilise maintenant :
- `transactions_get_montant_retirable(...)` pour le calcul du disponible ;
- `v_client_montant_retirable` pour la synthese financiere client.

### 7.2 RetraitService
`RetraitService` utilise maintenant :
- `transactions_create_retrait(...)` pour la creation atomique du retrait et du mouvement associe.

## 8. Regles metier effectivement couvertes
- `RB-005` la mise reste un multiple de `100 FCFA` aussi cote PostgreSQL ;
- `RB-015` le montant retirable est recalculable depuis les mouvements via vue et fonction SQL ;
- `RB-016` un retrait insuffisant est refuse aussi dans la fonction SQL ;
- `RB-018` un depot direct sur cycle cloture est bloque par trigger ;
- `RB-019` le retrait critique dispose d'un renfort transactionnel au plus pres des donnees ;
- `RB-020` les mouvements financiers historiques sont proteges contre mise a jour/suppression directe.

## 9. Pourquoi cette mise en oeuvre a ete retenue
- les vues SQL evitent de recopier les memes agregations dans plusieurs endroits ;
- la fonction SQL de retrait renforce une operation qui impacte directement le disponible client ;
- les triggers apportent un filet de securite utile sans cacher toute la logique applicative en base ;
- la creation SQL complete des depots et de la cloture n'a pas ete dupliquee a ce stade pour eviter une double orchestration metier difficile a maintenir entre Django et PostgreSQL.

## 10. Tests ajoutes
- verification de `v_client_montant_retirable`
- verification de `v_agent_commissions`
- verification de `v_cycle_resume`
- verification que `RetraitService` passe bien par la fonction SQL de creation de retrait
- verification du trigger de depot sur cycle cloture
- verification du trigger de depassement de `31` collectes
- verification du trigger d'interdiction de mise a jour des mouvements
- verification du trigger d'interdiction de suppression physique des mouvements

## 11. Resultat des tests
Commandes executees :
- `.venv/bin/python manage.py migrate`
- `.venv/bin/python manage.py test apps.transactions --noinput`
- `.venv/bin/python -m pytest -p no:cacheprovider apps/transactions`

Resultats :
- `manage.py migrate` : migrations `0002` a `0005` appliquees avec succes ;
- `manage.py test apps.transactions --noinput` : `24 tests OK` ;
- `python -m pytest -p no:cacheprovider apps/transactions` : `24 tests passes`.

Note d'execution :
- une tentative de lancement parallele `manage.py test` + `pytest` sur PostgreSQL fait echouer la base de test partagee ;
- la consigne correcte pour ce projet reste donc une execution sequentielle.

## 12. Points restant a traiter dans les etapes suivantes
- brancher ces vues SQL sur les interfaces `Admin` et `Agent` ;
- exposer les commissions et resumes de cycles dans les pages de supervision ;
- poursuivre avec le decoupage UI/UX et les interfaces separees par role ;
- ajouter ensuite les messages, confirmations, logs et pages d'erreur.

## 13. Conclusion de l'etape
L'etape 7 renforce reellement le projet cote base :
- invariants metier renforces ;
- calculs de reporting centralises ;
- retrait critique securise ;
- historique financier protege ;
- preuve d'execution fournie par migrations et tests PostgreSQL.
