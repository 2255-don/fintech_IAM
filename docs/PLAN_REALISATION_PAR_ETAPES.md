# PLAN DE REALISATION PAR ETAPES

## Projet Fintech-IAM
### Methode de realisation incremental, documentee et testee

## 1. Objet du document
Ce document definit la methode officielle de realisation du projet.

Le projet ne sera pas implemente d'un seul bloc. Il sera construit par etapes successives.

Chaque etape devra etre :
- concue ;
- implementee ;
- testee ;
- documentee ;
- tracee.

L'objectif est d'obtenir un projet propre, maitrisable et defendable, avec une preuve claire de ce qui a ete fait a chaque phase.

## 2. Principe de travail retenu
Pour chaque etape du projet, on devra produire :
- le code correspondant ;
- les tests correspondants ;
- la documentation correspondante ;
- la liste des fichiers crees ou modifies ;
- l'explication du role de chaque element important ajoute ;
- les regles metier couvertes ;
- les limites ou points a finaliser si necessaire.

Autrement dit, chaque etape doit pouvoir etre relue et comprise de maniere autonome.

## 3. Structure de sortie attendue a chaque fin d'etape
Chaque etape devra laisser une trace documentaire avec au minimum :

### 3.1 Contenu attendu
- objectif de l'etape ;
- perimetre traite ;
- decisions prises ;
- fichiers crees ;
- fichiers modifies ;
- fonctions, classes, services ou composants ajoutes ;
- raison de leur creation ;
- regles metier couvertes ;
- tests ajoutes ;
- resultat des tests ;
- points restant a faire.

### 3.2 Format documentaire recommande
Dans `docs/etapes/`, chaque etape pourra avoir un document dedie du type :

```text
docs/
└── etapes/
    ├── ETAPE_01_CADRAGE_ET_OSSATURE.md
    ├── ETAPE_02_AUTH_ET_ROLES.md
    ├── ETAPE_03_MODELES_ET_MIGRATIONS.md
    ├── ETAPE_04_LOGIQUE_METIER_CYCLES_DEPOTS.md
    ├── ETAPE_05_RETRAITS_MOUVEMENTS_REPORTING.md
    ├── ETAPE_06_INTERFACES_ADMIN_AGENT.md
    ├── ETAPE_07_UX_LOGS_ERREURS.md
    └── ETAPE_08_FINALISATION_TESTS_DEMO.md
```

Chaque document d'etape devra expliquer clairement ce qui a ete fait.

## 4. Cycle de travail pour chaque etape
Pour chaque etape, on suivra toujours la meme logique :

1. definir l'objectif exact de l'etape ;
2. definir le perimetre fonctionnel et technique ;
3. implementer uniquement ce perimetre ;
4. ajouter les tests lies a ce perimetre ;
5. verifier le resultat ;
6. documenter ce qui a ete realise ;
7. valider l'etape avant de passer a la suivante.

## 5. Regle importante de progression
On ne doit pas avancer a l'etape suivante si l'etape en cours n'est pas suffisamment :
- claire ;
- stable ;
- testee ;
- documentee.

Cela permet :
- d'eviter la dette technique ;
- d'eviter les oublis documentaires ;
- d'avoir une trace defendable du travail ;
- de garder une progression propre.

## 6. Enumeration des etapes de realisation

## Etape 1 - Cadrage final et ossature du projet

### Objectif
Mettre en place la base de travail technique et organisationnelle du projet.

### Contenu
- valider la documentation existante ;
- creer l'ossature initiale du projet Django ;
- preparer le dossier `docs/` ;
- preparer le dossier `logs/` ;
- preparer la structure initiale `apps/`, `templates/`, `static/` ;
- configurer les dependances de base ;
- preparer l'environnement de travail.

### Livrables attendus
- structure initiale du projet ;
- fichier de dependances ;
- configuration initiale ;
- documentation d'etape 1 ;
- premiers tests de demarrage si necessaire.

### Documentation de fin d'etape
Le document devra preciser :
- l'arborescence creee ;
- les fichiers de base crees ;
- le role de chaque dossier principal ;
- les choix techniques de depart.

## Etape 2 - Authentification et gestion des roles

### Objectif
Mettre en place la gestion des utilisateurs, des roles et des acces de base.

### Contenu
- creer le `CustomUser` ;
- definir les roles `ADMIN` et `AGENT` ;
- gerer la connexion/deconnexion ;
- gerer la redirection selon role ;
- preparer la base du profil agent ;
- poser les premieres restrictions d'acces.

### Livrables attendus
- model utilisateur ;
- eventuel model agent initial ou app agent prete ;
- vues d'authentification ;
- templates d'auth ;
- tests des roles et acces.

### Documentation de fin d'etape
Le document devra decrire :
- les modeles crees ;
- les champs ajoutes ;
- les vues/fichiers d'authentification ;
- les regles de redirection ;
- les tests de permissions ajoutes.

## Etape 3 - Modeles metier et migrations initiales

### Objectif
Mettre en place les entites principales du domaine et leurs relations.

### Contenu
- creer `Agent` ;
- creer `Client` ;
- creer `Cycle` ;
- creer `Depot` ;
- creer `Retenue` ;
- creer `Retrait` ;
- creer `Mouvement` ;
- ajouter champs d'audit ;
- creer les migrations initiales.

### Livrables attendus
- modeles ORM principaux ;
- relations et contraintes de base ;
- migrations ;
- documentation des entites et de leurs responsabilites ;
- tests de creation de base des modeles si utiles.

### Documentation de fin d'etape
Le document devra indiquer :
- les fichiers modeles crees ;
- les champs importants ;
- les relations ;
- le pourquoi de chaque entite ;
- ce qui est stocke et ce qui est recalcule.

## Etape 4 - Regles metier de base des clients et cycles

### Objectif
Implementer les premieres regles metier stables autour des clients et cycles.

### Contenu
- creation client via service ;
- ouverture de cycle via service ;
- validations sur la mise ;
- statut initial du cycle ;
- nombre initial de collectes ;
- exceptions metier de base.

### Livrables attendus
- `ClientService` ;
- `CycleService` ;
- regles de validation metier ;
- tests sur creation client et cycle ;
- documentation des services et regles associees.

### Documentation de fin d'etape
Le document devra preciser :
- les services crees ;
- les fonctions importantes ;
- les regles couvertes ;
- les tests metier correspondants.

## Etape 5 - Depots et cloture automatique des cycles

### Objectif
Implementer la logique critique de depot et de cloture automatique.

### Contenu
- creation d'un depot ;
- calcul du montant depot ;
- incrementation des collectes ;
- refus des depassements ;
- refus sur cycle cloture ;
- cloture automatique a 31 collectes ;
- creation de la retenue ;
- creation des mouvements de cloture ;
- passage du cycle a `CLOTURE`.

### Livrables attendus
- `DepotService` ;
- logique de cloture ;
- fonctions de calcul associees ;
- tests critiques sur depots et cloture ;
- documentation technique de la logique critique.

### Documentation de fin d'etape
Le document devra indiquer :
- les services/fonctions crees ;
- les calculs implementes ;
- les cas limites traites ;
- les tests de validation critique.

## Etape 6 - Retraits, montant retirable et reporting financier

### Objectif
Implementer la logique de retrait et les calculs de consultation financiere.

### Contenu
- calcul du montant retirable ;
- retrait global ;
- refus si solde insuffisant ;
- creation mouvement `RETRAIT` ;
- vues ou requetes de reporting ;
- synthese commissions agent ;
- historique financier exploitable.

### Livrables attendus
- `RetraitService` ;
- `ReportingService` ;
- eventuelles vues SQL ;
- tests de calcul du retirable ;
- documentation des calculs et du reporting.

### Documentation de fin d'etape
Le document devra preciser :
- les formules retenues ;
- les fonctions/services ajoutes ;
- les vues SQL ou requetes centralisees ;
- les tests de coherence financiere.

## Etape 7 - Renforcement PostgreSQL

### Objectif
Ajouter les mecanismes SQL critiques demandes dans la documentation technique.

### Contenu
- contraintes SQL complementaires ;
- vues SQL de reporting ;
- fonctions SQL critiques ;
- triggers de protection utiles ;
- migrations `RunSQL`.

### Livrables attendus
- scripts/migrations SQL ;
- documentation des vues, fonctions et triggers ;
- tests d'integration base de donnees.

### Documentation de fin d'etape
Le document devra expliquer :
- chaque vue SQL creee ;
- chaque fonction SQL creee ;
- chaque trigger cree ;
- le pourquoi de chaque ajout ;
- les fichiers/migrations concernes ;
- les tests associes.

## Etape 8 - Interfaces Admin et Agent

### Objectif
Construire les interfaces principales separees par role.

### Contenu
- layouts `Admin` et `Agent` ;
- dashboard admin ;
- dashboard agent ;
- listes et details essentiels ;
- formulaires principaux ;
- navigation claire par espace.

### Livrables attendus
- templates ;
- vues Django ;
- formulaires ;
- composants reutilisables ;
- documentation UI/UX d'etape.

### Documentation de fin d'etape
Le document devra preciser :
- les pages creees ;
- les composants reutilisables crees ;
- le role de chaque vue/page ;
- le decoupage admin/agent ;
- les fichiers templates/forms/views ajoutes.

## Etape 9 - UX, confirmations, messages, logs et pages d'erreur

### Objectif
Professionnaliser l'experience utilisateur et la gestion des erreurs.

### Contenu
- flash messages ;
- toaster ;
- confirmations SweetAlert2 ;
- pages `403`, `404`, `500` ;
- configuration des logs ;
- journalisation des erreurs et evenements critiques.

### Livrables attendus
- composants/messages UI ;
- configuration logging ;
- pages d'erreur ;
- documentation d'observabilite et UX.

### Documentation de fin d'etape
Le document devra decrire :
- les messages et interactions ajoutes ;
- les fichiers de config modifies ;
- les logs mis en place ;
- les pages d'erreur creees ;
- les cas testes.

## Etape 10 - Finalisation, tests globaux et preparation demo

### Objectif
Stabiliser le projet et preparer une version presentable et defendable.

### Contenu
- jeu de donnees minimum ;
- tests de bout en bout ;
- revue des regles metier couvertes ;
- verification de la tracabilite ;
- nettoyage final du code ;
- finalisation documentation.

### Livrables attendus
- jeu de demonstration ;
- rapport de tests final ;
- documentation finale de synthese ;
- liste des fonctionnalites effectivement realisees.

### Documentation de fin d'etape
Le document devra indiquer :
- le scenario de demonstration ;
- les donnees de demo ;
- les tests finaux executes ;
- les points couverts ;
- les limites restantes eventuelles.

## 7. Regle documentaire a respecter pendant tout le projet
Chaque document d'etape devra aussi contenir une section du type :

### Fichiers crees
- liste des fichiers crees

### Fichiers modifies
- liste des fichiers modifies

### Elements fonctionnels ajoutes
- services
- fonctions
- vues
- formulaires
- composants
- migrations

### Pourquoi ces elements ont ete crees
- justification simple et claire

### Regles metier couvertes
- liste des regles traitees dans l'etape

### Tests ajoutes
- liste des tests

### Resultat des tests
- reussi / echoue / a completer

## 8. Regle de tracabilite
Le projet doit rester traçable a tout moment.

Cela signifie qu'on doit toujours pouvoir repondre a ces questions :
- qu'est-ce qui a ete fait ?
- dans quels fichiers ?
- pourquoi ?
- quelle regle metier cela couvre ?
- quel test le prouve ?

## 9. Conclusion
La suite logique n'est donc pas seulement de "coder", mais de realiser le projet par blocs fermes et documentes.

Cette approche nous permettra :
- de garder le controle ;
- de produire une documentation defendable ;
- de respecter la logique Spec-Driven ;
- d'eviter la dette technique ;
- de justifier clairement chaque ajout technique et metier.

## 10. Prochaine etape immediate
La premiere etape concrete a lancer est :

`Etape 1 - Cadrage final et ossature du projet`

Cette etape posera les bases du projet avant l'implementation metier.

## 11. Extension fonctionnelle documentee
Une evolution transverse a ete ajoutee apres les etapes initiales afin de couvrir un besoin metier complementaire important :
- cycles successifs pour un meme client ;
- impossibilite d'avoir plusieurs cycles `EN_COURS` ;
- retrait d'urgence avec cloture anticipee ;
- reliquat eventuel converti en disponible client.

Trace documentaire associee :
- `docs/etapes/ETAPE_11_CYCLES_SUCCESSIFS_ET_RETRAIT_URGENCE.md`

Cette extension respecte le meme cadre de realisation :
- regles metier explicites ;
- implementation service-first ;
- interface agent adaptee ;
- migrations PostgreSQL alignees ;
- tests automatises dedies.
