from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator

from .validators import year_validator, validate_username


class User(AbstractUser):

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICES = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )
    username = models.CharField(
        validators=(validate_username,),
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        blank=False,
    )
    email = models.EmailField(max_length=254, unique=True)
    bio = models.TextField(blank=True)
    role = models.SlugField(choices=CHOICES, default=USER)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR

    @property
    def is_user(self):
        return self.role == User.USER


class Category(models.Model):
    """Модель категории произведения"""
    name = models.CharField(
        max_length=256,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name='Slug категории'
    )

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
    year = models.PositiveSmallIntegerField(
        validators=(year_validator,),
        blank=True,
        null=True,
        verbose_name='Год выпуска',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория произведения',
        default='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр произведения',
        default='Жанр',
        through='GenreTitle'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(verbose_name='Рецензия')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва',
        related_name='reviews',
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка в отзыве к произведению',
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_reviewing'
            )
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментария к отзыву"""
    text = models.TextField(verbose_name='Комментарий')
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
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return '"{}" to review "{}" by author "{}"'.format(
            self.text, self.review, self.author
        )


class GenreTitle(models.Model):
    """Модель взаимосвязи жанров и произведений"""
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Жанры-произведения'

    def __str__(self):
        return f'{self.genre} - {self.title}'
