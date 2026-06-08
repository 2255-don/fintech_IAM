from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.clients.models import Client
from apps.cycles.models import Cycle
from apps.transactions.models import Retrait
from apps.transactions.services import DepotService


User = get_user_model()


class InterfaceWorkflowTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_ui",
            password="StrongPass123!",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="UI",
        )
        self.agent_user = User.objects.create_user(
            username="agent_ui",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Aicha",
            last_name="Konate",
        )
        self.agent = Agent.objects.create(user=self.agent_user, code="AG-UI-0001")
        self.client_record = Client.objects.create(
            code="CLI-UI-0001",
            agent=self.agent,
            nom="Diallo",
            prenom="Mariam",
            telephone="71110000",
        )
        self.cycle = Cycle.objects.create(
            code="CYC-UI-0001",
            client=self.client_record,
            mise=1000,
        )

    def test_admin_dashboard_and_lists_are_accessible(self):
        self.client.force_login(self.admin_user)

        dashboard = self.client.get(reverse("admin_dashboard"))
        agents = self.client.get(reverse("admin_agent_list"))
        clients = self.client.get(reverse("admin_client_list"))
        cycles = self.client.get(reverse("admin_cycle_list"))

        self.assertContains(dashboard, "Tableau de bord administrateur")
        self.assertContains(agents, "Agents")
        self.assertContains(clients, self.client_record.code)
        self.assertContains(cycles, self.cycle.code)

    def test_agent_can_create_client_from_interface(self):
        self.client.force_login(self.agent_user)

        response = self.client.post(
            reverse("agent_client_create"),
            {
                "nom": "Keita",
                "prenom": "Saran",
                "telephone": "72220000",
                "genre": "F",
                "date_naissance": "",
                "email": "saran@example.com",
                "adresse": "Bamako",
            },
            follow=True,
        )

        created_client = Client.objects.get(telephone="72220000")
        self.assertRedirects(response, reverse("agent_client_detail", args=[created_client.id]))
        self.assertEqual(created_client.agent, self.agent)
        self.assertContains(response, "Client cree avec succes.")
        self.assertContains(response, "data-toast")

    def test_agent_can_open_cycle_from_interface(self):
        self.client.force_login(self.agent_user)

        response = self.client.post(
            reverse("agent_cycle_create", args=[self.client_record.id]),
            {
                "mise": 2000,
            },
        )

        cycle = Cycle.objects.get(client=self.client_record, mise=2000)
        self.assertRedirects(response, reverse("agent_cycle_detail", args=[cycle.id]))

    def test_agent_can_create_depot_from_interface(self):
        self.client.force_login(self.agent_user)

        response = self.client.post(
            reverse("agent_depot_create", args=[self.cycle.id]),
            {
                "nb_mises": 3,
            },
        )

        self.cycle.refresh_from_db()
        self.assertRedirects(response, reverse("agent_cycle_detail", args=[self.cycle.id]))
        self.assertEqual(self.cycle.nb_collectes, 3)

    def test_agent_can_create_retrait_from_interface(self):
        DepotService.create_depot(
            code="DEP-UI-0001",
            cycle_id=self.cycle.id,
            nb_mises=31,
            created_by=self.agent_user,
        )
        self.client.force_login(self.agent_user)

        response = self.client.post(
            reverse("agent_retrait_create", args=[self.client_record.id]),
            {
                "montant": 5000,
                "motif": "Besoin familial",
            },
        )

        retrait = Retrait.objects.get(client=self.client_record, montant=5000)
        self.assertRedirects(response, reverse("agent_client_detail", args=[self.client_record.id]))
        self.assertTrue(retrait.code.startswith("RTT-SQL-"))

    def test_agent_cannot_access_admin_agent_list(self):
        self.client.force_login(self.agent_user)

        response = self.client.get(reverse("admin_agent_list"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Acces refuse", status_code=403)

    def test_admin_cannot_access_agent_client_create(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("agent_client_create"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Acces refuse", status_code=403)

    def test_sensitive_forms_expose_confirmation_attributes(self):
        self.client.force_login(self.agent_user)

        client_create = self.client.get(reverse("agent_client_create"))
        cycle_create = self.client.get(reverse("agent_cycle_create", args=[self.client_record.id]))
        depot_create = self.client.get(reverse("agent_depot_create", args=[self.cycle.id]))

        self.assertContains(client_create, 'data-confirm-title="Creer ce client ?"')
        self.assertContains(cycle_create, 'data-confirm-title="Ouvrir ce cycle ?"')
        self.assertContains(depot_create, 'data-confirm-title="Confirmer le depot ?"')
