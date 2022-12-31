from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    """Тестируем страницы проекта"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем записи в базе данных
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.user_two = User.objects.create_user(username='second_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_two = Client()
        cls.authorized_client_two.force_login(cls.user_two)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )

    def test_page_url_exists_at_desired_location(self):
        """Проверяем, что страницы доступны всем пользователям.
        Несуществующая страница возвращает код ошибки 404"""
        pages_for_all_users = {
            '/': HTTPStatus.OK.value,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK.value,
            f'/profile/{PostURLTests.user.username}/': HTTPStatus.OK.value,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK.value,
            '/unexisting_page/': HTTPStatus.NOT_FOUND.value
        }
        # Делаем запрос к странице и проверяем статус
        for address, status in pages_for_all_users.items():
            with self.subTest(address=address):
                response = PostURLTests.guest_client.get(address)
                # Утверждаем, что для прохождения теста код должен иметь
                # соответствующий статус
                self.assertEqual(
                    response.status_code,
                    status,
                    f'Что-то не так с адресом {address}'
                )

    def test_create_post_url_exists_for_authorized_user(self):
        """
        Проверяем, что создание поста доступно
        для зарегистрированного пользователя
        """
        response = PostURLTests.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_url_exists_for_author(self):
        """
        Проверяем, что для автора поста существует страница редактирования
        """
        if PostURLTests.authorized_client == PostURLTests.post.author:
            response = PostURLTests.authorized_client.get(
                f'/posts/{PostURLTests.post.id}/edit/'
            )
            self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_redirects_anonymous_user_to_user_login(self):
        """Проверяем переадресацию неавторизованного пользователя"""
        urls_for_athorized_users = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{PostURLTests.post.id}/edit/':
            f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/'
        }
        for url, redirect_url in urls_for_athorized_users.items():
            response = PostURLTests.guest_client.get(url, follow=True)
            self.assertRedirects(
                response, redirect_url)

    def test_edit_post_url_not_available_for_non_author(self):
        """Проверяем, что редактировать пост может только автор"""
        if PostURLTests.authorized_client_two != PostURLTests.post.author:
            response = PostURLTests.authorized_client_two.get(
                f'/posts/{PostURLTests.post.id}/edit/')
            self.assertRedirects(response, f'/posts/{PostURLTests.post.id}/')

    def test_urls_use_correct_templates(self):
        """Проверяем, что url-адрес использует верный шаблон"""
        urls_templates_set = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for url, template in urls_templates_set.items():
            with self.subTest(url=url):
                response = PostURLTests.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
