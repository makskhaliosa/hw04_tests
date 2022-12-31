from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Group, Post

NUMBER_OF_LETTERS = 15

User = get_user_model()


class PostModelTest(TestCase):
    """Тестируем модель Post"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(username='Auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый сдаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.test_user,
            text='Тестовый текст'
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        group_title = group.title
        post_title = post.text[:NUMBER_OF_LETTERS]
        self.assertEqual(group_title, str(group))
        self.assertEqual(post_title, str(post))

    def test_post_verbose_name(self):
        """Проверяет понятные названия полей поста"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'текст поста',
            'author': 'автор'
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected)

    def test_post_help_text(self):
        """Проверяет понятные подсказки для поста"""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'введите текст поста',
            'group': 'выберите группу'
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected)

    def test_group_verbose_name(self):
        """Проверяет понятные названия полей группы"""
        group = PostModelTest.group
        field_verboses = {
            'title': 'название группы',
            'slug': 'название адреса группы',
            'description': 'описание группы'
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected,
                    'Название группы отображается не верно')

    def test_group_help_texts(self):
        """Проверяет понятные подсказки для группы"""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'дайте подходящее название группе',
            'slug': 'адрес не должен повторяться',
            'description': 'группа предназначена для определенной тематики'
        }
        for field, expected in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected)
