from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MaxLengthValidator, RegexValidator, EmailValidator
from rest_framework.response import Response

from reviews.models import User, Category, Genre, Title, Review, Comment


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all())
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


UserValidator = RegexValidator(r'^[\w.@+-]+$', 'Enter a valid username.')
LengthValidator = MaxLengthValidator(150)


class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, validators=[EmailValidator])
    username = serializers.CharField(max_length=150, validators=[UserValidator, LengthValidator])

    # def validate_email(self, value):
    #     if User.objects.filter(email__iexact=value).exists():
    #         return Response({'message': 'This email address is already in use.'}, status=400)
    #     return value
    #
    # def validate_username(self, value):
    #     if User.objects.filter(username__iexact=value).exists():
    #         return Response({'message': 'This username is already in use.'}, status=400)
    #     return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        return validated_data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()

    def validate(self, attrs):
        try:
            user = User.objects.get(username=attrs['username'])
            if user.profile.confirmation_code != attrs['confirmation_code']:
                raise serializers.ValidationError('Invalid confirmation code')
            attrs['user'] = user
            return attrs
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
