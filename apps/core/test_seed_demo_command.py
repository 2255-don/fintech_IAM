from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.cycles.models import Cycle
from apps.transactions.models import Depot, Retrait


User = get_user_model()


class SeedDemoCommandTests(TestCase):
    def test_seed_demo_creates_expected_demo_dataset_and_is_idempotent(self):
        stdout = StringIO()

        call_command("seed_demo", stdout=stdout)
        call_command("seed_demo", stdout=stdout)

        self.assertTrue(User.objects.filter(username="admin_demo", role=UserRole.ADMIN).exists())
        self.assertTrue(User.objects.filter(username="agent_alpha", role=UserRole.AGENT).exists())
        self.assertTrue(User.objects.filter(username="agent_beta", role=UserRole.AGENT).exists())
        self.assertEqual(Agent.objects.count(), 2)
        self.assertEqual(Client.objects.count(), 3)
        self.assertEqual(Cycle.objects.count(), 3)
        self.assertEqual(Depot.objects.count(), 3)
        self.assertEqual(Retrait.objects.count(), 1)
        self.assertIn("Jeu de demonstration cree ou mis a jour avec succes.", stdout.getvalue())
