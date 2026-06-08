# DEPANNAGE LOCAL POSTGRESQL

## 1. Contexte
Lors de la reprise des validations du projet `fintech_IAM`, les tests PostgreSQL ne pouvaient plus se lancer.

Symptomes observes :
- `pg_isready -h 127.0.0.1 -p 5432` retourne `no response` ;
- `manage.py test ...` echoue avec `psycopg.OperationalError: connection is bad` ;
- `pg_lsclusters` indique que le cluster `18/main` est `down`.

Diagnostic releve sur la machine :
- le repertoire de donnees PostgreSQL appartient a `nobody:nogroup` ;
- le cluster liste par `pg_lsclusters` ressort aussi avec `Owner = nobody`.

Etat constate :

```text
Ver Cluster Port Status Owner  Data directory              Log file
18  main    5432 down   nobody /var/lib/postgresql/18/main /var/log/postgresql/postgresql-18-main.log
```

Et sur le filesystem :

```text
/var/lib/postgresql            -> nobody:nogroup
/var/lib/postgresql/18         -> nobody:nogroup
/var/lib/postgresql/18/main    -> nobody:nogroup
```

## 2. Cause probable
Le cluster a ete initialise ou modifie avec de mauvais proprietaires systeme.

PostgreSQL attend normalement :
- utilisateur systeme `postgres` ;
- groupe `postgres` ;
- permissions strictes sur le dossier `main`.

Tant que ces proprietaires ne sont pas corriges, le service ne peut pas etre redemarre proprement et le projet Django ne peut pas recreer sa base de test.

## 3. Commandes de remise en etat
Executer localement sur la machine :

```bash
sudo chown -R postgres:postgres /var/lib/postgresql
sudo chown -R postgres:postgres /var/log/postgresql
sudo pg_ctlcluster 18 main start
pg_lsclusters
pg_isready -h 127.0.0.1 -p 5432
```

Le resultat attendu apres correction :

```text
18  main  5432  online  postgres  /var/lib/postgresql/18/main ...
127.0.0.1:5432 - accepting connections
```

## 4. Verification de connexion applicative
Une fois le cluster reparti :

```bash
PGPASSWORD=123456 psql -h 127.0.0.1 -U postgres -d fintech_iam -c "SELECT current_database(), current_user;"
```

Resultat attendu :
- connexion OK sur `fintech_iam` ;
- utilisateur `postgres`.

## 5. Relance des validations du projet
Apres remise en etat PostgreSQL, relancer dans le projet :

```bash
.venv/bin/python manage.py test apps.accounts apps.core apps.transactions --noinput
.venv/bin/python -m pytest -p no:cacheprovider apps/accounts apps/core apps/transactions
```

Important :
- execution sequentielle recommande sur PostgreSQL ;
- ne pas lancer simultanement plusieurs suites qui partagent la base de test.

## 6. Pourquoi ce document existe
Ce document permet de garder la tracabilite d'un blocage d'environnement qui n'est pas un bug metier du projet, mais qui empeche la preuve par tests demandee par notre methode de realisation.

## 7. Etat apres reprise
La connectivite PostgreSQL a pu etre retablie et les validations du projet sont passees correctement a condition de respecter une regle importante :
- ne jamais lancer plusieurs suites de tests PostgreSQL en parallele sur `test_fintech_iam`.

Validation confirmee ensuite :
- `manage.py test apps.core --noinput` : OK ;
- `manage.py test apps.transactions --noinput` : OK ;
- `pytest -p no:cacheprovider apps/accounts apps/core apps/transactions` : `46 passed`.
