from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserRole
from django.contrib.auth import get_user_model


User = get_user_model()


class CoreViewsTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fintech-IAM")

    def test_healthcheck_returns_ok_payload(self):
        response = self.client.get(reverse("healthcheck"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"status": "ok", "service": "fintech-iam"},
        )

    def test_home_redirects_authenticated_users_to_dashboard(self):
        user = User.objects.create_user(
            username="redirect_user",
            password="StrongPass123!",
            role=UserRole.ADMIN,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("home"))

        self.assertRedirects(response, reverse("admin_dashboard"))
