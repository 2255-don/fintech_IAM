from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserRole


User = get_user_model()


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_iam",
            password="StrongPass123!",
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="IAM",
        )
        self.agent_user = User.objects.create_user(
            username="agent_iam",
            password="StrongPass123!",
            role=UserRole.AGENT,
            first_name="Agent",
            last_name="IAM",
        )

    def test_login_page_is_available(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Connexion")

    def test_admin_login_redirects_to_admin_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": "admin_iam", "password": "StrongPass123!"},
            follow=True,
        )

        self.assertRedirects(response, reverse("admin_dashboard"))
        self.assertContains(response, "Tableau de bord administrateur")

    def test_agent_login_redirects_to_agent_dashboard(self):
        response = self.client.post(
            reverse("login"),
            {"username": "agent_iam", "password": "StrongPass123!"},
            follow=True,
        )

        self.assertRedirects(response, reverse("agent_dashboard"))
        self.assertContains(response, "Tableau de bord agent")

    def test_admin_cannot_access_agent_dashboard(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("agent_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_agent_cannot_access_admin_dashboard(self):
        self.client.force_login(self.agent_user)

        response = self.client.get(reverse("admin_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_redirect_requires_authentication(self):
        response = self.client.get(reverse("dashboard_redirect"))

        self.assertRedirects(response, reverse("login"))


class UserModelTests(TestCase):
    def test_user_defaults_to_admin_role(self):
        user = User.objects.create_user(
            username="default_admin",
            password="StrongPass123!",
        )

        self.assertEqual(user.role, UserRole.ADMIN)

    def test_user_display_name_prefers_full_name(self):
        user = User.objects.create_user(
            username="agent_display",
            password="StrongPass123!",
            first_name="Aminata",
            last_name="Traore",
            role=UserRole.AGENT,
        )

        self.assertEqual(user.get_display_name(), "Aminata Traore")
