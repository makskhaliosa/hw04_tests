from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


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
        cls.signup = reverse('users:signup')
        cls.login = reverse('users:login')
        cls.logout = reverse('users:logout')
        cls.password_change_form = reverse('users:password_change_form')
        cls.password_change_done = reverse('users:password_change_done')
        cls.password_reset_form = reverse('users:password_reset_form')
        cls.password_reset_done = reverse('users:password_reset_done')
        cls.password_reset_confirm = reverse('users:password_reset_confirm',
                                             args=('<uidb64>', '<token>',))
        cls.password_reset_complete = reverse('users:password_reset_complete')

    def test_urls_exist_for_guest_user(self):
        """signup url доступен для незарегистрированного пользователя"""
        urls_for_anonymous_users = {
            self.signup: HTTPStatus.OK,
            self.login: HTTPStatus.OK
        }
        for url, status in urls_for_anonymous_users.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_urls_exist_for_authorized_user(self):
        """Проверяем url для авторизованного пользователя"""
        urls_for_authorized_users = {
            self.logout: HTTPStatus.OK,
            self.password_change_form: HTTPStatus.FOUND,
            self.password_change_done: HTTPStatus.FOUND,
            self.password_reset_form: HTTPStatus.OK,
            self.password_reset_done: HTTPStatus.OK,
            self.password_reset_confirm: HTTPStatus.OK,
            self.password_reset_complete: HTTPStatus.OK
        }
        for url, status in urls_for_authorized_users.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status)
