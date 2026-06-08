from django.contrib.auth import get_user_model
from django.db import DatabaseError, connection
from django.test import TestCase, TransactionTestCase

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.models import Mouvement, MouvementType, Retrait, RetraitType
from apps.transactions.services import DepotService, EmergencyWithdrawalService, ReportingService, RetraitService


User = get_user_model()


class PostgreSQLViewsAndFunctionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_sql_views",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Aya",
            last_name="Diallo",
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0700")
        self.client = Client.objects.create(
            code="CLI-2026-0700",
            agent=self.agent,
            nom="Toure",
            prenom="Awa",
            telephone="70000001",
        )
        self.cycle = Cycle.objects.create(
            code="CYC-2026-0700",
            client=self.client,
            mise=1000,
        )
        DepotService.create_depot(
            code="DEP-2026-0700",
            cycle_id=self.cycle.id,
            nb_mises=31,
            created_by=self.user,
        )

    def test_sql_view_client_montant_retirable_matches_service(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT total_credit_client, total_retraits, montant_retirable
                FROM v_client_montant_retirable
                WHERE client_id = %s
                """,
                [self.client.id],
            )
            row = cursor.fetchone()

        self.assertEqual(tuple(int(value) for value in row), (30000, 0, 30000))
        self.assertEqual(ReportingService.get_montant_retirable(client_id=self.client.id), 30000)

    def test_sql_view_agent_commissions_returns_expected_total(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT total_commissions, nb_commissions
                FROM v_agent_commissions
                WHERE agent_id = %s
                """,
                [self.agent.id],
            )
            row = cursor.fetchone()

        self.assertEqual(tuple(int(value) for value in row), (500, 1))

    def test_sql_view_cycle_resume_returns_expected_values(self):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT mise, nb_collectes, statut, total_collecte_courant
                FROM v_cycle_resume
                WHERE cycle_id = %s
                """,
                [self.cycle.id],
            )
            row = cursor.fetchone()

        self.assertEqual((int(row[0]), int(row[1]), row[2], int(row[3])), (1000, 31, "CLOTURE", 31000))

    def test_sql_function_create_retrait_is_used_by_service(self):
        retrait = RetraitService.create_retrait(
            client_id=self.client.id,
            montant=5000,
            created_by=self.user,
            motif="Retrait SQL",
        )

        self.assertTrue(Retrait.objects.filter(id=retrait.id).exists())
        self.assertEqual(retrait.type, RetraitType.STANDARD)
        self.assertTrue(retrait.code.startswith("RTT-SQL-"))
        self.assertTrue(
            Mouvement.objects.filter(
                reference_operation=retrait.code,
                type=MouvementType.RETRAIT,
                montant=5000,
            ).exists()
        )
        self.assertEqual(ReportingService.get_montant_retirable(client_id=self.client.id), 25000)

    def test_emergency_withdrawal_does_not_break_retirable_sql_view(self):
        open_cycle = Cycle.objects.create(
            code="CYC-2026-0701",
            client=self.client,
            mise=1000,
            nb_collectes=20,
            statut=CycleStatus.EN_COURS,
        )

        result = EmergencyWithdrawalService.create_emergency_withdrawal(
            cycle_id=open_cycle.id,
            montant=10000,
            created_by=self.user,
            motif="SQL urgence",
        )

        self.assertEqual(result.credit_client, 9000)
        self.assertEqual(ReportingService.get_montant_retirable(client_id=self.client.id), 39000)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT total_credit_client, total_retraits, montant_retirable
                FROM v_client_montant_retirable
                WHERE client_id = %s
                """,
                [self.client.id],
            )
            row = cursor.fetchone()
        self.assertEqual(tuple(int(value) for value in row), (39000, 0, 39000))


class PostgreSQLTriggerProtectionTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_sql_triggers",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Fatou",
            last_name="Keita",
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0800")
        self.client = Client.objects.create(
            code="CLI-2026-0800",
            agent=self.agent,
            nom="Ba",
            prenom="Mina",
            telephone="70000002",
        )
        self.open_cycle = Cycle.objects.create(
            code="CYC-2026-0800",
            client=self.client,
            mise=1000,
            nb_collectes=30,
        )
        self.closed_cycle = Cycle.objects.create(
            code="CYC-2026-0801",
            client=self.client,
            mise=1000,
            nb_collectes=31,
            statut=CycleStatus.CLOTURE,
        )
        self.early_closed_cycle = Cycle.objects.create(
            code="CYC-2026-0802",
            client=self.client,
            mise=1000,
            nb_collectes=20,
            statut=CycleStatus.CLOTURE_ANTICIPEE,
        )
        self.mouvement = Mouvement.objects.create(
            code="MVT-2026-0800",
            client=self.client,
            cycle=self.open_cycle,
            agent=self.agent,
            type=MouvementType.MISE,
            sens="ENTREE",
            montant=1000,
            reference_operation="DEP-2026-0800",
            created_by=self.user,
            updated_by=self.user,
        )

    def _execute(self, sql: str, params: list) -> None:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)

    def test_trigger_prevents_depot_on_closed_cycle(self):
        with self.assertRaises(DatabaseError):
            self._execute(
                """
                INSERT INTO transactions_depot (
                    created_at,
                    updated_at,
                    deleted_at,
                    code,
                    nb_mises,
                    montant,
                    date_depot,
                    agent_id,
                    client_id,
                    cycle_id,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                ) VALUES (
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    NULL,
                    'DEP-SQL-CLOSED-0800',
                    1,
                    1000,
                    CURRENT_TIMESTAMP,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NULL
                )
                """,
                [self.agent.id, self.client.id, self.closed_cycle.id, self.user.id, self.user.id],
            )
        connection.rollback()

    def test_trigger_prevents_depot_on_early_closed_cycle(self):
        with self.assertRaises(DatabaseError):
            self._execute(
                """
                INSERT INTO transactions_depot (
                    created_at,
                    updated_at,
                    deleted_at,
                    code,
                    nb_mises,
                    montant,
                    date_depot,
                    agent_id,
                    client_id,
                    cycle_id,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                ) VALUES (
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    NULL,
                    'DEP-SQL-EARLY-0800',
                    1,
                    1000,
                    CURRENT_TIMESTAMP,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NULL
                )
                """,
                [self.agent.id, self.client.id, self.early_closed_cycle.id, self.user.id, self.user.id],
            )
        connection.rollback()

    def test_trigger_prevents_depot_limit_overflow(self):
        with self.assertRaises(DatabaseError):
            self._execute(
                """
                INSERT INTO transactions_depot (
                    created_at,
                    updated_at,
                    deleted_at,
                    code,
                    nb_mises,
                    montant,
                    date_depot,
                    agent_id,
                    client_id,
                    cycle_id,
                    created_by_id,
                    updated_by_id,
                    deleted_by_id
                ) VALUES (
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP,
                    NULL,
                    'DEP-SQL-LIMIT-0800',
                    2,
                    2000,
                    CURRENT_TIMESTAMP,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    NULL
                )
                """,
                [self.agent.id, self.client.id, self.open_cycle.id, self.user.id, self.user.id],
            )
        connection.rollback()

    def test_trigger_prevents_mouvement_update(self):
        with self.assertRaises(DatabaseError):
            self._execute(
                "UPDATE transactions_mouvement SET montant = %s WHERE id = %s",
                [2000, self.mouvement.id],
            )
        connection.rollback()
