# CONCEPTION DETAILLEE DU PROJET

## Projet Fintech-IAM
### Blueprint fonctionnel et technique de realisation

## 1. Objet du document
Ce document traduit la documentation technique generale en plan de conception concret.

Son objectif est de definir clairement :
- les espaces fonctionnels du projet ;
- les roles et permissions ;
- les pages a creer ;
- les composants reutilisables ;
- le decoupage technique ;
- les cas d'usage metier ;
- l'ordre d'implementation.

Ce document sert de blueprint de travail avant le developpement.

## 2. Vision de conception
Le projet doit etre pense comme une application metier simple, modulaire et defendable.

Priorites :
- logique metier centralisee ;
- separation claire entre `Admin` et `Agent` ;
- pages simples et peu surchargees ;
- composants reutilisables ;
- parcours utilisateur comprehensibles ;
- traçabilite financiere complete ;
- base technique propre sans dette inutile.

## 3. Roles applicatifs

### 3.1 Role ADMIN
Responsabilites :
- gerer les agents ;
- consulter tous les clients ;
- consulter tous les cycles ;
- consulter tous les depots ;
- consulter tous les retraits ;
- consulter tous les mouvements financiers ;
- superviser les indicateurs globaux.

Objectif UX :
- offrir une vue systeme ;
- faciliter la supervision ;
- centraliser les operations d'administration.

### 3.2 Role AGENT
Responsabilites :
- consulter son portefeuille client ;
- creer et consulter ses clients ;
- ouvrir un cycle pour un client de son portefeuille ;
- enregistrer des depots ;
- effectuer ou enregistrer des retraits selon la regle retenue ;
- consulter l'historique utile a son portefeuille ;
- consulter ses commissions et l'etat des cycles suivis.

Objectif UX :
- fournir un espace operationnel rapide ;
- aller directement aux actions frequentes ;
- limiter la surcharge cognitive.

## 4. Decoupage fonctionnel par espace

### 4.1 Espace ADMIN
Fonctions principales :
- dashboard global ;
- gestion des agents ;
- consultation globale des clients ;
- consultation globale des cycles ;
- consultation globale des depots ;
- consultation globale des retraits ;
- consultation globale des mouvements ;
- visualisation des commissions et montants retirable par client.

### 4.2 Espace AGENT
Fonctions principales :
- dashboard personnel ;
- gestion de son portefeuille client ;
- consultation detaillee d'un client ;
- ouverture de cycle ;
- detail d'un cycle ;
- enregistrement d'un depot ;
- enregistrement d'un retrait ;
- consultation des mouvements lies a son portefeuille ;
- consultation des commissions agent.

## 5. Parcours utilisateur principaux

### 5.1 Parcours Agent - Creer un client
Connexion agent -> dashboard agent -> page clients -> bouton "Nouveau client" -> formulaire -> validation -> creation -> message toaster succes -> redirection detail client ou liste.

### 5.2 Parcours Agent - Ouvrir un cycle
Connexion agent -> liste clients -> detail client -> action "Ouvrir un cycle" -> formulaire mise -> validation metier -> creation cycle -> toaster succes -> page detail cycle.

### 5.3 Parcours Agent - Enregistrer un depot
Connexion agent -> detail cycle `EN_COURS` -> action "Nouveau depot" -> saisie nb de mises -> validation -> confirmation si necessaire -> enregistrement -> toaster succes -> detail cycle actualise.

### 5.4 Parcours Agent - Effectuer un retrait
Connexion agent -> detail client -> consultation du montant retirable -> action "Effectuer un retrait" -> saisie montant -> confirmation SweetAlert -> validation metier -> enregistrement -> toaster succes -> detail client actualise.

### 5.5 Parcours Admin - Gerer un agent
Connexion admin -> dashboard admin -> page agents -> creation/modification/consultation -> toaster succes -> retour liste/detail.

### 5.6 Parcours Admin - Supervision financiere
Connexion admin -> dashboard admin -> pages cycles / mouvements / retraits / commissions -> filtres -> consultation.

## 6. Liste des pages a creer

### 6.1 Pages communes
- page de connexion ;
- page d'accueil authentifiee avec redirection selon role ;
- profil utilisateur minimal si retenu ;
- pages d'erreur `403`, `404`, `500`.

### 6.2 Pages ADMIN
- dashboard admin ;
- liste agents ;
- creation agent ;
- detail agent ;
- liste clients ;
- detail client ;
- liste cycles ;
- detail cycle ;
- liste depots ;
- liste retraits ;
- liste mouvements ;
- page de synthese commissions.

### 6.3 Pages AGENT
- dashboard agent ;
- liste de mes clients ;
- creation client ;
- detail client ;
- ouverture cycle ;
- detail cycle ;
- creation depot ;
- creation retrait ;
- historique des mouvements de mon portefeuille ;
- page de mes commissions.

### 6.4 Pages transverses
- page de recherche simple si utile ;
- page de confirmation operationnelle si besoin ;
- pages de logs non exposees a l'utilisateur final, reservees au back-office technique si un besoin apparait plus tard.

## 7. Regles de decoupage des pages
- une page doit servir une responsabilite principale ;
- eviter les ecrans fourre-tout ;
- ne pas mettre creation, consultation detaillee, historique complet et administration lourde dans une seule vue ;
- privilegier des pages detaillees par contexte ;
- les operations sensibles doivent etre visibles, explicites et confirmees.

## 8. Composants UI reutilisables

### 8.1 Composants structurels
- `BaseLayout`
- `AdminLayout`
- `AgentLayout`
- `Sidebar`
- `Topbar`
- `PageHeader`
- `Breadcrumb`

### 8.2 Composants de presentation
- `StatCard`
- `DataTable`
- `StatusBadge`
- `EmptyState`
- `InfoCard`
- `DetailSection`
- `TimelineList` pour mouvements si utile.

### 8.3 Composants de formulaire
- `FormSection`
- `InputGroup`
- `SelectField`
- `NumberField`
- `TextareaField`
- `FormActions`

### 8.4 Composants d'interaction
- `ToastContainer`
- `FlashMessageRenderer`
- `ConfirmActionModal` ou integration SweetAlert2 ;
- `ActionButton`
- `DangerButton`
- `FilterBar`

### 8.5 Regles de conception des composants
- ne componentiser que ce qui est vraiment reutilise ;
- garder des composants simples ;
- eviter les composants trop magiques ;
- mutualiser structure, styles et patterns repetes ;
- ne pas cacher la logique metier dans les composants.

## 9. Structure technique recommandee

### 9.1 Option retenue
Projet Django avec separation par domaines metier simples.

Structure recommandee :

```text
specDriven/
├── docs/
├── config/
├── apps/
│   ├── accounts/
│   ├── agents/
│   ├── clients/
│   ├── cycles/
│   ├── transactions/
│   └── core/
├── templates/
├── static/
├── theme/
├── logs/
└── tests/
```

### 9.2 Role de chaque module
- `accounts` : authentification, custom user, roles, redirections selon role.
- `agents` : profil agent, gestion admin des agents.
- `clients` : clients, portefeuille, affichage detail client.
- `cycles` : cycles d'epargne, ouverture, detail, cloture.
- `transactions` : depots, retraits, retenues, mouvements, reporting financier simple.
- `core` : utilitaires vraiment necessaires, base models, services communs limites, pages d'erreur, configuration UI transversale.

## 10. Couche metier cible

### 10.1 Domaine
Le domaine doit contenir :
- enums ;
- exceptions metier ;
- regles pures ;
- fonctions de calcul simples.

Exemples :
- `CycleStatus`
- `MouvementType`
- `validate_mise`
- `validate_nb_mises`
- `calculate_depot_amount`
- `calculate_close_cycle_distribution`

### 10.2 Services applicatifs
Les services doivent porter la logique principale.

Services minimaux attendus :
- `AgentService`
- `ClientService`
- `CycleService`
- `DepotService`
- `RetraitService`
- `ReportingService`

### 10.3 Responsabilites des services
- `ClientService` : creation client, verification portefeuille, recherche client.
- `CycleService` : ouverture cycle, verification eligibilite, detail cycle, cloture si necessaire.
- `DepotService` : creation depot, verification limite, creation mouvement mise, declenchement cloture.
- `RetraitService` : verification solde disponible, creation retrait, creation mouvement retrait.
- `ReportingService` : consultation soldes, commissions, historiques et syntheses.

## 11. Entites metier a implementer

### 11.1 User
Responsabilites :
- authentification ;
- role `ADMIN` ou `AGENT` ;
- statut actif.

### 11.2 Agent
Responsabilites :
- profil metier agent ;
- rattachement a un user ;
- portefeuille client associe.

### 11.3 Client
Responsabilites :
- identification client ;
- rattachement agent ;
- consultation cycles ;
- consultation montant retirable.

### 11.4 Cycle
Responsabilites :
- mise ;
- statut ;
- nombre de collectes ;
- date ouverture/fermeture ;
- relation avec depots et mouvements.

### 11.5 Depot
Responsabilites :
- historiser les versements ;
- conserver `nb_mises` et `montant`.

### 11.6 Retenue
Responsabilites :
- historiser la retenue de cloture ;
- enregistrer la distribution agent / institution.

### 11.7 Retrait
Responsabilites :
- historiser les retraits client ;
- servir au calcul du montant retirable.

### 11.8 Mouvement
Responsabilites :
- servir de source de verite financiere pour les calculs et historiques.

## 12. Cas d'usage metier detailles

### 12.1 Cas d'usage - Creer un client
Entree :
- nom ;
- prenom si present ;
- telephone ;
- agent responsable.

Traitement :
- verifier l'existence de l'agent ;
- verifier les champs obligatoires ;
- creer le client ;
- renseigner audit.

Sortie :
- client cree ;
- message succes.

### 12.2 Cas d'usage - Ouvrir un cycle
Entree :
- client ;
- mise.

Traitement :
- verifier que le client existe ;
- verifier que la mise est positive ;
- verifier qu'elle est multiple de 100 ;
- initialiser `nb_collectes=0` ;
- initialiser `statut=EN_COURS`.

Sortie :
- cycle cree ;
- message succes.

### 12.3 Cas d'usage - Enregistrer un depot
Entree :
- cycle ;
- nb_mises.

Traitement :
- verifier que le cycle existe ;
- verifier qu'il est `EN_COURS` ;
- verifier que `nb_mises > 0` ;
- verifier que `nb_collectes + nb_mises <= 31` ;
- calculer montant depot ;
- creer depot ;
- creer mouvement `MISE` ;
- mettre a jour `nb_collectes` ;
- si `nb_collectes == 31`, declencher cloture automatique.

Sortie :
- depot cree ;
- cycle mis a jour ;
- eventuelle cloture automatique.

### 12.4 Cas d'usage - Cloturer un cycle
Precondition :
- le cycle atteint `31` collectes.

Traitement :
- calculer total collecte ;
- calculer retenue ;
- calculer commission agent ;
- calculer commission institution ;
- calculer credit client ;
- creer retenue ;
- creer mouvements `RETENUE`, `COM_AGENT`, `COM_INSTITUTION`, `CREDIT_CLIENT` ;
- fermer le cycle.

Sortie :
- cycle cloture ;
- disponible client augmente.

### 12.5 Cas d'usage - Effectuer un retrait
Entree :
- client ;
- montant.

Traitement :
- verifier que le client existe ;
- verifier que le montant est positif ;
- calculer montant retirable ;
- refuser si insuffisant ;
- creer retrait ;
- creer mouvement `RETRAIT`.

Sortie :
- retrait enregistre ;
- disponible diminue.

## 13. Permissions detaillees

### 13.1 Verification de portefeuille
Regle importante :
- un agent ne doit pouvoir acceder qu'a ses propres clients, cycles et operations associees.

Doivent etre controles :
- detail client ;
- ouverture cycle ;
- creation depot ;
- creation retrait ;
- consultation historique.

### 13.2 Verifications admin
L'admin peut consulter l'ensemble des donnees et gerer les agents. Il ne doit toutefois pas contourner la coherence metier.

## 14. Strategie UI/UX par page

### 14.1 Dashboard Admin
Doit afficher de maniere synthese :
- nombre d'agents ;
- nombre de clients ;
- cycles en cours ;
- cycles clotures ;
- total commissions agents ;
- total retraits ;
- derniers mouvements.

### 14.2 Dashboard Agent
Doit afficher de maniere simple :
- nombre de mes clients ;
- cycles en cours ;
- cycles clotures ;
- montant retirable global de mon portefeuille si juge pertinent ;
- mes commissions ;
- dernieres actions utiles.

### 14.3 Detail Client
Doit afficher :
- infos client ;
- agent responsable ;
- montant retirable calcule ;
- liste des cycles ;
- historique recent ;
- actions principales.

### 14.4 Detail Cycle
Doit afficher :
- mise ;
- nb_collectes ;
- statut ;
- progression vers 31 ;
- depots associes ;
- mouvements associes ;
- action de depot si cycle en cours.

## 15. Messages utilisateur attendus
Exemples :
- `Client cree avec succes.`
- `Cycle ouvert avec succes.`
- `Depot enregistre avec succes.`
- `Le cycle a ete cloture automatiquement.`
- `Retrait enregistre avec succes.`
- `Impossible d'ajouter un depot sur un cycle cloture.`
- `Le montant retirable est insuffisant.`
- `Vous n'etes pas autorise a acceder a cette ressource.`

Regles :
- messages courts ;
- messages metier clairs ;
- pas de jargon technique ;
- affichage via toaster.

## 16. Confirmations utilisateur
SweetAlert2 ou equivalent doit etre utilise pour :
- confirmer un retrait ;
- confirmer une suppression logique ;
- confirmer une action irreversible ;
- confirmer une operation sensible d'administration.

## 17. Gestion des erreurs et logs

### 17.1 Gestion UI
- erreurs metier => toaster ou message lisible ;
- erreurs d'acces => page `403` ;
- ressource absente => page `404` ;
- erreur inattendue => page `500`.

### 17.2 Journalisation
Les logs doivent tracer au moins :
- erreurs applicatives inattendues ;
- refus de regles metier significatifs ;
- acces non autorises ;
- erreurs transactionnelles ;
- operations critiques utiles au diagnostic.

### 17.3 Emplacement
Prevoir un dossier :

```text
logs/
├── app.log
├── error.log
└── security.log
```

## 18. Plan de tables et calculs a figer
Le calcul du `montant_retirable` repose uniquement sur :
- total des `CREDIT_CLIENT`
- moins total des `RETRAIT`

Ce calcul doit etre disponible :
- dans un service ;
- idealement dans une vue SQL ou requete centralisee ;
- dans les ecrans de detail client et reporting.

## 19. Conception base de donnees renforcee

### 19.1 Principe
La base PostgreSQL ne doit pas servir uniquement a stocker les donnees. Elle doit aussi :
- proteger les invariants critiques ;
- centraliser certains calculs de reporting ;
- renforcer les operations financieres sensibles ;
- servir de second niveau de defense si l'interface ou un appel direct contourne l'application.

### 19.2 Contraintes SQL a prevoir
Contraintes minimales a mettre en place :
- `CHECK mise > 0`
- `CHECK mise % 100 = 0`
- `CHECK nb_collectes >= 0 AND nb_collectes <= 31`
- `CHECK statut IN ('EN_COURS', 'CLOTURE')`
- `CHECK nb_mises > 0`
- `CHECK montant > 0` pour depot, retrait, retenue et mouvement quand applicable
- `CHECK type IN ('MISE', 'RETENUE', 'COM_AGENT', 'COM_INSTITUTION', 'CREDIT_CLIENT', 'RETRAIT')`
- foreign keys obligatoires entre client, cycle, agent, depot, retrait, retenue et mouvement
- contraintes d'unicite sur les codes metier.

### 19.3 Index a prevoir
Index recommandes :
- index sur `client_id` dans `cycle`, `retrait`, `mouvement`
- index sur `agent_id` dans `client`, `depot`, `retrait`, `mouvement`
- index sur `cycle_id` dans `depot`, `retenue`, `mouvement`
- index sur `type` et `date_mouvement` dans `mouvement`
- index sur `statut` dans `cycle`
- index sur `deleted_at` si suppression logique utilisee dans les filtres standards.

## 20. Vues SQL de reporting

### 20.1 Objectif
Les vues SQL doivent simplifier les lectures metier et eviter de recalculer les agregats importants dans plusieurs endroits du code.

### 20.2 Vue prioritaire - montant retirable client
Vue cible :
- `v_client_montant_retirable`

Responsabilite :
- calculer le disponible retirable de chaque client a partir des mouvements.

Formule :
- `sum(CREDIT_CLIENT) - sum(RETRAIT)`

Usage :
- dashboard ;
- detail client ;
- page retraits ;
- reporting global admin.

### 20.3 Vue commissions agent
Vue cible :
- `v_agent_commissions`

Responsabilite :
- calculer le total des commissions agent via les mouvements `COM_AGENT`.

Usage :
- dashboard agent ;
- synthese admin ;
- detail agent si necessaire.

### 20.4 Vue resume cycles
Vue cible possible :
- `v_cycle_resume`

Responsabilite :
- exposer pour chaque cycle :
- client ;
- agent ;
- mise ;
- nb_collectes ;
- statut ;
- total collecte courant ;
- date ouverture ;
- date fermeture.

Usage :
- listes cycles ;
- detail cycle ;
- dashboard.

### 20.5 Vue historique financier enrichi
Vue cible possible :
- `v_financial_history`

Responsabilite :
- presenter un historique plus lisible en enrichissant les mouvements avec nom client, code cycle, agent et references utiles.

Usage :
- liste mouvements admin ;
- historique portefeuille agent.

## 21. Fonctions SQL metier critiques

### 21.1 Principe
Les fonctions SQL ne doivent pas remplacer toute la logique Django, mais elles peuvent securiser les traitements financiers critiques au plus pres des donnees.

Elles seront appelees via les services applicatifs Django.

### 21.2 Fonctions prioritaires

#### `get_montant_retirable(p_client_id)`
Responsabilite :
- retourner le montant retirable calcule d'un client.

Formule :
- `total(CREDIT_CLIENT) - total(RETRAIT)`

Usage :
- verification avant retrait ;
- affichage detail client ;
- reporting.

#### `create_depot(p_cycle_id, p_nb_mises, p_user_id)`
Responsabilite :
- verifier le cycle ;
- verifier qu'il est `EN_COURS` ;
- verifier que le depot ne depasse pas `31` collectes ;
- calculer le montant ;
- creer le depot ;
- creer le mouvement `MISE` ;
- mettre a jour `nb_collectes` ;
- declencher la cloture automatique si `31`.

Pourquoi c'est critique :
- c'est un point d'entree financier sensible ;
- il doit rester atomique ;
- aucune ecriture partielle ne doit subsister.

#### `close_cycle(p_cycle_id, p_user_id)`
Responsabilite :
- recalculer les montants de cloture ;
- creer la retenue ;
- creer `RETENUE`, `COM_AGENT`, `COM_INSTITUTION`, `CREDIT_CLIENT` ;
- renseigner la date de fermeture ;
- passer le cycle a `CLOTURE`.

Pourquoi c'est critique :
- cette fonction porte le coeur du calcul financier de fin de cycle.

#### `create_retrait(p_client_id, p_montant, p_user_id)`
Responsabilite :
- verifier que le montant est positif ;
- verifier le montant retirable disponible ;
- creer le retrait ;
- creer le mouvement `RETRAIT`.

Pourquoi c'est critique :
- le retrait impacte directement le disponible client ;
- il faut proteger contre tout solde negatif.

### 21.3 Strategie d'appel depuis Django
Les services Django doivent encapsuler les appels SQL.

Exemples d'appel cote infrastructure :
- `CycleService` ou `DepotService` appelle `create_depot(...)`
- `CycleService` appelle `close_cycle(...)` si necessaire
- `RetraitService` appelle `get_montant_retirable(...)` puis `create_retrait(...)`

Regle :
- l'interface n'appelle jamais directement la logique SQL ;
- les appels SQL passent toujours par la couche service/infrastructure.

## 22. Triggers et garde-fous complementaires

### 22.1 Principe
Les triggers doivent rester limites, explicites et justifies. Ils servent de filet de securite, pas de couche metier principale.

### 22.2 Triggers recommandes

#### `prevent_depot_on_closed_cycle`
But :
- empecher un enregistrement direct d'un depot sur un cycle cloture.

#### `validate_depot_limit`
But :
- refuser toute tentative qui ferait depasser `31` collectes.

#### `prevent_mouvement_update`
But :
- empecher la modification d'un mouvement financier historique.

#### `prevent_mouvement_delete`
But :
- empecher la suppression physique d'un mouvement.

#### `set_updated_at`
But :
- maintenir automatiquement `updated_at`.

### 22.3 Regles d'usage
- peu de triggers ;
- chacun doit etre testable ;
- chacun doit avoir une justification metier ou d'audit claire ;
- ne pas cacher une logique complexe dans des triggers opaques.

## 23. Migrations SQL et ordre technique

### 23.1 Ordre recommande
- `0001_initial` : tables principales
- `0002_constraints` : contraintes CHECK, FK et unicites complementaires
- `0003_views` : vues SQL de reporting
- `0004_functions` : fonctions SQL critiques
- `0005_triggers` : triggers de protection
- `0006_seed_demo` : jeu de donnees minimum

### 23.2 Regle de mise en oeuvre
Les vues, fonctions et triggers doivent etre crees via migrations versionnees, idealement avec `RunSQL`, afin de garantir :
- la reproductibilite ;
- la tracabilite ;
- la coherence entre code et base.

## 24. Traçabilite regles metier -> services -> SQL -> tests

### 24.1 Objectif
La conception detaillee doit aussi relier les regles a leur implementation technique.

### 24.2 Exemples de correspondance
- `RB-005` mise multiple de 100 -> `CycleService.validate_mise` + `CHECK mise % 100 = 0` + test refus mise invalide
- `RB-008` max 31 collectes -> `DepotService/create_depot` + `validate_depot_limit` + test depot depassement refuse
- `RB-011` cloture automatique a 31 -> `DepotService` + `create_depot/close_cycle` + test cloture automatique
- `RB-012` retenue egale a une mise -> `close_cycle` + test verification retenue
- `RB-013` partage 50/50 -> `close_cycle` + test commissions agent/institution
- `RB-015` montant retirable depuis mouvements -> `ReportingService/get_montant_retirable` + `v_client_montant_retirable` + test recalcul coherent
- `RB-016` retrait insuffisant refuse -> `RetraitService/create_retrait` + `get_montant_retirable/create_retrait` + test solde insuffisant
- `RB-018` depot sur cycle cloture refuse -> `DepotService` + `prevent_depot_on_closed_cycle` + test depot interdit

## 25. Ordre d'implementation recommande

### Phase 1 - Cadrage
- finaliser la documentation ;
- valider roles et pages ;
- figer la structure du projet.

### Phase 2 - Initialisation technique
- creer projet Django ;
- configurer PostgreSQL ;
- configurer Tailwind ;
- preparer settings, templates, static, logs.

### Phase 3 - Authentification et roles
- creer custom user ;
- creer role admin/agent ;
- gerer login, logout et redirection selon role.

### Phase 4 - Modeles et migrations
- implementer `Agent`, `Client`, `Cycle`, `Depot`, `Retenue`, `Retrait`, `Mouvement` ;
- ajouter champs d'audit ;
- creer migrations.

### Phase 5 - Domaine et services
- creer enums et exceptions ;
- implementer validations metier ;
- implementer services principaux ;
- ajouter transactions atomiques.

### Phase 6 - Interface de base
- layouts admin/agent ;
- composants reutilisables ;
- dashboards ;
- listes et details principaux.

### Phase 7 - Interactions UX
- integrer toaster ;
- integrer confirmations SweetAlert2 ;
- integrer pages d'erreur personnalisees.

### Phase 8 - Reporting et controle
- historique mouvements ;
- calculs synthese ;
- pages de supervision.

### Phase 9 - Logs et robustesse
- configurer logging ;
- journaliser les erreurs ;
- verifier les cas d'echec.

### Phase 10 - Tests
- tests metier ;
- tests services ;
- tests permissions ;
- tests cas limites ;
- scenario complet de bout en bout.

## 26. Checklist de pre-developpement
- les roles sont definis ;
- les pages sont listees ;
- les services sont identifies ;
- les entites sont stabilisees ;
- les composants sont recenses ;
- les cas d'usage sont decrits ;
- les vues SQL sont identifiees ;
- les fonctions SQL critiques sont listees ;
- les triggers utiles sont justifies ;
- la strategie de logs est definie ;
- les messages utilisateur sont identifies ;
- les actions sensibles a confirmer sont listees ;
- le plan d'implementation est valide.

## 27. Conclusion
Cette conception detaillee sert de pont entre la documentation generale et l'implementation.

Elle permet de commencer le projet avec une direction claire sur :
- ce qu'il faut construire ;
- comment le decouper ;
- comment separer `Admin` et `Agent` ;
- quels services metier ecrire ;
- quels renforts SQL et PostgreSQL mettre en place ;
- quelles pages et composants realiser ;
- dans quel ordre avancer.

La suite logique apres validation de ce document est la mise en place de l'ossature technique du projet.
