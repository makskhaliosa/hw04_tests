from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    """Тестирует правильность заполнения формы для создания поста"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group
        )
        cls.form = PostForm()
        cls.posts_index = reverse('posts:index')
        cls.posts_group_list = reverse('posts:group_list',
                                       args=(cls.group.slug,))
        cls.posts_profile = reverse('posts:profile',
                                    args=(cls.user.username,))
        cls.posts_post_detail = reverse('posts:post_detail',
                                        args=(cls.post.id,))
        cls.posts_post_create = reverse('posts:post_create')
        cls.posts_post_edit = reverse('posts:post_edit',
                                      args=(cls.post.id,))

    def test_post_created_after_submitting_form(self):
        """
        Проверяем создание новой записи в базе и переадресацию
        на страницу пользователя
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            self.posts_post_create,
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group']
        ).exists()
        )
        self.assertRedirects(response, self.posts_profile)

    def test_post_form_show_correct_label(self):
        """Проверяем правильное отображение названия поля формы"""
        label_value_expected = {
            'text': 'Текст',
            'group': 'Группа'
        }
        for field, expected in label_value_expected.items():
            with self.subTest(expected=expected):
                field_label = self.form.fields[field].label
                self.assertEqual(field_label, expected)

    def test_post_changed_after_submitting_edit_form(self):
        """
        Проверяем правильность редактирования поста
        после отправки формы для редактирования
        """
        form_data = {
            'text': 'Измененный текст из формы',
            'group': self.group_2.id
        }
        response = self.authorized_client.post(
            self.posts_post_edit,
            data=form_data,
            follow=True
        )
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group']
        ).exists()
        )
        self.assertRedirects(response, self.posts_post_detail)

    def test_create_page_show_correct_context(self):
        """
        Проверяем правильность полей формы на странице post_create
        """
        response = self.authorized_client.get(
            self.posts_post_create
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
        """Проверяем правильность полей формы на странице post_edit"""
        response = self.authorized_client.get(
            self.posts_post_edit
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, expected)
