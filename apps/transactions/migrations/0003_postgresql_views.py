from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0002_postgresql_constraints"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW v_client_montant_retirable AS
            SELECT
                c.id AS client_id,
                c.agent_id AS agent_id,
                c.code AS client_code,
                TRIM(CONCAT(c.nom, ' ', COALESCE(c.prenom, ''))) AS client_nom_complet,
                COALESCE(SUM(CASE WHEN m.type = 'CREDIT_CLIENT' THEN m.montant ELSE 0 END), 0) AS total_credit_client,
                COALESCE(SUM(CASE WHEN m.type = 'RETRAIT' THEN m.montant ELSE 0 END), 0) AS total_retraits,
                COALESCE(SUM(CASE
                    WHEN m.type = 'CREDIT_CLIENT' THEN m.montant
                    WHEN m.type = 'RETRAIT' THEN -m.montant
                    ELSE 0
                END), 0) AS montant_retirable
            FROM clients_client c
            LEFT JOIN transactions_mouvement m
                ON m.client_id = c.id
                AND m.deleted_at IS NULL
            WHERE c.deleted_at IS NULL
            GROUP BY c.id, c.agent_id, c.code, c.nom, c.prenom;

            CREATE OR REPLACE VIEW v_agent_commissions AS
            SELECT
                a.id AS agent_id,
                a.code AS agent_code,
                COALESCE(SUM(CASE WHEN m.type = 'COM_AGENT' THEN m.montant ELSE 0 END), 0) AS total_commissions,
                COALESCE(SUM(CASE WHEN m.type = 'COM_AGENT' THEN 1 ELSE 0 END), 0) AS nb_commissions
            FROM agents_agent a
            LEFT JOIN transactions_mouvement m
                ON m.agent_id = a.id
                AND m.deleted_at IS NULL
            WHERE a.deleted_at IS NULL
            GROUP BY a.id, a.code;

            CREATE OR REPLACE VIEW v_cycle_resume AS
            SELECT
                cy.id AS cycle_id,
                cy.code AS cycle_code,
                cy.client_id AS client_id,
                cl.code AS client_code,
                cl.agent_id AS agent_id,
                ag.code AS agent_code,
                cy.mise AS mise,
                cy.nb_collectes AS nb_collectes,
                cy.statut AS statut,
                (cy.mise * cy.nb_collectes) AS total_collecte_courant,
                cy.date_ouverture AS date_ouverture,
                cy.date_fermeture AS date_fermeture
            FROM cycles_cycle cy
            INNER JOIN clients_client cl ON cl.id = cy.client_id
            INNER JOIN agents_agent ag ON ag.id = cl.agent_id
            WHERE cy.deleted_at IS NULL
              AND cl.deleted_at IS NULL
              AND ag.deleted_at IS NULL;
            """,
            reverse_sql="""
            DROP VIEW IF EXISTS v_cycle_resume;
            DROP VIEW IF EXISTS v_agent_commissions;
            DROP VIEW IF EXISTS v_client_montant_retirable;
            """,
        ),
    ]
