from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

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
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', args=(PostURLTests.group.slug,)):
            HTTPStatus.OK,
            reverse('posts:profile', args=(PostURLTests.user.username,)):
            HTTPStatus.OK,
            reverse('posts:post_detail', args=(PostURLTests.post.id,)):
            HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        # Делаем запрос к странице и проверяем статус
        for address, status in pages_for_all_users.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
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
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_url_exists_for_author(self):
        """
        Проверяем, что для автора поста существует страница редактирования
        """
        url = reverse('posts:post_edit', args=(self.post.id,))
        if self.authorized_client == self.post.author:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirects_anonymous_user_to_user_login(self):
        """Проверяем переадресацию неавторизованного пользователя"""
        urls_for_athorized_users = {
            reverse('posts:post_create'): '/auth/login/?next=/create/',
            reverse('posts:post_edit', args=(self.post.id,)):
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        }
        for url, redirect_url in urls_for_athorized_users.items():
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(
                response, redirect_url)

    def test_edit_post_url_not_available_for_non_author(self):
        """Проверяем, что редактировать пост может только автор"""
        url = reverse('posts:post_edit', args=(self.post.id,))
        redirect_url = reverse('posts:post_detail', args=(self.post.id,))
        if self.authorized_client_two != self.post.author:
            response = self.authorized_client_two.get(url)
            self.assertRedirects(response, redirect_url)

    def test_urls_use_correct_templates(self):
        """Проверяем, что url-адрес использует верный шаблон"""
        urls_templates_set = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=(PostURLTests.group.slug,)):
            'posts/group_list.html',
            reverse('posts:profile', args=(PostURLTests.user.username,)):
            'posts/profile.html',
            reverse('posts:post_detail', args=(PostURLTests.post.id,)):
            'posts/post_detail.html',
            reverse('posts:post_edit', args=(self.post.id,)):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for url, template in urls_templates_set.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
