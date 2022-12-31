from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from http import HTTPStatus

User = get_user_model()


class UserURLTest(TestCase):
    """Тестирует URL-адреса в users"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_urls_exist_for_guest_user(self):
        """signup url доступен для незарегистрированного пользователя"""
        urls_for_anonymous_users = {
            '/auth/signup/': HTTPStatus.OK.value,
            '/auth/login/': HTTPStatus.OK.value
        }
        for url, status in urls_for_anonymous_users.items():
            with self.subTest(url=url):
                response = UserURLTest.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_exist_for_authorized_user(self):
        """Проверяем url для авторизованного пользователя"""
        urls_for_authorized_users = {
            '/auth/logout/': HTTPStatus.OK.value,
            '/auth/password_change/': HTTPStatus.FOUND.value,
            '/auth/password_change/done/': HTTPStatus.FOUND.value,
            '/auth/password_reset/': HTTPStatus.OK.value,
            '/auth/password_reset/done/': HTTPStatus.OK.value,
            '/auth/reset/<uidb64>/<token>/': HTTPStatus.OK.value,
            '/auth/reset/done/': HTTPStatus.OK.value,
        }
        for url, status in urls_for_authorized_users.items():
            with self.subTest(url=url):
                response = UserURLTest.authorized_client.get(url)
                self.assertEqual(response.status_code, status)
