from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django import forms

from ..models import Post, Group

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
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for i in range(1, 3):
            Group.objects.create(
                title=f'Тестовая группа {i}',
                slug=f'test-slug-{i}',
                description=f'Тестовое описание {i}'
            )
        for i in range(1, 16):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {i}',
                group=get_object_or_404(Group, pk=1)
            )

    def test_pages_use_correct_template(self):
        """
        Проверяем, что для отображения страницы использован верный шаблон
        """
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': get_object_or_404(Group, pk=1).slug}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': PostPagesTests.user}):
            'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': get_object_or_404(Post, pk=1).id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': get_object_or_404(Post, pk=1).id}):
            'posts/create_post.html'
        }
        for page, template in pages_templates_names.items():
            response = PostPagesTests.authorized_client.get(page)
            with self.subTest(template=template):
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Проверяем корректный контекст на главной странице"""
        response = PostPagesTests.authorized_client.get(reverse('posts:index'))
        objects_list = response.context['post_list']
        for post in objects_list:
            if post.text == (f'Тестовый текст {len(objects_list)}'):
                post_expected_values = {
                    post.author:
                    get_object_or_404(Post, pk=len(objects_list)).author,
                    post.text:
                    get_object_or_404(Post, pk=len(objects_list)).text,
                    post.group.title:
                    get_object_or_404(Post, pk=len(objects_list)).group.title
                }
                for object_value, expected in post_expected_values.items():
                    with self.subTest(object_value=object_value):
                        self.assertEqual(object_value, expected)

    def test_group_list_page_show_correct_context(self):
        """Проверяем корректный контекст на странице group_list"""
        response = PostPagesTests.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': get_object_or_404(Group, pk=1).slug})
        )
        objects_list = response.context['post_list']
        for post in objects_list:
            if post.text == (f'Тестовый текст {len(objects_list)}'):
                grp_post_expected_value = {
                    post.author:
                    get_object_or_404(Post, pk=len(objects_list)).author,
                    post.text:
                    get_object_or_404(Post, pk=len(objects_list)).text,
                    post.group.title:
                    get_object_or_404(Post, pk=len(objects_list)).group.title
                }
                for object_value, expected in grp_post_expected_value.items():
                    with self.subTest(object_value=object_value):
                        self.assertEqual(object_value, expected)

    def test_created_post_exists_on_correct_pages(self):
        """Проверяем, что новый пост отображается на корректных страницах"""
        page_objects_expected = {
            reverse('posts:group_list',
                    kwargs={'slug': get_object_or_404(Group, pk=1).slug}):
            Post.objects.count(),
            reverse('posts:group_list',
                    kwargs={'slug': get_object_or_404(Group, pk=2).slug}):
            0,
            reverse('posts:index'): Post.objects.count(),
            reverse('posts:profile',
                    kwargs={'username': get_object_or_404(User, pk=1)}):
            get_object_or_404(User, pk=1).posts.count()
        }
        for page, expected in page_objects_expected.items():
            with self.subTest(page=page):
                response = PostPagesTests.authorized_client.get(page)
                objects_list = len(response.context['post_list'])
                self.assertEqual(objects_list, expected)

    def test_profile_page_show_correct_context(self):
        """Проверяем контекст на странице профиля пользователя"""
        response = PostPagesTests.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': get_object_or_404(User, pk=1)})
        )
        objects_list = response.context['post_list']
        obj_num = len(objects_list)
        value_expected = {
            objects_list[0].author: get_object_or_404(User, pk=1),
            obj_num:
            Post.objects.all().filter(
                author__username=get_object_or_404(User, pk=1)
            ).count()
        }
        for value, expected in value_expected.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_post_detail_page_show_correct_context(self):
        """Проверяем контекст на странице post_detail"""
        response = PostPagesTests.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': get_object_or_404(Post, pk=1).id})
        )
        post = response.context['post']
        posts_number = len(response.context['post_list'])
        post_values = {
            post.author: get_object_or_404(Post, pk=1).author,
            post.text: get_object_or_404(Post, pk=1).text,
            post.group.title: get_object_or_404(Post, pk=1).group.title,
            posts_number:
            Post.objects.all().filter(
                author__username=get_object_or_404(User, pk=1)).count()
        }
        for value, expected in post_values.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_create_page_show_correct_context(self):
        """
        Проверяем, что поля формы в post_create содержат верный тип данных
        """
        response = PostPagesTests.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Проверяем контекст страницы post_edit"""
        response = PostPagesTests.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': get_object_or_404(Post, pk=1).id}
                    )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, expected)

    def test_paginator_contains_correct_number_of_posts(self):
        """
        Тестируем паджинатор на страницах со списком постов:
        index, group_list, profile
        """
        page_contains_posts = {
            reverse('posts:index'): POSTS_NUM_PAGE_ONE,
            reverse('posts:index') + '?page=2': POSTS_NUM_PAGE_TWO,
            reverse('posts:profile',
                    kwargs={'username': get_object_or_404(User, pk=1)}):
            POSTS_NUM_PAGE_ONE,
            reverse('posts:profile',
                    kwargs={'username':
                            get_object_or_404(User, pk=1)}) + '?page=2':
            POSTS_NUM_PAGE_TWO,
            reverse('posts:group_list',
                    kwargs={'slug': get_object_or_404(Group, pk=1).slug}):
            POSTS_NUM_PAGE_ONE,
            reverse('posts:group_list',
                    kwargs={'slug':
                            get_object_or_404(Group, pk=1).slug}) + '?page=2':
            POSTS_NUM_PAGE_TWO
        }
        for page, expected in page_contains_posts.items():
            with self.subTest(page=page):
                response = PostPagesTests.authorized_client.get(page)
                page_obj = response.context['page_obj']
                self.assertEqual(len(page_obj), expected)
