import django_filters
from django_filters.rest_framework import Filter

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    category = Filter(field_name='category__slug')
    genre = Filter(field_name='genre__slug')
    year = django_filters.NumberFilter()
    name = django_filters.CharFilter(
        lookup_expr='icontains'
    )

    class Meta:
        model = Title
        fields = '__all__'
