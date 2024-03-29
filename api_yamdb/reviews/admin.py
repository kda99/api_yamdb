from django.contrib import admin

from reviews.models import (Category, Comment, Genre, Review,
                            Title, User, GenreTitle)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(GenreTitle)
