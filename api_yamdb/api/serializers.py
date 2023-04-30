from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from rest_framework.generics import get_object_or_404
from django.core.validators import EmailValidator, MaxLengthValidator, RegexValidator

from reviews.models import User, Category, Genre, Title, Review, Comment


# def validate_


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(limit_value=150),
            RegexValidator(r'^[\w.@+-]+$', code=400),

        ],
        required=True,
    )
    email = serializers.EmailField(
        max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator(code=400),
            MaxLengthValidator(limit_value=254),
        ],
        required=True,
    )

    class Meta:
        fields = '__all__'
        model = User


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User
        read_only_fields = ('role',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('title', 'review')


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field='username',
        read_only=True)

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise exceptions.ValidationError('Вы не можете написать более'
                                                 'одного отзыва')
        return data

    class Meta:
        fields = '__all__'
        model = Review


class LoginAPISerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        many=True
    )
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'
        read_only_fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class SignUpSerializer(serializers.ModelSerializer):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
