from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.clients.services import ClientService
from apps.core.exceptions import AgentNotFoundError


User = get_user_model()


class ClientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_client_owner",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Aminata",
            last_name="Traore",
        )
        self.agent = Agent.objects.create(
            user=self.user,
            code="AG-2026-0001",
            telephone="70000000",
        )

    def test_client_can_be_linked_to_agent(self):
        client = Client.objects.create(
            code="CLI-2026-0001",
            agent=self.agent,
            nom="Diallo",
            prenom="Moussa",
            telephone="71000000",
        )

        self.assertEqual(client.agent, self.agent)
        self.assertEqual(str(client), "CLI-2026-0001 - Diallo Moussa")
        self.assertIsNotNone(client.created_at)


class ClientServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="agent_service_owner",
            password="StrongPass123!",
            role=UserRole.AGENT,
        )
        self.agent = Agent.objects.create(
            user=self.user,
            code="AG-2026-0100",
            telephone="74000000",
        )

    def test_create_client_creates_client_with_expected_defaults(self):
        client = ClientService.create_client(
            code="CLI-2026-0100",
            agent_id=self.agent.id,
            nom="Traore",
            prenom="Aminata",
            telephone="75000000",
            created_by=self.user,
        )

        self.assertEqual(client.agent, self.agent)
        self.assertEqual(client.created_by, self.user)
        self.assertEqual(client.updated_by, self.user)

    def test_create_client_raises_when_agent_not_found(self):
        with self.assertRaises(AgentNotFoundError):
            ClientService.create_client(
                code="CLI-2026-0101",
                agent_id=999999,
                nom="Diop",
                telephone="76000000",
            )

    def test_update_client_updates_expected_fields(self):
        client = Client.objects.create(
            code="CLI-2026-0102",
            agent=self.agent,
            nom="Diallo",
            prenom="Awa",
            telephone="77000000",
            created_by=self.user,
            updated_by=self.user,
        )

        ClientService.update_client(
            client,
            nom="Diallo",
            prenom="Aminata",
            telephone="78000000",
            genre="F",
            email="aminata@example.com",
            adresse="Bamako",
            updated_by=self.user,
        )

        client.refresh_from_db()
        self.assertEqual(client.prenom, "Aminata")
        self.assertEqual(client.telephone, "78000000")
        self.assertEqual(client.email, "aminata@example.com")
