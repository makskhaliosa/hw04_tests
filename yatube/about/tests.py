from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTest(TestCase):
    """Проверяем URL приложения about"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.about_author = reverse('about:author')
        cls.about_tech = reverse('about:tech')

    def test_pages_exist_at_desired_location(self):
        pages_for_all_users = {
            self.about_author: HTTPStatus.OK,
            self.about_tech: HTTPStatus.OK
        }
        for url, status in pages_for_all_users.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_use_correct_templates(self):
        urls_templates_set = {
            self.about_author: 'about/author.html',
            self.about_tech: 'about/tech.html'
        }
        for url, template in urls_templates_set.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
