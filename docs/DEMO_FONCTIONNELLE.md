# DEMONSTRATION FONCTIONNELLE

## 1. Objectif
Ce document sert de guide rapide pour lancer l'application et tester fonctionnellement les principaux parcours.

## 2. Preparation
Appliquer les migrations si besoin :

```bash
.venv/bin/python manage.py migrate
```

Creer le jeu de demonstration :

```bash
.venv/bin/python manage.py seed_demo
```

Lancer l'application :

```bash
.venv/bin/python manage.py runserver
```

Connexion :
- URL : `http://127.0.0.1:8000/connexion/`

## 3. Comptes de demonstration
- Admin :
  - identifiant : `admin_demo`
  - mot de passe : `AdminDemo123!`
- Agent 1 :
  - identifiant : `agent_alpha`
  - mot de passe : `AgentDemo123!`
- Agent 2 :
  - identifiant : `agent_beta`
  - mot de passe : `AgentDemo123!`

## 4. Donnees de demonstration creees
- 1 administrateur ;
- 2 agents ;
- 3 clients ;
- 3 cycles ;
- 3 depots ;
- 1 retrait ;
- des mouvements generes automatiquement par les services ;
- au moins un cycle cloture pour voir :
  - la retenue ;
  - les commissions ;
  - le credit client ;
  - le montant retirable.

## 5. Parcours de demonstration recommande

### 5.1 Parcours Admin
1. Se connecter avec `admin_demo`.
2. Ouvrir le tableau de bord administrateur.
3. Verifier :
   - les compteurs agents, clients et cycles ;
   - les mouvements recents ;
   - la synthese commissions ;
   - les clients avec montant retirable.
4. Aller sur la liste des agents.
5. Ouvrir le detail d'un agent.
6. Verifier qu'un admin peut creer un nouvel agent via l'interface.

### 5.2 Parcours Agent
1. Se connecter avec `agent_alpha`.
2. Ouvrir le tableau de bord agent.
3. Verifier :
   - le portefeuille client ;
   - les cycles en cours et clotures ;
   - le retirable global ;
   - les commissions.
4. Ouvrir un client.
5. Ouvrir le detail du cycle.
6. Tester :
   - creation d'un nouveau client ;
   - ouverture d'un nouveau cycle ;
   - enregistrement d'un depot ;
   - tentative de retrait.

### 5.3 Parcours UX / securite
Verifier aussi :
- les toasts apres action ;
- les confirmations SweetAlert2 ;
- les refus d'acces entre espaces admin et agent ;
- les pages `403`, `404` et `500`.

## 6. Important
- les comptes agents sont bien crees par l'admin dans le fonctionnement normal de l'application ;
- le seed existe uniquement pour accelerer la demonstration et les tests fonctionnels ;
- sur PostgreSQL, ne pas lancer plusieurs suites de tests en parallele sur la meme base de test.

## 7. Nouveau parcours a verifier : cycles successifs et retrait special

### 7.1 Ouverture d'un nouveau cycle
1. Se connecter avec `agent_alpha`.
2. Ouvrir la fiche d'un client ayant deja un cycle `EN_COURS`.
3. Verifier que l'action propose `Voir le cycle en cours` et non pas l'ouverture d'un second cycle.
4. Cloturer le cycle normalement ou via retrait special.
5. Revenir sur la fiche client.
6. Verifier que l'action `Ouvrir un nouveau cycle` redevient disponible.

### 7.2 Retrait special / urgence
1. Se connecter avec `agent_alpha`.
2. Ouvrir un cycle avec au moins `2` collectes.
3. Depuis la fiche client ou le detail cycle, cliquer sur `Retrait special / urgence`.
4. Verifier que la page affiche :
   - le montant maximal autorise ;
   - la penalite egale a une mise ;
   - le rappel de la cloture anticipee.
5. Saisir un montant inferieur ou egal au maximum autorise.
6. Valider l'action.
7. Verifier apres retour sur la fiche client :
   - que le cycle est passe en `CLOTURE_ANTICIPEE` ;
   - qu'aucun depot supplementaire n'est possible sur ce cycle ;
   - que le reliquat eventuel apparait dans le `montant retirable` standard du client.

### 7.3 Verification admin
1. Se connecter avec `admin_demo`.
2. Ouvrir `Retraits` dans les flux financiers.
3. Verifier que la liste distingue :
   - les retraits `STANDARD` ;
   - les retraits `URGENCE` ;
   - le cycle associe lorsqu'il s'agit d'un retrait d'urgence.
