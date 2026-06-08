from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE cycles_cycle
            ADD CONSTRAINT cycle_mise_multiple_100
            CHECK (mise % 100 = 0);

            ALTER TABLE transactions_mouvement
            ADD CONSTRAINT mouvement_type_valid
            CHECK (type IN ('MISE', 'RETENUE', 'COM_AGENT', 'COM_INSTITUTION', 'CREDIT_CLIENT', 'RETRAIT'));

            ALTER TABLE transactions_mouvement
            ADD CONSTRAINT mouvement_sens_valid
            CHECK (sens IN ('ENTREE', 'SORTIE', 'INFO'));

            CREATE INDEX IF NOT EXISTS idx_transactions_mouvement_client_type_active
            ON transactions_mouvement (client_id, type)
            WHERE deleted_at IS NULL;

            CREATE INDEX IF NOT EXISTS idx_transactions_mouvement_agent_type_active
            ON transactions_mouvement (agent_id, type)
            WHERE deleted_at IS NULL;

            CREATE INDEX IF NOT EXISTS idx_transactions_mouvement_cycle_type_active
            ON transactions_mouvement (cycle_id, type)
            WHERE deleted_at IS NULL;

            CREATE INDEX IF NOT EXISTS idx_cycles_cycle_statut_active
            ON cycles_cycle (statut)
            WHERE deleted_at IS NULL;
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS idx_cycles_cycle_statut_active;
            DROP INDEX IF EXISTS idx_transactions_mouvement_cycle_type_active;
            DROP INDEX IF EXISTS idx_transactions_mouvement_agent_type_active;
            DROP INDEX IF EXISTS idx_transactions_mouvement_client_type_active;

            ALTER TABLE transactions_mouvement DROP CONSTRAINT IF EXISTS mouvement_sens_valid;
            ALTER TABLE transactions_mouvement DROP CONSTRAINT IF EXISTS mouvement_type_valid;
            ALTER TABLE cycles_cycle DROP CONSTRAINT IF EXISTS cycle_mise_multiple_100;
            """,
        ),
    ]
