from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0003_postgresql_views"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
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
            """,
            reverse_sql="""
            DROP FUNCTION IF EXISTS transactions_create_retrait(BIGINT, INTEGER, BIGINT, TEXT);
            DROP FUNCTION IF EXISTS transactions_get_montant_retirable(BIGINT);
            """,
        ),
    ]
