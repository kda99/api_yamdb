from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Category(models.Model):
    """Модель категории произведения"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug категории'
    )

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанра произведения"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug жанра'
    )

    class Meta:
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения, к которому пишут отзывы"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название произведения'
    )
    year = models.IntegerField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name='Год выпуска'
    )
    text = models.TextField(
        verbose_name='Описание произведения',
        help_text='Введите описание произведения'
    )
    genre = models.ForeignKey(
        'Genre',
        on_delete=models.SET_DEFAULT,
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_DEFAULT,
        verbose_name='Категория произведения'
    )

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Модель комментария к отзыву"""
    review_id = models.ForeignKey(
        'Review',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Коммент',
        help_text='Введите текст коммента'
    )
    #здесь пока что закомментил строку "author", потому что она ссылается на модель User
    #а модели "User" пока что нет
    #author = models.ForeignKey(
    #    User,
    #    on_delete=models.CASCADE,
    #    related_name='comments'
    #)
    pub_date = models.DateTimeField(
        auto_now_add=True
    )


class Review(models.Model):
    """Модель отзыва"""
    text = models.TextField(
        verbose_name='Отзыв',
        help_text='Введите текст отзыва'
    )
    score = models.IntegerField(
        verbose_name='Оценка в отзыве к произведению',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    title_id = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    #здесь пока что закомментил строку "author", потому что она ссылается на модель User
    #а модели "User" пока что нет
    #author = models.ForeignKey(
    #    User,
    #    on_delete=models.CASCADE,
    #    related_name='reviews'
    #)

    class Meta:
        ordering = ('pub_date',)
