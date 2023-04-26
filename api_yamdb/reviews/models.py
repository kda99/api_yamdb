from django.db import models


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
    text = models.TextField(verbose_name='Описание произведения', help_text='Введите описание произведения')
    genre = models.ForeignKey('Genre', on_delete=models.SET_DEFAULT, verbose_name='Жанр произведения')
    category = models.ForeignKey('Category', on_delete=models.SET_DEFAULT, verbose_name='Категория произведения')

    class Meta:
        ordering = ('pub_date',)

    def __str__(self):
        return self.name


class Comment(models.Model):
    """Модель комментария к отзыву"""
    #title_id integer (ID произведения)
    #review_id integer (ID отзыва)
    #"id": 0, 
    #"text": "string", (Текст комментария)
    #"author": "string",
    #"pub_date": "2019-08-24T14:15:22Z"

    pass


class Review(models.Model):
    """Модель отзыва"""
    #"text": "string", string (Текст отзыва)
    #"score": 1 	 integer (Оценка) [ 1 .. 10 ]
    #title_id   integer  (ID произведения)
    #"pub_date": "2019-08-24T14:15:22Z"
    #"author": "string",
    #"id": 0,

    pass