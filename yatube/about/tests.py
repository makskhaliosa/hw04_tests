from django.test import TestCase, Client

from http import HTTPStatus


class AboutURLTest(TestCase):
    """Проверяем URL приложения about"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_pages_exist_at_desired_location(self):
        pages_for_all_users = {
            '/about/author/': HTTPStatus.OK.value,
            '/about/tech/': HTTPStatus.OK.value
        }
        for url, status in pages_for_all_users.items():
            with self.subTest(url=url):
                response = AboutURLTest.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_use_correct_templates(self):
        urls_templates_set = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in urls_templates_set.items():
            with self.subTest(url=url):
                response = AboutURLTest.guest_client.get(url)
                self.assertTemplateUsed(response, template)
