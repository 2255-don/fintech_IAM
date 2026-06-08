# DOCUMENTATION TECHNIQUE ENRICHIE

## Projet Fintech-IAM
### Gestion de tontine numerique
### Architecture Spec-Driven avec Django, Tailwind CSS et PostgreSQL

## 1. Objet du document
Ce document constitue la reference officielle de conception et de realisation du projet `Fintech-IAM`.

Il a pour objectif de :
- cadrer le projet fonctionnellement et techniquement ;
- formaliser les regles metier et les regles de realisation ;
- definir l'architecture cible ;
- encadrer les choix UI/UX ;
- imposer des principes anti-dette-technique ;
- guider la conception, l'implementation, les tests et la demonstration finale.

Ce projet ne doit pas etre traite comme un simple CRUD. Il s'agit d'un noyau applicatif financier simple mais rigoureux, dans lequel chaque montant important doit etre justifiable par l'historique des mouvements.

## 2. Contexte et objectif du projet
Fintech-IAM est une application de gestion de tontine numerique inspiree d'un cas metier reel.

Le systeme doit permettre de gerer :
- les agents ;
- les clients ;
- les cycles d'epargne ;
- les depots ;
- la cloture automatique d'un cycle ;
- le calcul des commissions ;
- le retrait global d'un client ;
- l'historique financier sous forme de mouvements.

Le principe directeur est le suivant :

`L'interface sert a saisir et afficher. La couche metier decide, valide, calcule et protege les donnees.`

## 3. Approche Spec-Driven retenue
La demarche Spec-Driven impose la chaine de travail suivante :

`Besoin metier -> Regles metier -> Modele de donnees -> Logique metier -> Protections BD -> Tests -> Preuve`

Cela implique que :
- toute regle metier importante doit etre ecrite explicitement ;
- toute regle critique doit avoir une traduction identifiable dans le code ;
- toute regle critique doit etre couverte par au moins un test ;
- aucune operation financiere ne doit dependre uniquement de l'interface ;
- tout montant affiche doit pouvoir etre justifie depuis les donnees persistantes.

## 4. Cadrage fonctionnel

### 4.1 Probleme resolu
L'application permet a une institution de tontine de suivre les clients et leurs cycles d'epargne, d'enregistrer les depots, de cloturer automatiquement les cycles a la 31e collecte, de distribuer les retenues, et de calculer de maniere fiable le montant retirable des clients.

### 4.2 Utilisateurs concernes
- `ADMIN` : supervision globale, gestion des agents, consultation complete du systeme.
- `AGENT` : gestion operationnelle de son portefeuille client, de ses cycles, de ses depots et des retraits lies a son perimetre.

### 4.3 Perimetre inclus
- gestion des agents ;
- authentification ;
- gestion des clients ;
- ouverture de cycle ;
- enregistrement de depots ;
- cloture automatique ;
- calcul de retenue et commissions ;
- retrait global ;
- historique financier ;
- dashboard et pages de consultation ;
- messages utilisateur ;
- journalisation des erreurs et evenements critiques ;
- tests metier et techniques.

### 4.4 Perimetre exclu
- integration mobile money ou API bancaire ;
- comptabilite institutionnelle complete ;
- multi-agence complexe ;
- notifications SMS ou e-mail ;
- gestion avancee de workflow de validation multi-niveaux ;
- reporting analytique avance hors besoins du sujet.

## 5. Glossaire metier
- `Agent` : utilisateur operationnel qui gere un portefeuille de clients.
- `Client` : personne rattachee a un agent et pouvant posseder un ou plusieurs cycles.
- `Cycle` : periode d'epargne structuree autour d'une mise fixe.
- `Mise` : montant unitaire choisi pour un cycle. Elle doit etre positive et multiple de 100 FCFA.
- `Collecte` : unite logique correspondant a une mise.
- `Depot` : versement effectue dans un cycle, correspondant a une ou plusieurs mises.
- `Retenue` : montant preleve a la cloture d'un cycle, egal a une mise.
- `Commission agent` : moitie de la retenue attribuee a l'agent.
- `Commission institution` : moitie de la retenue attribuee a l'institution.
- `Credit client` : montant rendu disponible au client apres cloture du cycle.
- `Retrait` : montant retire par le client depuis son disponible.
- `Montant retirable` : montant calculable a partir des mouvements `CREDIT_CLIENT - RETRAIT`.
- `Mouvement` : trace financiere horodatee d'une operation metier.

## 6. Regles metier officielles

### 6.1 Regles principales
- `RB-001` Un agent peut gerer plusieurs clients.
- `RB-002` Un client appartient a un agent responsable.
- `RB-003` Un client peut avoir plusieurs cycles d'epargne.
- `RB-004` Une mise doit etre positive.
- `RB-005` Une mise doit etre un multiple de 100 FCFA.
- `RB-006` Un cycle commence avec `0` collecte.
- `RB-007` Un cycle demarre avec le statut `EN_COURS`.
- `RB-008` Un cycle ne peut jamais depasser `31` collectes.
- `RB-009` Un depot augmente le nombre de collectes.
- `RB-010` Un depot cree un mouvement `MISE`.
- `RB-011` Un cycle atteignant `31` collectes est cloture automatiquement.
- `RB-012` La retenue de cloture est egale a une mise.
- `RB-013` La retenue est partagee `50 % / 50 %` entre agent et institution.
- `RB-014` Le credit client est enregistre dans les mouvements financiers.
- `RB-015` Le montant retirable est calcule par `total(CREDIT_CLIENT) - total(RETRAIT)`.
- `RB-016` Un retrait global est refuse si le montant retirable calcule est insuffisant.
- `RB-017` Les montants financiers sont manipules en entiers FCFA.
- `RB-018` Un cycle cloture ne peut plus accepter de depot.
- `RB-019` Les operations financieres critiques doivent etre transactionnelles.
- `RB-020` Les donnees financieres doivent etre auditables.

### 6.2 Invariants metier
Les invariants suivants doivent etre vrais en permanence :
- `mise > 0`
- `mise % 100 == 0`
- `0 <= nb_collectes <= 31`
- `statut in {EN_COURS, CLOTURE}`
- `montant_depot = mise * nb_mises`
- `nb_mises > 0`
- `retenue = mise`
- `commission_agent = retenue / 2`
- `commission_institution = retenue / 2`
- `commission_agent + commission_institution = retenue`
- `credit_client = total_collecte - retenue`
- `montant_retirable = sum(CREDIT_CLIENT) - sum(RETRAIT)`
- `cycle cloture => aucun nouveau depot autorise`
- `aucune ecriture financiere partielle ne doit subsister apres erreur`

### 6.3 Etats et transitions
Etat du cycle :
- `EN_COURS`
- `CLOTURE`

Transitions autorisees :
- `creation -> EN_COURS`
- `EN_COURS -> CLOTURE` quand `nb_collectes == 31`

Transitions interdites :
- `CLOTURE -> EN_COURS`
- depot sur cycle `CLOTURE`
- toute operation qui ferait passer `nb_collectes > 31`

## 7. Types de mouvements financiers
Les types minimaux obligatoires sont :
- `MISE`
- `RETENUE`
- `COM_AGENT`
- `COM_INSTITUTION`
- `CREDIT_CLIENT`
- `RETRAIT`

### 7.1 Signification
- `MISE` : mouvement cree a chaque depot valide.
- `RETENUE` : mouvement cree a la cloture pour materialiser la retenue.
- `COM_AGENT` : part agent issue de la retenue.
- `COM_INSTITUTION` : part institution issue de la retenue.
- `CREDIT_CLIENT` : disponible cree au profit du client.
- `RETRAIT` : reduction du disponible client suite a retrait.

### 7.2 Formule officielle
- `montantDepot = mise * nbMises`
- `totalCollecte = mise * 31`
- `retenue = mise`
- `commissionAgent = retenue / 2`
- `commissionInstitution = retenue / 2`
- `creditClient = totalCollecte - retenue`
- `montantRetirable = total(CREDIT_CLIENT) - total(RETRAIT)`

## 8. Stack technique retenue
- `Backend` : Django
- `Frontend` : Django Templates + Tailwind CSS + JavaScript leger
- `Base de donnees` : PostgreSQL
- `Tests` : pytest / pytest-django ou Django TestCase
- `Notifications UI` : Flash messages + toaster
- `Confirmations UI` : SweetAlert2
- `Logs` : logging Django vers fichiers de logs

### 8.1 Justification
- Django permet un decoupage propre `views / forms / services / models`.
- PostgreSQL permet de renforcer les regles critiques avec contraintes, vues et transactions.
- Tailwind CSS permet une interface moderne et legere.
- SweetAlert2 permet des confirmations utilisateur propres pour actions sensibles.
- Le systeme de logs permet de retrouver rapidement les erreurs sans les exposer aux utilisateurs.

## 9. Principes de realisation du projet

### 9.1 Regles generales
- Respecter strictement le sujet demande.
- Ne pas ajouter de fonctionnalites hors perimetre sans justification.
- Concevoir d'abord le metier, ensuite l'interface.
- Rechercher la simplicite defendable plutot que la sophistication inutile.
- Ecrire du code lisible, testable et maintenable.

### 9.2 Regles anti-dette-technique
- Eviter toute dette technique evitable des le depart.
- Ne pas dupliquer la logique metier.
- Ne pas creer de structures temporaires destinees a rester.
- Ne pas stocker une donnee qui doit etre recalculable a partir de l'historique.
- Ne pas creer des helpers vagues, inutiles, ou non reutilises.
- Ne pas sur-abstraire.
- Ne pas ajouter de complexite "au cas ou".

### 9.3 Regles sur les helpers et reutilisation
- Un helper ne doit exister que s'il clarifie une logique ou evite une repetition reelle.
- Toute abstraction doit etre justifiable par au moins deux usages ou un fort besoin de lisibilite.
- Preferer des services metier explicites a une proliferation d'utilitaires generiques.
- Mutualiser la presentation UI via composants reutilisables simples.

### 9.4 Regles de qualite de code
- Nommer les classes, fonctions et variables avec un vocabulaire metier clair.
- Eviter les fonctions trop longues.
- Une fonction doit avoir une responsabilite principale.
- Separer nettement interface, metier, infrastructure et presentation.
- Toute regle metier doit etre localisable rapidement.

## 10. Architecture generale cible

### 10.1 Principe
L'architecture doit etre decoupee en couches clairement identifiables :
- interface web ;
- formulaires ;
- services applicatifs ;
- domaine metier ;
- models ORM ;
- infrastructure SQL ;
- base PostgreSQL ;
- tests.

### 10.2 Repartition des responsabilites
- `Templates` : affichage, navigation, lisibilite.
- `Views` : orchestration web, appel des services, choix de la reponse.
- `Forms` : validation de saisie simple.
- `Services` : orchestration metier et transactionnelle.
- `Domaine` : regles pures, enums, exceptions metier.
- `Models` : persistance et relations.
- `PostgreSQL` : garde-fous de donnees, vues de calcul, contraintes.
- `Tests` : preuve du respect des regles.

## 11. Organisation des dossiers recommandee

```text
specDriven/
├── README.md
├── requirements.txt
├── .env.example
├── manage.py
├── docs/
│   ├── 01_cadrage_metier.md
│   ├── 02_regles_metier.md
│   ├── 03_glossaire_invariants.md
│   ├── 04_modele_donnees.md
│   ├── 05_architecture_technique.md
│   ├── 06_ui_ux_et_parcours.md
│   ├── 07_tracabilite_regles_code_tests.md
│   └── 08_rapport_tests.md
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

### 11.1 Observation de conception
Le projet doit rester simple. Un decoupage par sous-domaines metier peut etre prefere si cela garde le code plus lisible que de tout mettre dans une seule app.

## 12. Modele de donnees cible

### 12.1 Entites minimales
- `User`
- `Agent`
- `Client`
- `Cycle`
- `Depot`
- `Retenue`
- `Retrait`
- `Mouvement`

### 12.2 Relations principales
- `User 1 --- 0..1 Agent`
- `Agent 1 --- N Client`
- `Client 1 --- N Cycle`
- `Cycle 1 --- N Depot`
- `Cycle 1 --- 0..1 Retenue`
- `Client 1 --- N Retrait`
- `Client 1 --- N Mouvement`
- `Cycle 1 --- N Mouvement`
- `Agent 1 --- N Mouvement`

### 12.3 Regles de stockage
- `montant_retirable` ne doit pas etre stocke comme source de verite.
- `montant_retirable` doit etre recalculable depuis les mouvements.
- `nb_collectes` est une donnee stockee et mise a jour de maniere controlee.
- `montant` d'un depot est stocke comme valeur historique calculee.
- les mouvements doivent toujours permettre de reconstituer les calculs majeurs.

## 13. Conventions de codification
Chaque entite metier peut recevoir un code lisible :
- `AG-2026-0001`
- `CLI-2026-0001`
- `CYC-2026-0001`
- `DEP-2026-0001`
- `RET-2026-0001`
- `RTT-2026-0001`
- `MVT-2026-0001`

Objectif :
- faciliter l'audit ;
- rendre les tests plus lisibles ;
- avoir des references metier parlantes.

## 14. Audit, suppression logique et tracabilite
Toutes les tables metier doivent inclure des champs d'audit standards :
- `created_at`
- `updated_at`
- `deleted_at`
- `created_by`
- `updated_by`
- `deleted_by`

Regles :
- les donnees financieres ne doivent pas etre supprimees physiquement en fonctionnement normal ;
- la suppression logique doit etre privilegiee ;
- les mouvements doivent rester auditables ;
- les erreurs et actions critiques doivent etre tracables.

## 15. Strategie transactionnelle
Les operations suivantes doivent etre atomiques :
- creation d'un depot ;
- cloture d'un cycle ;
- creation d'un retrait.

Cela signifie :
- si une sous-etape echoue, toute l'operation est annulee ;
- aucune ecriture partielle ne doit subsister ;
- les mouvements et entites associees doivent rester coherents.

Operations a proteger en priorite :
- `create_depot`
- `close_cycle`
- `create_retrait`

## 16. Catalogue d'erreurs metier
Des exceptions metier explicites doivent etre definies. Exemples :
- `BusinessRuleError`
- `AgentNotFoundError`
- `ClientNotFoundError`
- `CycleNotFoundError`
- `InvalidMiseError`
- `InvalidNbMisesError`
- `CycleClosedError`
- `CollecteLimitExceededError`
- `InsufficientRetirableAmountError`
- `UnauthorizedPortfolioAccessError`

Objectif :
- faciliter les tests ;
- produire des messages utilisateurs clairs ;
- separer erreurs metier et erreurs techniques.

## 17. Permissions et perimetres par role

### 17.1 ADMIN
Peut :
- creer et gerer les agents ;
- consulter tous les clients ;
- consulter tous les cycles, depots, retraits et mouvements ;
- visualiser les tableaux de bord globaux ;
- acceder a l'administration technique si prevu.

### 17.2 AGENT
Peut :
- consulter ses clients ;
- creer un client dans son portefeuille si la regle retenue l'autorise ;
- ouvrir un cycle pour son client ;
- enregistrer un depot ;
- consulter les mouvements lies a son portefeuille ;
- initier ou enregistrer un retrait dans son perimetre autorise.

Ne peut pas :
- consulter l'ensemble du systeme hors de son portefeuille ;
- gerer les agents ;
- contourner les validations metier ;
- agir sur des clients non rattaches a son portefeuille.

## 18. Regles UI/UX officielles

### 18.1 Principes generaux
- L'interface doit etre moderne, simple, claire et agreable.
- Les pages doivent etre legeres et faciles a comprendre.
- Il ne faut pas vouloir tout mettre dans une seule page.
- Le projet doit separer proprement les espaces `Admin` et `Agent`.
- Les parcours doivent etre fluides, parlants et centres sur les actions reelles.

### 18.2 Decoupage des interfaces
Ne pas faire une page unique surchargee.

Prevoir au minimum :
- un dashboard `Admin` ;
- un dashboard `Agent` ;
- une page liste agents ;
- une page liste clients ;
- une page detail client ;
- une page ouverture de cycle ;
- une page detail cycle ;
- une page enregistrement de depot ;
- une page retrait ;
- une page historique des mouvements ;
- des pages d'erreur personnalisees.

### 18.3 Composants reutilisables
Le projet doit utiliser un systeme de composants de presentation reutilisables, par exemple :
- layout principal ;
- sidebar ;
- topbar ;
- cartes statistiques ;
- tableaux standardises ;
- badges de statut ;
- blocs de formulaire ;
- boutons d'action ;
- modales ou confirmations ;
- composants d'alertes et messages.

Objectif :
- eviter de reecrire la meme structure partout ;
- alleger les pages ;
- garder une UI coherente ;
- faciliter les evolutions.

### 18.4 Design et experience
- Utiliser un design moderne et propre.
- Ajouter de petites animations utiles et discretes.
- Soigner les etats vides, les etats d'erreur et les retours visuels.
- Utiliser des libelles metier clairs et parlants.
- Rechercher une experience `user-friendly`, fluide et fun sans perdre le serieux du contexte financier.

## 19. Retours utilisateur et interactions

### 19.1 Flash messages et toaster
Chaque action importante doit produire un retour utilisateur visible :
- succes ;
- erreur metier ;
- avertissement ;
- information.

Regles :
- utiliser les `flash messages` Django ;
- les afficher via une UI de type toaster ;
- ne jamais laisser l'utilisateur sans retour apres une action.

### 19.2 Confirmations utilisateur
Les actions sensibles doivent demander confirmation avant execution, idealement via `SweetAlert2`.

Actions concernees en priorite :
- suppression logique ;
- cloture manuelle si un cas existe ;
- retrait ;
- action irreversible ;
- operation impactant les donnees financieres.

Objectif :
- reduire les erreurs de manipulation ;
- rendre l'interface plus sure et plus professionnelle.

## 20. Gestion des erreurs et observabilite

### 20.1 Regles de gestion d'erreur
- Ne jamais afficher une erreur technique brute a l'utilisateur.
- Transformer les erreurs metier en messages comprehensibles.
- Journaliser les erreurs techniques dans les logs.
- Afficher des pages d'erreur personnalisees pour les cas adequats.

### 20.2 Pages d'erreur dediees
Prevoir au minimum :
- `403` acces refuse ;
- `404` page ou ressource introuvable ;
- `500` erreur interne.

Ces pages doivent :
- etre coherentes avec l'identite visuelle ;
- rester comprehensibles ;
- ne pas exposer de details techniques sensibles.

### 20.3 Strategie de logs
Le projet doit disposer d'une journalisation claire.

Niveaux minimaux :
- `INFO`
- `WARNING`
- `ERROR`

Les logs doivent permettre de retrouver :
- les erreurs inattendues ;
- les refus metier importants ;
- les operations critiques ;
- le contexte minimal utile au diagnostic.

Exemples d'evenements a tracer :
- tentative de retrait insuffisant ;
- depot refuse pour depassement ;
- erreur transactionnelle ;
- erreur serveur inattendue ;
- acces non autorise a un portefeuille client.

## 21. Contraintes PostgreSQL et garde-fous BD
La base doit renforcer les invariants critiques.

Exemples de protections :
- `CHECK mise > 0`
- `CHECK mise % 100 = 0`
- `CHECK nb_collectes BETWEEN 0 AND 31`
- `CHECK statut IN ('EN_COURS', 'CLOTURE')`
- `CHECK type IN (...)` pour les mouvements
- foreign keys obligatoires ;
- index utiles ;
- transactions sur operations critiques.

La base de donnees ne remplace pas la logique metier, mais elle doit empecher les incoherences majeures.

## 22. Vues SQL et calculs de reporting
Des vues SQL peuvent etre utilisees pour les calculs de consultation.

Vue prioritaire :
- `v_client_montant_retirable`

Autres vues possibles :
- total commissions agent ;
- resume des cycles ;
- historique financier enrichi.

But :
- centraliser les calculs de consultation ;
- eviter la duplication ;
- garder des ecrans de consultation simples.

## 23. Flux metier principaux

### 23.1 Creer un client
Formulaire -> validation simple -> service metier -> verification agent -> creation client -> message de succes.

### 23.2 Ouvrir un cycle
Formulaire -> validation mise -> creation cycle avec `nb_collectes=0` et `statut=EN_COURS`.

### 23.3 Enregistrer un depot
Formulaire -> validation nombre de mises -> verification cycle -> creation depot -> creation mouvement `MISE` -> mise a jour collectes -> cloture auto si `31`.

### 23.4 Cloturer automatiquement un cycle
Detection de `31` collectes -> retenue -> commissions -> credit client -> mouvements -> passage a `CLOTURE`.

### 23.5 Effectuer un retrait
Saisie montant -> calcul du disponible -> refus ou creation retrait -> mouvement `RETRAIT` -> message utilisateur.

### 23.6 Consulter les donnees
Lecture des listes, details, historiques et calculs via pages dediees et dashboard adapte au role.

## 24. Cas limites a couvrir
- creation de cycle avec mise negative ;
- creation de cycle avec mise non multiple de 100 ;
- depot de `1` mise sur un cycle a `30` collectes ;
- depot de `2` mises sur un cycle a `30` collectes ;
- depot sur cycle cloture ;
- retrait de `0` ;
- retrait superieur au disponible ;
- retrait egal au disponible exact ;
- client sans mouvement ;
- cycle ouvert sans depot ;
- acces agent a un client ne lui appartenant pas.

## 25. Strategie de tests

### 25.1 Niveaux de test
- tests de domaine ;
- tests de services ;
- tests d'integration base de donnees ;
- tests de permissions ;
- tests UI minimaux si necessaire.

### 25.2 Scenarios obligatoires
- creer un cycle avec une mise de `1 000 FCFA` -> accepte ;
- creer un cycle avec une mise de `1 050 FCFA` -> refuse ;
- depot de `5` mises -> nb_collectes augmente de `5` ;
- depot depassant `31` collectes -> refuse ;
- atteindre exactement `31` collectes -> cloture automatique ;
- verifier la cloture pour mise `1 000 FCFA` -> retenue `1 000`, agent `500`, institution `500`, retirable `30 000` ;
- depot sur cycle cloture -> refuse ;
- retrait superieur au disponible -> refuse ;
- retrait valide -> accepte et montant retirable diminue ;
- recalcul du montant retirable depuis les mouvements -> coherent ;
- verification des restrictions de role `AGENT` / `ADMIN`.

### 25.3 Rapport de test
Chaque test ou scenario documente doit indiquer :
- le scenario ;
- les donnees utilisees ;
- le resultat attendu ;
- le resultat obtenu ;
- le statut.

## 26. Mini-tracabilite regle -> code -> test
Un tableau de tracabilite devra etre maintenu pendant le developpement.

Exemples :
- `RB-005` mise multiple de 100 -> `CycleService` + contrainte SQL -> test de refus
- `RB-008` max 31 collectes -> `DepotService` + validation/transaction -> test de depassement refuse
- `RB-011` cloture auto -> `DepotService/CloseCycleService` -> test d'atteinte exacte a 31
- `RB-015` montant retirable depuis mouvements -> `ReportingService/vue SQL` -> test de recalcul
- `RB-018` depot sur cycle cloture refuse -> service + garde-fou BD -> test dedie

## 27. Jeu de donnees minimum
- un agent `Agent IAM 1` ;
- un compte agent associe ;
- un client `Aminata TRAORE` ;
- un cycle pour ce client avec mise `1 000 FCFA` ;
- un scenario complet totalisant `31` collectes ;
- un retrait global apres cloture.

## 28. Plan de developpement recommande
Ordre conseille :
- finaliser le cadrage documentaire ;
- figer les regles du projet ;
- valider l'architecture et le modele de donnees ;
- definir les pages `Admin` et `Agent` ;
- mettre en place la structure Django ;
- implementer authentification et roles ;
- implementer les models et migrations ;
- ajouter les protections PostgreSQL utiles ;
- implementer les services metier ;
- implementer les ecrans principaux ;
- mettre en place toaster, confirmations et pages d'erreur ;
- configurer les logs ;
- ecrire les tests ;
- preparer les donnees de demonstration.

## 29. Checklist de validation avant implementation
- les regles metier sont completes ;
- le glossaire est valide ;
- les invariants sont identifies ;
- le modele de donnees est coherent ;
- les roles `ADMIN` et `AGENT` sont definis ;
- les flux metier sont clairs ;
- la strategie transactionnelle est fixee ;
- les pages principales sont listees ;
- les composants reutilisables sont identifies ;
- la gestion d'erreur est definie ;
- la strategie de logs est definie ;
- les tests obligatoires sont recenses.

## 30. Conclusion
Le projet Fintech-IAM doit etre realise comme une application metier rigoureuse, claire et defendable.

La priorite absolue est :
- la coherence des regles metier ;
- la tracabilite financiere ;
- la qualite du decoupage technique ;
- la simplicite de l'experience utilisateur ;
- l'absence de dette technique inutile.

La ligne directrice de tout le projet doit rester :

`Regles metier d'abord, base et services ensuite, interface propre enfin.`
