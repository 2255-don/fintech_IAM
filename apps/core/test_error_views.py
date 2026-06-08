from django.test import SimpleTestCase, override_settings


@override_settings(DEBUG=False)
class ErrorPagesTests(SimpleTestCase):
    def test_404_page_is_rendered_with_controlled_message(self):
        response = self.client.get("/page-introuvable-demo/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page introuvable", status_code=404)
        self.assertContains(response, "Erreur 404", status_code=404)

    @override_settings(ROOT_URLCONF="apps.core.test_urls")
    def test_500_page_is_rendered_with_controlled_message(self):
        self.client.raise_request_exception = False

        response = self.client.get("/__test-error-500/")

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Incident interne", status_code=500)
        self.assertContains(response, "Erreur 500", status_code=500)
