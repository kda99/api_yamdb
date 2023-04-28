from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLS = [(ADMIN, 'admin'), (MODERATOR, 'moderator'), (USER, 'user')]

    email = models.EmailField(
        max_length=254,
        verbose_name='Эл. почта',
        unique=True,
    )
    username = models.TextField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True
    )
    role = models.CharField(
        max_length=25,
        verbose_name='Права пользователя',
        choices=ROLS,
        default=USER,
    )
    bio = models.TextField(
        verbose_name='О себе',
        null=True,
        blank=True,
    )


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
        Genre,
        on_delete=models.CASCADE,  #.SET_DEFAULT,
        verbose_name='Жанр произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,  #.SET_DEFAULT,
        verbose_name='Категория произведения'
    )

    #class Meta:
    #    ordering = ('pub_date',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Комментарий')
    score = models.IntegerField(
        verbose_name='Оценка в отзыве к произведению',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_reviewing'
            )
        ]


class Comment(models.Model):
    """Модель комментария к отзыву"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Комментарий')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return '"{}" to review "{}" by author "{}"'.format(
            self.text, self.review, self.author
        )
