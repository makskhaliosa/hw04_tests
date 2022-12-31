from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404

from ..forms import PostForm
from ..models import Post

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
        Post.objects.create(
            author=cls.user,
            text='Тестовый текст'
        )
        cls.form = PostForm()

    def test_post_created_after_submitting_form(self):
        """
        Проверяем создание новой записи в базе и переадресацию
        на страницу пользователя
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы'
        }
        response = PostFormTests.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        redirect_url = reverse('posts:profile',
                               args=('testuser',))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, redirect_url)

    def test_post_form_show_correct_label(self):
        """Проверяем правильное отображение названия поля формы"""
        label_value_expected = {
            'text': 'Текст',
            'group': 'Группа'
        }
        for field, expected in label_value_expected.items():
            with self.subTest(expected=expected):
                field_label = PostFormTests.form.fields[field].label
                self.assertEqual(field_label, expected)

    def test_post_changed_after_submitting_edit_form(self):
        """
        Проверяем правильность редактирования поста
        после отправки формы для редактирования
        """
        form_data = {
            'text': 'Измененный текст из формы'
        }
        response = PostFormTests.authorized_client.post(
            reverse('posts:post_edit',
                    args=(get_object_or_404(Post, pk=1).id,)),
            data=form_data,
            follow=True
        )
        redirect_url = reverse('posts:post_detail',
                               args=(get_object_or_404(Post, pk=1).id,))
        self.assertEqual(get_object_or_404(Post, pk=1).text,
                         form_data['text'])
        self.assertRedirects(response, redirect_url)
