from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTest(TestCase):
    """Проверяем URL приложения about"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_pages_exist_at_desired_location(self):
        pages_for_all_users = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK
        }
        for url, status in pages_for_all_users.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_use_correct_templates(self):
        urls_templates_set = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for url, template in urls_templates_set.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
