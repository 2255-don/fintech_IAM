from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cycles", "0001_initial"),
        ("transactions", "0005_postgresql_triggers"),
    ]

    operations = [
        migrations.AddField(
            model_name="retrait",
            name="cycle",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="retraits",
                to="cycles.cycle",
            ),
        ),
        migrations.AddField(
            model_name="retrait",
            name="type",
            field=models.CharField(
                choices=[("STANDARD", "Retrait standard"), ("URGENCE", "Retrait d'urgence")],
                default="STANDARD",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="mouvement",
            name="type",
            field=models.CharField(
                choices=[
                    ("MISE", "Mise"),
                    ("RETENUE", "Retenue"),
                    ("COM_AGENT", "Commission agent"),
                    ("COM_INSTITUTION", "Commission institution"),
                    ("CREDIT_CLIENT", "Credit client"),
                    ("RETRAIT", "Retrait"),
                    ("RETRAIT_URGENCE", "Retrait urgence"),
                    ("PENALITE_URGENCE", "Penalite urgence"),
                ],
                max_length=50,
            ),
        ),
        migrations.RunSQL(
            sql="""
            ALTER TABLE transactions_mouvement DROP CONSTRAINT IF EXISTS mouvement_type_valid;
            ALTER TABLE transactions_mouvement
            ADD CONSTRAINT mouvement_type_valid
            CHECK (type IN (
                'MISE',
                'RETENUE',
                'COM_AGENT',
                'COM_INSTITUTION',
                'CREDIT_CLIENT',
                'RETRAIT',
                'RETRAIT_URGENCE',
                'PENALITE_URGENCE'
            ));

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

            CREATE OR REPLACE FUNCTION transactions_get_montant_retirable(p_client_id BIGINT)
            RETURNS INTEGER
            LANGUAGE SQL
            STABLE
            AS $$
                SELECT COALESCE(montant_retirable, 0)::INTEGER
                FROM v_client_montant_retirable
                WHERE client_id = p_client_id
            $$;

            CREATE OR REPLACE FUNCTION transactions_create_retrait(
                p_client_id BIGINT,
                p_montant INTEGER,
                p_user_id BIGINT DEFAULT NULL,
                p_motif TEXT DEFAULT ''
            )
            RETURNS BIGINT
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_agent_id BIGINT;
                v_retrait_id BIGINT;
                v_code VARCHAR(50);
                v_montant_retirable INTEGER;
            BEGIN
                IF p_montant <= 0 THEN
                    RAISE EXCEPTION 'Le montant du retrait doit etre strictement positif.';
                END IF;

                SELECT agent_id
                INTO v_agent_id
                FROM clients_client
                WHERE id = p_client_id
                  AND deleted_at IS NULL;

                IF NOT FOUND THEN
                    RAISE EXCEPTION 'Le client selectionne est introuvable.';
                END IF;

                v_montant_retirable := transactions_get_montant_retirable(p_client_id);
                IF p_montant > v_montant_retirable THEN
                    RAISE EXCEPTION 'Le montant retirable est insuffisant.';
                END IF;

                v_code := format(
                    'RTT-SQL-%s-%s',
                    p_client_id,
                    to_char(clock_timestamp(), 'YYYYMMDDHH24MISSUS')
                );

                INSERT INTO transactions_retrait (
                    code,
                    client_id,
                    cycle_id,
                    agent_id,
                    type,
                    montant,
                    date_retrait,
                    motif,
                    created_at,
                    updated_at,
                    deleted_at,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                )
                VALUES (
                    v_code,
                    p_client_id,
                    NULL,
                    v_agent_id,
                    'STANDARD',
                    p_montant,
                    clock_timestamp(),
                    COALESCE(p_motif, ''),
                    clock_timestamp(),
                    clock_timestamp(),
                    NULL,
                    p_user_id,
                    p_user_id,
                    NULL
                )
                RETURNING id INTO v_retrait_id;

                INSERT INTO transactions_mouvement (
                    code,
                    client_id,
                    cycle_id,
                    agent_id,
                    type,
                    sens,
                    montant,
                    description,
                    reference_operation,
                    date_mouvement,
                    created_at,
                    updated_at,
                    deleted_at,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                )
                VALUES (
                    format('MVT-%s', v_code),
                    p_client_id,
                    NULL,
                    v_agent_id,
                    'RETRAIT',
                    'SORTIE',
                    p_montant,
                    'Retrait enregistre via fonction PostgreSQL.',
                    v_code,
                    clock_timestamp(),
                    clock_timestamp(),
                    clock_timestamp(),
                    NULL,
                    p_user_id,
                    p_user_id,
                    NULL
                );

                RETURN v_retrait_id;
            END;
            $$;

            CREATE OR REPLACE FUNCTION transactions_prevent_depot_on_closed_cycle()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_statut VARCHAR(30);
            BEGIN
                SELECT statut
                INTO v_statut
                FROM cycles_cycle
                WHERE id = NEW.cycle_id;

                IF v_statut IN ('CLOTURE', 'CLOTURE_ANTICIPEE') THEN
                    RAISE EXCEPTION 'Impossible d''enregistrer un depot sur un cycle cloture.';
                END IF;

                RETURN NEW;
            END;
            $$;
            """,
            reverse_sql="""
            ALTER TABLE transactions_mouvement DROP CONSTRAINT IF EXISTS mouvement_type_valid;
            ALTER TABLE transactions_mouvement
            ADD CONSTRAINT mouvement_type_valid
            CHECK (type IN ('MISE', 'RETENUE', 'COM_AGENT', 'COM_INSTITUTION', 'CREDIT_CLIENT', 'RETRAIT'));

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

            CREATE OR REPLACE FUNCTION transactions_get_montant_retirable(p_client_id BIGINT)
            RETURNS INTEGER
            LANGUAGE SQL
            STABLE
            AS $$
                SELECT COALESCE(montant_retirable, 0)::INTEGER
                FROM v_client_montant_retirable
                WHERE client_id = p_client_id
            $$;

            CREATE OR REPLACE FUNCTION transactions_create_retrait(
                p_client_id BIGINT,
                p_montant INTEGER,
                p_user_id BIGINT DEFAULT NULL,
                p_motif TEXT DEFAULT ''
            )
            RETURNS BIGINT
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_agent_id BIGINT;
                v_retrait_id BIGINT;
                v_code VARCHAR(50);
                v_montant_retirable INTEGER;
            BEGIN
                IF p_montant <= 0 THEN
                    RAISE EXCEPTION 'Le montant du retrait doit etre strictement positif.';
                END IF;

                SELECT agent_id
                INTO v_agent_id
                FROM clients_client
                WHERE id = p_client_id
                  AND deleted_at IS NULL;

                IF NOT FOUND THEN
                    RAISE EXCEPTION 'Le client selectionne est introuvable.';
                END IF;

                v_montant_retirable := transactions_get_montant_retirable(p_client_id);
                IF p_montant > v_montant_retirable THEN
                    RAISE EXCEPTION 'Le montant retirable est insuffisant.';
                END IF;

                v_code := format(
                    'RTT-SQL-%s-%s',
                    p_client_id,
                    to_char(clock_timestamp(), 'YYYYMMDDHH24MISSUS')
                );

                INSERT INTO transactions_retrait (
                    code,
                    client_id,
                    agent_id,
                    montant,
                    date_retrait,
                    motif,
                    created_at,
                    updated_at,
                    deleted_at,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                )
                VALUES (
                    v_code,
                    p_client_id,
                    v_agent_id,
                    p_montant,
                    clock_timestamp(),
                    COALESCE(p_motif, ''),
                    clock_timestamp(),
                    clock_timestamp(),
                    NULL,
                    p_user_id,
                    p_user_id,
                    NULL
                )
                RETURNING id INTO v_retrait_id;

                INSERT INTO transactions_mouvement (
                    code,
                    client_id,
                    cycle_id,
                    agent_id,
                    type,
                    sens,
                    montant,
                    description,
                    reference_operation,
                    date_mouvement,
                    created_at,
                    updated_at,
                    deleted_at,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                )
                VALUES (
                    format('MVT-%s', v_code),
                    p_client_id,
                    NULL,
                    v_agent_id,
                    'RETRAIT',
                    'SORTIE',
                    p_montant,
                    'Retrait enregistre via fonction PostgreSQL.',
                    v_code,
                    clock_timestamp(),
                    clock_timestamp(),
                    clock_timestamp(),
                    NULL,
                    p_user_id,
                    p_user_id,
                    NULL
                );

                RETURN v_retrait_id;
            END;
            $$;

            CREATE OR REPLACE FUNCTION transactions_prevent_depot_on_closed_cycle()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_statut VARCHAR(30);
            BEGIN
                SELECT statut
                INTO v_statut
                FROM cycles_cycle
                WHERE id = NEW.cycle_id;

                IF v_statut = 'CLOTURE' THEN
                    RAISE EXCEPTION 'Impossible d''enregistrer un depot sur un cycle cloture.';
                END IF;

                RETURN NEW;
            END;
            $$;
            """,
        ),
    ]
