from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLS = ((ADMIN, 'admin'), (MODERATOR, 'moderator'), (USER, 'user'))

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
    first_name = models.TextField(
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.TextField(
        max_length=150,
        verbose_name='Фамилия',
    )
    confirmation_code = models.TextField(max_length=40)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(username__iexact='me'),
                name='username_is_not_me'
            )
        ]


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
    year = models.PositiveSmallIntegerField(
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
        default='Жанр'
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
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
