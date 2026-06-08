from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.cycles.models import Cycle
from apps.transactions.models import (
    Depot,
    Mouvement,
    MouvementSens,
    MouvementType,
    Retenue,
    Retrait,
)


User = get_user_model()


class TransactionModelsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_tx_owner",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Mariam",
            last_name="Sow",
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0003")
        self.client = Client.objects.create(
            code="CLI-2026-0003",
            agent=self.agent,
            nom="Keita",
            prenom="Awa",
            telephone="73000000",
        )
        self.cycle = Cycle.objects.create(
            code="CYC-2026-0003",
            client=self.client,
            mise=1000,
        )

    def test_depot_keeps_cycle_client_and_agent_relations(self):
        depot = Depot.objects.create(
            code="DEP-2026-0001",
            cycle=self.cycle,
            client=self.client,
            agent=self.agent,
            nb_mises=2,
            montant=2000,
        )

        self.assertEqual(depot.cycle, self.cycle)
        self.assertEqual(depot.client, self.client)
        self.assertEqual(depot.agent, self.agent)

    def test_retenue_can_be_attached_once_to_cycle(self):
        retenue = Retenue.objects.create(
            code="RET-2026-0001",
            cycle=self.cycle,
            client=self.client,
            agent=self.agent,
            montant=1000,
            commission_agent=500,
            commission_institution=500,
        )

        self.assertEqual(retenue.cycle, self.cycle)
        self.assertEqual(retenue.commission_agent + retenue.commission_institution, retenue.montant)

    def test_retrait_can_exist_without_agent(self):
        retrait = Retrait.objects.create(
            code="RTT-2026-0001",
            client=self.client,
            montant=5000,
        )

        self.assertIsNone(retrait.agent)

    def test_mouvement_can_reference_financial_context(self):
        mouvement = Mouvement.objects.create(
            code="MVT-2026-0001",
            client=self.client,
            cycle=self.cycle,
            agent=self.agent,
            type=MouvementType.MISE,
            sens=MouvementSens.ENTREE,
            montant=2000,
            reference_operation="DEP-2026-0001",
        )

        self.assertEqual(mouvement.type, MouvementType.MISE)
        self.assertEqual(mouvement.sens, MouvementSens.ENTREE)
        self.assertEqual(str(mouvement), "MVT-2026-0001 - MISE")
