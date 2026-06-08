# ETAPE 11 - CYCLES SUCCESSIFS ET RETRAIT D'URGENCE

## 1. Objectif de l'etape
Etendre les regles metier des cycles et retraits pour couvrir :
- l'ouverture d'un nouveau cycle uniquement quand aucun cycle n'est deja en cours ;
- la possibilite d'ouvrir un nouveau cycle apres cloture normale ou cloture anticipee ;
- le retrait standard depuis le disponible deja credite ;
- le retrait d'urgence sur cycle en cours avec cloture anticipee automatique.

## 2. Perimetre traite
Cette etape couvre :
- la prevention de plusieurs cycles ouverts pour un meme client ;
- le nouveau statut `CLOTURE_ANTICIPEE` ;
- le retrait special / retrait d'urgence sur un cycle en cours ;
- la penalite egale a une mise ;
- la repartition 50/50 de la penalite entre agent et plateforme ;
- le reliquat eventuel du cycle converti en `CREDIT_CLIENT` ;
- l'interdiction de depot sur cycle cloture par anticipation ;
- la mise a jour des vues, formulaires, urls, templates et tests associes ;
- l'alignement des migrations PostgreSQL, vues SQL, fonctions SQL et contraintes SQL.

## 3. Decisions prises
- un cycle cloture n'est jamais reouvert ; un nouveau cycle est cree si le client repart sur un nouveau tour ;
- un client ne peut avoir qu'un seul cycle `EN_COURS` a la fois ;
- le retrait d'urgence ne remplace pas le retrait standard ; il suit un flux dedie ;
- le retrait d'urgence est autorise uniquement sur un cycle `EN_COURS` avec au moins `2` collectes ;
- le montant saisi pour le retrait d'urgence correspond au montant remis au client ;
- la penalite d'une mise est prelevee en plus de ce montant sur le total du cycle ;
- si tout le cycle n'est pas consomme par `montant + penalite`, le reliquat devient un `CREDIT_CLIENT` retirable ensuite par le flux standard ;
- le retrait d'urgence cloture toujours le cycle par anticipation selon l'option fonctionnelle retenue.

## 4. Fichiers crees
- `apps/transactions/services/emergency_withdrawal_service.py`
- `apps/transactions/migrations/0006_emergency_withdrawal_and_cycle_link.py`
- `templates/transactions/agent_emergency_withdrawal_create.html`
- `docs/etapes/ETAPE_11_CYCLES_SUCCESSIFS_ET_RETRAIT_URGENCE.md`

## 5. Fichiers modifies
- `apps/core/exceptions.py`
- `apps/cycles/models.py`
- `apps/cycles/services.py`
- `apps/cycles/views.py`
- `apps/clients/views.py`
- `apps/transactions/models.py`
- `apps/transactions/forms.py`
- `apps/transactions/urls.py`
- `apps/transactions/views.py`
- `apps/transactions/calculations.py`
- `apps/transactions/services/__init__.py`
- `apps/transactions/services/depot_service.py`
- `apps/transactions/services/retrait_service.py`
- `apps/transactions/tests/test_calculations.py`
- `apps/cycles/tests.py`
- `apps/transactions/tests/test_services.py`
- `apps/transactions/tests/test_postgresql_integration.py`
- `templates/clients/detail.html`
- `templates/cycles/detail.html`
- `templates/transactions/agent_retrait_create.html`
- `templates/transactions/admin_retrait_list.html`
- `docs/PLAN_REALISATION_PAR_ETAPES.md`
- `docs/DEMO_FONCTIONNELLE.md`

## 6. Elements techniques ajoutes

### 6.1 Exceptions metier
Ajout de :
- `ActiveCycleAlreadyExistsError`
- `EmergencyWithdrawalNotAllowedError`
- `EmergencyWithdrawalAmountExceededError`

Objectif :
- refuser proprement les cas metier non autorises ;
- garder des messages UI exploitables ;
- rendre les tests plus lisibles.

### 6.2 Nouveau statut de cycle
Ajout de `CycleStatus.CLOTURE_ANTICIPEE`.

Objectif :
- distinguer clairement une cloture a `31` collectes d'une sortie anticipee ;
- empecher les depots futurs sur un cycle casse par urgence ;
- garder une traçabilite plus precise dans les listes et details.

### 6.3 Evolution du modele de retrait
Ajout sur `Retrait` de :
- `cycle` nullable ;
- `type` avec valeurs `STANDARD` et `URGENCE`.

Objectif :
- separer les retraits issus du disponible et ceux relies a un cycle encore ouvert ;
- permettre un historique plus clair pour l'admin et les logs.

### 6.4 Nouveaux types de mouvements
Ajout de :
- `RETRAIT_URGENCE`
- `PENALITE_URGENCE`

Conservation de :
- `COM_AGENT`
- `COM_INSTITUTION`
- `CREDIT_CLIENT`

Objectif :
- ne pas polluer le `montant_retirable` standard ;
- garder des rapports lisibles ;
- reutiliser les commissions existantes pour le cumul agent / plateforme.

### 6.5 Calcul du retrait d'urgence
Ajout de `calculate_emergency_withdrawal_distribution(...)`.

Valeurs calculees :
- `total_collecte`
- `penalite`
- `commission_agent`
- `commission_institution`
- `montant_maximal`
- `montant_restant_en_credit`
- `montant_net_client`

### 6.6 EmergencyWithdrawalService
Ajout de `EmergencyWithdrawalService.create_emergency_withdrawal(...)`.

Responsabilites :
- verrouiller le cycle ;
- verifier le statut `EN_COURS` ;
- verifier le seuil minimal de `2` collectes ;
- verifier que le montant demande ne depasse pas `total_collecte - mise` ;
- creer un `Retrait` de type `URGENCE` ;
- creer les mouvements :
  - `RETRAIT_URGENCE`
  - `PENALITE_URGENCE`
  - `COM_AGENT`
  - `COM_INSTITUTION`
  - `CREDIT_CLIENT` si reliquat ;
- cloturer le cycle avec `CLOTURE_ANTICIPEE`.

## 7. Regles metier effectivement couvertes
- un client ne peut pas avoir deux cycles `EN_COURS` ;
- un nouveau cycle peut etre cree apres `CLOTURE` ou `CLOTURE_ANTICIPEE` ;
- un retrait standard continue d'utiliser uniquement le disponible calcule via `CREDIT_CLIENT - RETRAIT` ;
- un retrait d'urgence est interdit sur cycle deja cloture ;
- un retrait d'urgence est interdit avant `2` collectes ;
- un retrait d'urgence ne peut pas depasser `total_collecte - mise` ;
- la penalite d'urgence vaut exactement une mise ;
- la penalite d'urgence est partagee a `50/50` entre agent et plateforme ;
- le cycle passe automatiquement en `CLOTURE_ANTICIPEE` apres retrait d'urgence ;
- un depot est refuse sur cycle `CLOTURE` ou `CLOTURE_ANTICIPEE` ;
- le reliquat d'un retrait d'urgence reste disponible en `CREDIT_CLIENT` si le client n'a pas retire tout le montant maximal.

## 8. Vues SQL, fonctions SQL et contraintes SQL mises a jour
La migration `0006_emergency_withdrawal_and_cycle_link.py` met a jour :
- la contrainte PostgreSQL `mouvement_type_valid` pour accepter `RETRAIT_URGENCE` et `PENALITE_URGENCE` ;
- la vue `v_client_montant_retirable` ;
- la fonction `transactions_get_montant_retirable(...)` ;
- la fonction `transactions_create_retrait(...)` pour renseigner `type=STANDARD` et le nouveau schema du retrait ;
- la fonction trigger `transactions_prevent_depot_on_closed_cycle()` pour bloquer aussi `CLOTURE_ANTICIPEE`.

Important :
- le `montant_retirable` standard continue volontairement a se baser sur `CREDIT_CLIENT` et `RETRAIT` ;
- `RETRAIT_URGENCE` n'entre pas directement dans ce calcul ;
- seul le reliquat credite via `CREDIT_CLIENT` apres retrait d'urgence redevient retirable classiquement.

## 9. Interfaces mises a jour
### Fiche client agent
La fiche client agent affiche maintenant :
- `Ouvrir un nouveau cycle` uniquement s'il n'existe aucun cycle `EN_COURS` ;
- `Voir le cycle en cours` sinon ;
- `Effectuer un retrait standard` ;
- `Retrait special / urgence` si un cycle est encore ouvert.

### Detail cycle agent
Le detail cycle propose maintenant :
- `Enregistrer un depot` pour les cycles en cours ;
- `Declencher un retrait special` pour les cycles en cours ;
- une information explicite si le cycle est en `CLOTURE_ANTICIPEE`.

### Page dediee retrait d'urgence
La page `agent_emergency_withdrawal_create.html` affiche :
- le montant maximal autorise ;
- la penalite fixe ;
- le rappel de la cloture anticipee ;
- le formulaire de saisie du montant et du motif.

## 10. Tests ajoutes ou etendus
- calcul du retrait d'urgence ;
- refus de deux cycles ouverts pour un meme client ;
- autorisation d'un nouveau cycle apres cloture normale ;
- autorisation d'un nouveau cycle apres cloture anticipee ;
- refus de depot sur cycle cloture anticipee ;
- creation correcte d'un retrait d'urgence avec penalite et commissions ;
- cas de reliquat converti en `CREDIT_CLIENT` ;
- refus de montant d'urgence trop eleve ;
- refus d'urgence avant `2` collectes ;
- verification PostgreSQL que la vue `v_client_montant_retirable` reste coherente ;
- verification PostgreSQL que le trigger bloque aussi les cycles en cloture anticipee.

## 11. Resultat des tests
Commande executee :

```bash
.venv/bin/python manage.py test apps.cycles.tests apps.transactions.tests
```

Resultat :
- `42 tests OK`
- `System check identified no issues (0 silenced)`

## 12. Impact fonctionnel visible
Apres cette mise a jour :
- l'agent peut cloturer un cycle avant terme via un retrait special ;
- la penalite est automatiquement appliquee ;
- l'agent et la plateforme recoivent chacun 50% de cette penalite ;
- le client peut ensuite retirer le reliquat eventuel depuis son disponible ;
- un nouveau cycle peut etre ouvert proprement une fois le precedent sorti du statut `EN_COURS`.

## 13. Conclusion de l'etape
Cette etape complete fortement la logique terrain du projet :
- meilleure gestion des cas reels de sortie anticipee ;
- meilleure distinction entre retrait standard et retrait d'urgence ;
- architecture metier plus propre ;
- traçabilite conservee cote Django et cote PostgreSQL ;
- base saine pour les prochaines evolutions de reporting et d'interface.
