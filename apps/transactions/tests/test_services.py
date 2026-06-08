from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.core.exceptions import (
    CollecteLimitExceededError,
    CycleClosedError,
    EmergencyWithdrawalAmountExceededError,
    EmergencyWithdrawalNotAllowedError,
    InvalidNbMisesError,
    InsufficientRetirableAmountError,
)
from apps.cycles.models import Cycle, CycleStatus
from apps.transactions.models import Mouvement, MouvementType, Retenue, Retrait, RetraitType
from apps.transactions.services import DepotService, EmergencyWithdrawalService, ReportingService, RetraitService


User = get_user_model()


class DepotServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_depot_service",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Moussa",
            last_name="Camara",
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0500")
        self.client = Client.objects.create(
            code="CLI-2026-0500",
            agent=self.agent,
            nom="Barry",
            prenom="Nene",
            telephone="78000000",
        )
        self.cycle = Cycle.objects.create(
            code="CYC-2026-0500",
            client=self.client,
            mise=1000,
        )

    def test_create_depot_updates_collectes_and_creates_mise_mouvement(self):
        depot = DepotService.create_depot(
            code="DEP-2026-0500",
            cycle_id=self.cycle.id,
            nb_mises=5,
            created_by=self.user,
        )

        self.cycle.refresh_from_db()

        self.assertEqual(depot.montant, 5000)
        self.assertEqual(self.cycle.nb_collectes, 5)
        self.assertTrue(
            Mouvement.objects.filter(
                reference_operation=depot.code,
                type=MouvementType.MISE,
                montant=5000,
            ).exists()
        )

    def test_create_depot_rejects_invalid_nb_mises(self):
        with self.assertRaises(InvalidNbMisesError):
            DepotService.create_depot(
                code="DEP-2026-0501",
                cycle_id=self.cycle.id,
                nb_mises=0,
                created_by=self.user,
            )

    def test_create_depot_rejects_collecte_limit_overflow(self):
        self.cycle.nb_collectes = 30
        self.cycle.save(update_fields=["nb_collectes"])

        with self.assertRaises(CollecteLimitExceededError):
            DepotService.create_depot(
                code="DEP-2026-0502",
                cycle_id=self.cycle.id,
                nb_mises=2,
                created_by=self.user,
            )

    def test_create_depot_closes_cycle_at_31_and_creates_financial_records(self):
        depot = DepotService.create_depot(
            code="DEP-2026-0503",
            cycle_id=self.cycle.id,
            nb_mises=31,
            created_by=self.user,
        )

        self.cycle.refresh_from_db()

        self.assertEqual(depot.montant, 31000)
        self.assertEqual(self.cycle.nb_collectes, 31)
        self.assertEqual(self.cycle.statut, CycleStatus.CLOTURE)
        retenue = Retenue.objects.get(cycle=self.cycle)
        self.assertEqual(retenue.montant, 1000)
        self.assertEqual(retenue.commission_agent, 500)
        self.assertEqual(retenue.commission_institution, 500)
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.RETENUE, montant=1000).exists())
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.COM_AGENT, montant=500).exists())
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.COM_INSTITUTION, montant=500).exists())
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.CREDIT_CLIENT, montant=30000).exists())

    def test_create_depot_rejects_closed_cycle(self):
        self.cycle.statut = CycleStatus.CLOTURE
        self.cycle.save(update_fields=["statut"])

        with self.assertRaises(CycleClosedError):
            DepotService.create_depot(
                code="DEP-2026-0504",
                cycle_id=self.cycle.id,
                nb_mises=1,
                created_by=self.user,
            )

    def test_create_depot_rejects_early_closed_cycle(self):
        self.cycle.statut = CycleStatus.CLOTURE_ANTICIPEE
        self.cycle.save(update_fields=["statut"])

        with self.assertRaises(CycleClosedError):
            DepotService.create_depot(
                code="DEP-2026-0505",
                cycle_id=self.cycle.id,
                nb_mises=1,
                created_by=self.user,
            )


class ReportingAndRetraitServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_retrait_service",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Kadi",
            last_name="Fofana",
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0600")
        self.client = Client.objects.create(
            code="CLI-2026-0600",
            agent=self.agent,
            nom="Cisse",
            prenom="Mariam",
            telephone="79000000",
        )
        self.cycle = Cycle.objects.create(
            code="CYC-2026-0600",
            client=self.client,
            mise=1000,
        )
        DepotService.create_depot(
            code="DEP-2026-0600",
            cycle_id=self.cycle.id,
            nb_mises=31,
            created_by=self.user,
        )

    def test_reporting_service_returns_expected_montant_retirable(self):
        montant_retirable = ReportingService.get_montant_retirable(client_id=self.client.id)

        self.assertEqual(montant_retirable, 30000)

    def test_reporting_service_returns_client_financial_summary(self):
        summary = ReportingService.get_client_financial_summary(client_id=self.client.id)

        self.assertEqual(summary["client_code"], "CLI-2026-0600")
        self.assertEqual(summary["agent_code"], "AG-2026-0600")
        self.assertEqual(summary["montant_retirable"], 30000)
        self.assertEqual(summary["total_credit_client"], 30000)
        self.assertEqual(summary["total_retraits"], 0)

    def test_retrait_service_creates_retrait_and_mouvement(self):
        retrait = RetraitService.create_retrait(
            client_id=self.client.id,
            montant=5000,
            created_by=self.user,
            motif="Besoin personnel",
        )

        self.assertTrue(Retrait.objects.filter(id=retrait.id).exists())
        self.assertEqual(retrait.type, RetraitType.STANDARD)
        self.assertTrue(
            Mouvement.objects.filter(
                reference_operation=retrait.code,
                type=MouvementType.RETRAIT,
                montant=5000,
            ).exists()
        )
        self.assertEqual(ReportingService.get_montant_retirable(client_id=self.client.id), 25000)

    def test_retrait_service_refuses_amount_greater_than_retirable(self):
        with self.assertRaises(InsufficientRetirableAmountError):
            RetraitService.create_retrait(
                client_id=self.client.id,
                montant=40000,
                created_by=self.user,
            )

    def test_retrait_service_refuses_non_positive_amount(self):
        with self.assertRaises(InsufficientRetirableAmountError):
            RetraitService.create_retrait(
                client_id=self.client.id,
                montant=0,
                created_by=self.user,
            )


class EmergencyWithdrawalServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_retrait_urgence",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Mina",
            last_name="Traore",
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0900")
        self.client = Client.objects.create(
            code="CLI-2026-0900",
            agent=self.agent,
            nom="Sacko",
            prenom="Aicha",
            telephone="76000000",
        )
        self.cycle = Cycle.objects.create(
            code="CYC-2026-0900",
            client=self.client,
            mise=1000,
            nb_collectes=20,
            statut=CycleStatus.EN_COURS,
        )

    def test_emergency_withdrawal_closes_cycle_and_splits_penalty(self):
        result = EmergencyWithdrawalService.create_emergency_withdrawal(
            cycle_id=self.cycle.id,
            montant=19000,
            motif="Urgence familiale",
            created_by=self.user,
        )

        self.cycle.refresh_from_db()

        self.assertEqual(self.cycle.statut, CycleStatus.CLOTURE_ANTICIPEE)
        self.assertEqual(result.penalite, 1000)
        self.assertEqual(result.commission_agent, 500)
        self.assertEqual(result.commission_institution, 500)
        self.assertEqual(result.credit_client, 0)
        self.assertEqual(result.retrait.type, RetraitType.URGENCE)
        self.assertEqual(result.retrait.cycle, self.cycle)
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.RETRAIT_URGENCE, montant=19000).exists())
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.PENALITE_URGENCE, montant=1000).exists())
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.COM_AGENT, montant=500).exists())
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.COM_INSTITUTION, montant=500).exists())
        self.assertEqual(ReportingService.get_montant_retirable(client_id=self.client.id), 0)

    def test_emergency_withdrawal_can_leave_remaining_credit(self):
        result = EmergencyWithdrawalService.create_emergency_withdrawal(
            cycle_id=self.cycle.id,
            montant=10000,
            motif="Besoin partiel",
            created_by=self.user,
        )

        self.assertEqual(result.credit_client, 9000)
        self.assertTrue(Mouvement.objects.filter(cycle=self.cycle, type=MouvementType.CREDIT_CLIENT, montant=9000).exists())
        self.assertEqual(ReportingService.get_montant_retirable(client_id=self.client.id), 9000)

    def test_emergency_withdrawal_refuses_amount_greater_than_allowed(self):
        with self.assertRaises(EmergencyWithdrawalAmountExceededError):
            EmergencyWithdrawalService.create_emergency_withdrawal(
                cycle_id=self.cycle.id,
                montant=19500,
                created_by=self.user,
            )

    def test_emergency_withdrawal_refuses_cycle_with_less_than_two_collectes(self):
        self.cycle.nb_collectes = 1
        self.cycle.save(update_fields=["nb_collectes"])

        with self.assertRaises(EmergencyWithdrawalNotAllowedError):
            EmergencyWithdrawalService.create_emergency_withdrawal(
                cycle_id=self.cycle.id,
                montant=500,
                created_by=self.user,
            )

    def test_emergency_withdrawal_refuses_closed_cycle(self):
        self.cycle.statut = CycleStatus.CLOTURE
        self.cycle.save(update_fields=["statut"])

        with self.assertRaises(EmergencyWithdrawalNotAllowedError):
            EmergencyWithdrawalService.create_emergency_withdrawal(
                cycle_id=self.cycle.id,
                montant=1000,
                created_by=self.user,
            )
