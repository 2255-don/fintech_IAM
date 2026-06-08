from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.core.exceptions import ActiveCycleAlreadyExistsError, ClientNotFoundError, InvalidMiseError
from apps.cycles.models import Cycle, CycleStatus
from apps.cycles.services import CycleService


User = get_user_model()


class CycleModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_cycle_owner",
            password="StrongPass123!",
            role=UserRole.AGENT,
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0002")
        self.client = Client.objects.create(
            code="CLI-2026-0002",
            agent=self.agent,
            nom="Bah",
            prenom="Fatou",
            telephone="72000000",
        )

    def test_cycle_defaults_match_business_expectations(self):
        cycle = Cycle.objects.create(
            code="CYC-2026-0001",
            client=self.client,
            mise=1000,
        )

        self.assertEqual(cycle.nb_collectes, 0)
        self.assertEqual(cycle.statut, CycleStatus.EN_COURS)
        self.assertIsNone(cycle.date_fermeture)

    def test_cycle_rejects_negative_mise_constraint(self):
        with self.assertRaises(IntegrityError):
            Cycle.objects.create(
                code="CYC-2026-0002",
                client=self.client,
                mise=0,
            )


class CycleServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_cycle_service",
            password="StrongPass123!",
            role=UserRole.AGENT,
        )
        self.agent = Agent.objects.create(user=self.user, code="AG-2026-0200")
        self.client = Client.objects.create(
            code="CLI-2026-0200",
            agent=self.agent,
            nom="Kone",
            prenom="Aicha",
            telephone="77000000",
        )

    def test_validate_mise_accepts_valid_multiple_of_100(self):
        CycleService.validate_mise(1000)

    def test_validate_mise_rejects_non_positive_value(self):
        with self.assertRaises(InvalidMiseError):
            CycleService.validate_mise(0)

    def test_validate_mise_rejects_non_multiple_of_100(self):
        with self.assertRaises(InvalidMiseError):
            CycleService.validate_mise(1050)

    def test_create_cycle_sets_initial_business_values(self):
        cycle = CycleService.create_cycle(
            code="CYC-2026-0200",
            client_id=self.client.id,
            mise=1000,
            created_by=self.user,
        )

        self.assertEqual(cycle.client, self.client)
        self.assertEqual(cycle.nb_collectes, 0)
        self.assertEqual(cycle.statut, CycleStatus.EN_COURS)
        self.assertEqual(cycle.created_by, self.user)

    def test_create_cycle_raises_when_client_not_found(self):
        with self.assertRaises(ClientNotFoundError):
            CycleService.create_cycle(
                code="CYC-2026-0201",
                client_id=999999,
                mise=1000,
            )

    def test_create_cycle_rejects_second_active_cycle_for_same_client(self):
        Cycle.objects.create(
            code="CYC-2026-0202",
            client=self.client,
            mise=1000,
            statut=CycleStatus.EN_COURS,
        )

        with self.assertRaises(ActiveCycleAlreadyExistsError):
            CycleService.create_cycle(
                code="CYC-2026-0203",
                client_id=self.client.id,
                mise=1000,
                created_by=self.user,
            )

    def test_create_cycle_allows_new_cycle_after_standard_closure(self):
        Cycle.objects.create(
            code="CYC-2026-0204",
            client=self.client,
            mise=1000,
            statut=CycleStatus.CLOTURE,
        )

        cycle = CycleService.create_cycle(
            code="CYC-2026-0205",
            client_id=self.client.id,
            mise=1000,
            created_by=self.user,
        )

        self.assertEqual(cycle.statut, CycleStatus.EN_COURS)

    def test_create_cycle_allows_new_cycle_after_early_closure(self):
        Cycle.objects.create(
            code="CYC-2026-0206",
            client=self.client,
            mise=1000,
            statut=CycleStatus.CLOTURE_ANTICIPEE,
        )

        cycle = CycleService.create_cycle(
            code="CYC-2026-0207",
            client_id=self.client.id,
            mise=1000,
            created_by=self.user,
        )

        self.assertEqual(cycle.statut, CycleStatus.EN_COURS)
