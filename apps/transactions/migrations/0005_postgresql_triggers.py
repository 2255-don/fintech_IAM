from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0004_postgresql_functions"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
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

            CREATE OR REPLACE FUNCTION transactions_validate_depot_limit()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_nb_collectes INTEGER;
            BEGIN
                SELECT nb_collectes
                INTO v_nb_collectes
                FROM cycles_cycle
                WHERE id = NEW.cycle_id;

                IF v_nb_collectes + NEW.nb_mises > 31 THEN
                    RAISE EXCEPTION 'Le cycle ne peut jamais depasser 31 collectes.';
                END IF;

                RETURN NEW;
            END;
            $$;

            CREATE OR REPLACE FUNCTION transactions_prevent_mouvement_update()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'Un mouvement financier historique ne peut pas etre modifie.';
            END;
            $$;

            CREATE OR REPLACE FUNCTION transactions_prevent_mouvement_delete()
            RETURNS TRIGGER
            LANGUAGE plpgsql
            AS $$
            BEGIN
                RAISE EXCEPTION 'Un mouvement financier historique ne peut pas etre supprime physiquement.';
            END;
            $$;

            DROP TRIGGER IF EXISTS trg_transactions_prevent_depot_on_closed_cycle ON transactions_depot;
            CREATE TRIGGER trg_transactions_prevent_depot_on_closed_cycle
            BEFORE INSERT OR UPDATE OF cycle_id ON transactions_depot
            FOR EACH ROW
            EXECUTE FUNCTION transactions_prevent_depot_on_closed_cycle();

            DROP TRIGGER IF EXISTS trg_transactions_validate_depot_limit ON transactions_depot;
            CREATE TRIGGER trg_transactions_validate_depot_limit
            BEFORE INSERT OR UPDATE OF nb_mises, cycle_id ON transactions_depot
            FOR EACH ROW
            EXECUTE FUNCTION transactions_validate_depot_limit();

            DROP TRIGGER IF EXISTS trg_transactions_prevent_mouvement_update ON transactions_mouvement;
            CREATE TRIGGER trg_transactions_prevent_mouvement_update
            BEFORE UPDATE ON transactions_mouvement
            FOR EACH ROW
            EXECUTE FUNCTION transactions_prevent_mouvement_update();

            DROP TRIGGER IF EXISTS trg_transactions_prevent_mouvement_delete ON transactions_mouvement;
            CREATE TRIGGER trg_transactions_prevent_mouvement_delete
            BEFORE DELETE ON transactions_mouvement
            FOR EACH ROW
            EXECUTE FUNCTION transactions_prevent_mouvement_delete();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS trg_transactions_prevent_mouvement_delete ON transactions_mouvement;
            DROP TRIGGER IF EXISTS trg_transactions_prevent_mouvement_update ON transactions_mouvement;
            DROP TRIGGER IF EXISTS trg_transactions_validate_depot_limit ON transactions_depot;
            DROP TRIGGER IF EXISTS trg_transactions_prevent_depot_on_closed_cycle ON transactions_depot;

            DROP FUNCTION IF EXISTS transactions_prevent_mouvement_delete();
            DROP FUNCTION IF EXISTS transactions_prevent_mouvement_update();
            DROP FUNCTION IF EXISTS transactions_validate_depot_limit();
            DROP FUNCTION IF EXISTS transactions_prevent_depot_on_closed_cycle();
            """,
        ),
    ]
