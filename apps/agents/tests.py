from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserRole
from apps.agents.models import Agent
from apps.agents.services import AgentService


User = get_user_model()


class AgentModelTests(TestCase):
    def test_agent_profile_can_be_linked_to_agent_user(self):
        user = User.objects.create_user(
            username="agent_profile",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Mariam",
            last_name="Diallo",
        )
        agent = Agent.objects.create(user=user, code="AG-2026-0001", telephone="70000000")

        self.assertEqual(agent.user.role, UserRole.AGENT)
        self.assertEqual(str(agent), "AG-2026-0001 - Mariam Diallo")


class AgentServiceTests(TestCase):
    def test_create_agent_generates_default_password_and_code(self):
        agent = AgentService.create_agent(
            username="agent_auto",
            first_name="Awa",
            last_name="Traore",
            telephone="70000009",
            email="awa@example.com",
            adresse="Bamako",
        )

        self.assertTrue(agent.code.startswith(f"AG-{date.today().year}-"))
        self.assertTrue(agent.user.check_password(AgentService.DEFAULT_PASSWORD))

    def test_generate_next_code_increments_annual_sequence(self):
        current_year = date.today().year
        first_user = User.objects.create_user(
            username="agent_existing",
            password="StrongPass123!",
            role=UserRole.AGENT,
        )
        Agent.objects.create(user=first_user, code=f"AG-{current_year}-0042")

        generated = AgentService.generate_next_code()

        self.assertEqual(generated, f"AG-{current_year}-0043")

    def test_toggle_active_updates_agent_and_user_status(self):
        user = User.objects.create_user(username="agent_status", password="StrongPass123!", role=UserRole.AGENT)
        agent = Agent.objects.create(user=user, code=f"AG-{date.today().year}-0050", actif=True)

        AgentService.toggle_active(agent)
        agent.refresh_from_db()
        user.refresh_from_db()

        self.assertFalse(agent.actif)
        self.assertFalse(user.is_active)

    def test_soft_delete_marks_agent_deleted(self):
        user = User.objects.create_user(username="agent_delete", password="StrongPass123!", role=UserRole.AGENT)
        agent = Agent.objects.create(user=user, code=f"AG-{date.today().year}-0051", actif=True)

        AgentService.soft_delete(agent)
        agent.refresh_from_db()
        user.refresh_from_db()

        self.assertIsNotNone(agent.deleted_at)
        self.assertFalse(agent.actif)
        self.assertFalse(user.is_active)

    def test_reset_password_restores_default_password_and_access(self):
        user = User.objects.create_user(username="agent_reset", password="TempPass123!", role=UserRole.AGENT)
        agent = Agent.objects.create(user=user, code=f"AG-{date.today().year}-0052", actif=False)

        AgentService.reset_password(agent)
        agent.refresh_from_db()
        user.refresh_from_db()

        self.assertTrue(user.check_password(AgentService.DEFAULT_PASSWORD))
        self.assertTrue(agent.actif)
        self.assertTrue(user.is_active)


class AgentAdminViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_agents",
            password="StrongPass123!",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="Agents",
        )
        self.agent_user = User.objects.create_user(
            username="agent_view",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Awa",
            last_name="Diallo",
            email="awa@demo.local",
        )
        self.agent = Agent.objects.create(
            user=self.agent_user,
            code=f"AG-{date.today().year}-0090",
            telephone="70000099",
            email="awa@demo.local",
            adresse="Bamako",
        )

    def test_admin_can_create_agent_from_list_modal(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin_agent_list"),
            {
                "username": "agent_modal",
                "first_name": "Fatou",
                "last_name": "Keita",
                "telephone": "71234567",
                "email": "fatou@example.com",
                "adresse": "Bamako",
            },
            follow=True,
        )

        agent = Agent.objects.get(user__username="agent_modal")
        self.assertRedirects(response, reverse("admin_agent_detail", args=[agent.id]))
        self.assertTrue(agent.user.check_password(AgentService.DEFAULT_PASSWORD))
        self.assertContains(response, "Mot de passe initial")

    def test_invalid_modal_submission_reopens_list_modal(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(reverse("admin_agent_list"), {"username": ""})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="agent-modal-toggle"')
        self.assertContains(response, "Nom d&#x27;utilisateur")
        self.assertContains(response, "checked")

    def test_admin_can_update_agent(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin_agent_update", args=[self.agent.id]),
            {
                "username": "agent_view_updated",
                "first_name": "Awa",
                "last_name": "Konate",
                "telephone": "79990000",
                "email": "awa.updated@demo.local",
                "adresse": "Sikasso",
            },
            follow=True,
        )

        self.agent.refresh_from_db()
        self.agent_user.refresh_from_db()
        self.assertRedirects(response, reverse("admin_agent_detail", args=[self.agent.id]))
        self.assertEqual(self.agent_user.username, "agent_view_updated")
        self.assertEqual(self.agent_user.last_name, "Konate")
        self.assertEqual(self.agent.telephone, "79990000")

    def test_admin_can_toggle_agent_status(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin_agent_toggle_status", args=[self.agent.id]),
            {"next": reverse("admin_agent_list")},
            follow=True,
        )

        self.agent.refresh_from_db()
        self.agent_user.refresh_from_db()
        self.assertRedirects(response, reverse("admin_agent_list"))
        self.assertFalse(self.agent.actif)
        self.assertFalse(self.agent_user.is_active)

    def test_admin_can_soft_delete_agent(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin_agent_delete", args=[self.agent.id]),
            {"next": reverse("admin_agent_list")},
            follow=True,
        )

        self.agent.refresh_from_db()
        self.agent_user.refresh_from_db()
        self.assertRedirects(response, reverse("admin_agent_list"))
        self.assertIsNotNone(self.agent.deleted_at)
        self.assertFalse(self.agent_user.is_active)

    def test_admin_can_reset_agent_password(self):
        self.client.force_login(self.admin_user)
        self.agent_user.set_password("AutrePass123!")
        self.agent_user.is_active = False
        self.agent_user.save(update_fields=["password", "is_active"])
        self.agent.actif = False
        self.agent.save(update_fields=["actif"])

        response = self.client.post(
            reverse("admin_agent_reset_password", args=[self.agent.id]),
            {"next": reverse("admin_agent_detail", args=[self.agent.id])},
            follow=True,
        )

        self.agent.refresh_from_db()
        self.agent_user.refresh_from_db()
        self.assertRedirects(response, reverse("admin_agent_detail", args=[self.agent.id]))
        self.assertTrue(self.agent_user.check_password(AgentService.DEFAULT_PASSWORD))
        self.assertTrue(self.agent.actif)
        self.assertTrue(self.agent_user.is_active)
        self.assertContains(response, "réinitialisé")
