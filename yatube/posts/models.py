from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

NUMBER_OF_LETTERS = 15


class Group(models.Model):
    title = models.CharField(
        verbose_name='название группы',
        max_length=200,
        help_text='дайте подходящее название группе'
    )
    slug = models.SlugField(
        verbose_name='название адреса группы',
        unique=True,
        help_text='адрес не должен повторяться'
    )
    description = models.TextField(
        verbose_name='описание группы',
        help_text='группа предназначена для определенной тематики'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='текст поста',
        help_text='введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='группа',
        help_text='выберите группу'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:NUMBER_OF_LETTERS]
