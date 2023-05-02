from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from rest_framework.generics import get_object_or_404
from django.core.validators import (EmailValidator, MaxLengthValidator,
                                    RegexValidator, MinLengthValidator)
from reviews.models import User, Category, Genre, Title, Review, Comment


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
        fields = ("username", "email", "first_name",
                  "last_name", "bio", "role")
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
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


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
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator(code=400),
            MaxLengthValidator(limit_value=254)],)
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(limit_value=150),
            RegexValidator(r'^[\w.@+-]+$', code=400),
            MinLengthValidator(limit_value=3)
        ])

    class Meta:
        model = User
        fields = ['username', 'email']

    # def validate_username(self, data):
    #     if not re.fullmatch(data, r'^[\w.@+-]+$') or len(data) > 150:
    #         return Response(
    #             {},
    #             status=401
    #         )
    #     return data


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    class Meta:
        model = User
        fields = ['confirmation_code', 'username']
