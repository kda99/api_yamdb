from django.db import models
from django.contrib.postgres.fields import ArrayField


class Categories(models.Model):
    """Модель категории произведения"""
    
    #"name": "string", <= 256 characters
    #"slug": "string" <= 50 characters ^[-a-zA-Z0-9_]+$

    pass


class Genres(models.Model):
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
    #здесь не использовал ForeignKey, потому что в документации указано, что эта модель string
    #опять же буду разбираться
    category = models.CharField(verbose_name='Slug категории')

    def __str__(self):
        return self.name


class Comments(models.Model):
    """Модель комментария к отзыву"""
    #title_id integer (ID произведения)
    #review_id integer (ID отзыва)
    #"id": 0, 
    #"text": "string", (Текст комментария)
    #"author": "string",
    #"pub_date": "2019-08-24T14:15:22Z"

    pass


class Reviews(models.Model):
    """Модель отзыва"""
    #"text": "string", string (Текст отзыва)
    #"score": 1 	 integer (Оценка) [ 1 .. 10 ]
    #title_id   integer  (ID произведения)
    #"pub_date": "2019-08-24T14:15:22Z"
    #"author": "string",
    #"id": 0,

    pass