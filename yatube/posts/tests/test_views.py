from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group
from ..forms import PostForm

POSTS_NUM_PAGE_ONE = 10
POSTS_NUM_PAGE_TWO = 5

User = get_user_model()


class PostPagesTests(TestCase):
    """Тестируем шаблоны и view функции приложения post"""
    @classmethod
    def setUpClass(cls):
        """Создаем пользователей и базу данных"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.user_2 = User.objects.create_user(username='testuser_2')
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug-1',
            description='Тестовое описание 1'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст 1',
            group=cls.group
        )
        for i in range(2, 16):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=cls.group
            )
        cls.posts_index = reverse('posts:index')
        cls.posts_group_list = reverse('posts:group_list',
                                       args=(cls.group.slug,))
        cls.posts_profile = reverse('posts:profile',
                                    args=(cls.user.username,))
        cls.posts_profile_2 = reverse('posts:profile',
                                      args=(cls.user_2.username,))
        cls.posts_post_detail = reverse('posts:post_detail',
                                        args=(cls.post.id,))
        cls.posts_post_create = reverse('posts:post_create')
        cls.posts_post_edit = reverse('posts:post_edit',
                                      args=(cls.post.id,))

    def test_pages_use_correct_template(self):
        """
        Проверяем, что для отображения страницы использован верный шаблон
        """
        pages_templates_names = {
            self.posts_index: 'posts/index.html',
            self.posts_group_list:
            'posts/group_list.html',
            self.posts_profile:
            'posts/profile.html',
            self.posts_post_detail:
            'posts/post_detail.html',
            self.posts_post_create: 'posts/create_post.html',
            self.posts_post_edit:
            'posts/create_post.html'
        }
        for page, template in pages_templates_names.items():
            response = self.authorized_client.get(page)
            with self.subTest(template=template):
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверяем корректный контекст на главной странице"""
        response = self.authorized_client.get(self.posts_index)
        objects_list = response.context['post_list']
        object = objects_list.get(text=self.post.text)
        post_expected_values = {
            object.author:
            Post.objects.get(text=object.text).author,
            object.text:
            Post.objects.get(text=object.text).text,
            object.group.title:
            Post.objects.get(text=object.text).group.title
        }
        for object_value, expected in post_expected_values.items():
            with self.subTest(object_value=object_value):
                self.assertEqual(object_value, expected)

    def test_group_list_page_show_correct_context(self):
        """Проверяем корректный контекст на странице group_list"""
        form_data = {
            'text': 'Новый текст с группой',
            'group': self.group_2.id
        }
        self.authorized_client.post(
            self.posts_post_create,
            data=form_data,
            follow=True
        )
        group_2_url = reverse('posts:group_list', args=(self.group_2.slug,))
        new_post = Post.objects.get(text='Новый текст с группой')
        response_gr_1 = self.authorized_client.get(
            self.posts_group_list
        )
        objects_list_gr_1 = response_gr_1.context['post_list']
        object_1 = objects_list_gr_1.get(text=self.post.text)
        response_gr_2 = self.authorized_client.get(group_2_url)
        objects_list_gr_2 = response_gr_2.context['post_list']
        object_2 = objects_list_gr_2.get(text=new_post.text)
        grp_post_expected_values = {
            object_1.author:
            Post.objects.get(text=object_1.text).author,
            object_1.text:
            Post.objects.get(text=object_1.text).text,
            object_1.group.title:
            Post.objects.get(text=object_1.text).group.title,
            object_2.author:
            Post.objects.get(text=object_2.text).author,
            object_2.text:
            Post.objects.get(text=object_2.text).text,
            object_2.group.title:
            Post.objects.get(text=object_2.text).group.title
        }
        for object_value, expected in grp_post_expected_values.items():
            with self.subTest(object_value=object_value):
                self.assertEqual(object_value, expected)
        self.assertIn(self.post, objects_list_gr_1)
        self.assertIn(new_post, objects_list_gr_2)
        self.assertNotIn(self.post, objects_list_gr_2)
        self.assertNotIn(new_post, objects_list_gr_1)

    def test_created_post_exists_on_correct_pages(self):
        """
        Проверяем, что новый пост с группой отображается
        на корректных страницах
        """
        form_data = {
            'text': 'Новый текст с группой',
            'group': self.group_2.id
        }
        self.authorized_client.post(
            self.posts_post_create,
            data=form_data,
            follow=True
        )
        group_2_url = reverse('posts:group_list', args=(self.group_2.slug,))
        new_post = Post.objects.get(text='Новый текст с группой')
        pages_with_post_list = [
            group_2_url,
            self.posts_index,
            self.posts_profile
        ]
        for page in pages_with_post_list:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                objects_list = response.context['post_list']
                self.assertIn(new_post, objects_list)
        response_group_1 = self.authorized_client.get(self.posts_group_list)
        objects_list = response_group_1.context['post_list']
        self.assertNotIn(new_post, objects_list)

    def test_profile_page_show_correct_context(self):
        """Проверяем контекст на странице профиля пользователя"""
        form_data = {
            'text': 'Текст с профиля 2',
            'group': self.group_2.id
        }
        self.authorized_client_2.post(
            self.posts_post_create,
            data=form_data,
            follow=True
        )
        response_1 = self.authorized_client.get(
            self.posts_profile
        )
        response_2 = self.authorized_client_2.get(
            self.posts_profile_2
        )
        new_post = Post.objects.get(text='Текст с профиля 2')
        objects_list_1 = response_1.context['post_list']
        obj_num_1 = len(objects_list_1)
        objects_list_2 = response_2.context['post_list']
        obj_num_2 = len(objects_list_2)
        user_1_posts = Post.objects.filter(
            author__username=self.user.username
        ).count()
        user_2_posts = Post.objects.filter(
            author__username=self.user_2.username
        ).count()
        value_expected = {
            objects_list_1.get(id=self.post.id).author: self.user,
            objects_list_1.get(id=self.post.id).text: self.post.text,
            objects_list_1.get(id=self.post.id).group: self.group,
            objects_list_2.get(id=new_post.id).author: self.user_2,
            objects_list_2.get(id=new_post.id).text: new_post.text,
            objects_list_2.get(id=new_post.id).group: self.group_2,
            obj_num_1: user_1_posts,
            obj_num_2: user_2_posts
        }
        for value, expected in value_expected.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
        self.assertIn(self.post, objects_list_1)
        self.assertIn(new_post, objects_list_2)
        self.assertNotIn(self.post, objects_list_2)
        self.assertNotIn(new_post, objects_list_1)

    def test_post_detail_page_show_correct_context(self):
        """Проверяем контекст на странице post_detail"""
        response = self.authorized_client.get(
            self.posts_post_detail
        )
        post = response.context['post']
        posts_number = len(response.context['post_list'])
        post_values = {
            post.author: self.post.author,
            post.text: self.post.text,
            post.group.title: self.post.group.title,
            posts_number:
            Post.objects.all().filter(
                author__username=self.user.username
            ).count()
        }
        for value, expected in post_values.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_create_page_show_correct_context(self):
        """Проверяем контекст страницы post_create"""
        response = self.authorized_client.get(
            self.posts_post_create
        )
        create_form = response.context['form']
        self.assertIsInstance(create_form, PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Проверяем контекст страницы post_edit"""
        response = self.authorized_client.get(
            self.posts_post_edit
        )
        edit_form = response.context['form']
        self.assertIsInstance(edit_form, PostForm)
        self.assertIn('is_edit', response.context)

    def test_paginator_contains_correct_number_of_posts(self):
        """
        Тестируем паджинатор на страницах со списком постов:
        index, group_list, profile
        """
        page_contains_posts = {
            self.posts_index: POSTS_NUM_PAGE_ONE,
            self.posts_index + '?page=2': POSTS_NUM_PAGE_TWO,
            self.posts_profile: POSTS_NUM_PAGE_ONE,
            self.posts_profile + '?page=2': POSTS_NUM_PAGE_TWO,
            self.posts_group_list: POSTS_NUM_PAGE_ONE,
            self.posts_group_list + '?page=2': POSTS_NUM_PAGE_TWO
        }
        for page, expected in page_contains_posts.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                page_obj = response.context['page_obj']
                self.assertEqual(len(page_obj), expected)
