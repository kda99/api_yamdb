from django.db import models
from django.contrib.postgres.fields import ArrayField


class Category(models.Model):
    """Модель категории произведения"""
    
    #"name": "string", <= 256 characters
    #"slug": "string" <= 50 characters ^[-a-zA-Z0-9_]+$

    pass


class Genre(models.Model):
    """Модель жанра произведения"""
    
    #"name": "string", <= 256 characters
    #"slug": "string" - поле slug каждого жанра должно быть уникальным <= 50 characters ^[-a-zA-Z0-9_]+$


    pass


class Title(models.Model):
    """Модель произведения, к которому пишут отзывы"""
    name = models.CharField(max_length=256, verbose_name='Название произведения')
    year = models.IntegerField(max_length=4, blank=True, null=True, verbose_name='Год выпуска')
    text = models.TextField('Описание произведения', help_text='Введите описание произведения')
    
    #здесь сделал ArrayField, потому что это указывают в документации
    #возможно, это не правильно. Это правильно при условии, что можно выбрать несколько жанров
    #для одного произведения. Но, как я понял, можно выбрать только один жанр. Буду разбираться.
    genre = ArrayField(
        models.CharField(max_length=10, blank=True),
    )
    category = models.ForeignKey(Category, verbose_name='Категории')

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва"""
    #"text": "string", string (Текст отзыва)
    #"score": 1 	 integer (Оценка) [ 1 .. 10 ]
    #title_id   integer  (ID произведения)
    #"pub_date": "2019-08-24T14:15:22Z"
    #"author": "string",
    #"id": 0,
    author = models.ForeignKey(
        #User, #Пока нет юзера
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва'
    )
    titel = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Комментарий')
    score = models.IntegerChoices() #Буду разбираться, как лучше сделать выбор
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'titel'], name='unique_reviewing'
            )
        ]


class Comment(models.Model):
    """Модель комментария к отзыву"""
    #title_id integer (ID произведения)
    #review_id integer (ID отзыва)
    #"id": 0, 
    #"text": "string", (Текст комментария)
    #"author": "string",
    #"pub_date": "2019-08-24T14:15:22Z"
    author = models.ForeignKey(
        #User,
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
    titel = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Произведение'
    )
    text = models.TextField(verbose_name='Комментарий')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self):
        return '"{}" to review "{}" by author "{}"'.format(
            self.text, self.review, self.author
        )
