from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api_yamdb.reviews.models import User, Comment, Review, Title


class UserSerializers(serializers.ModelSerializer):
    username = serializers.CharField(
        validatirs=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )
    email = serializers.EmailField(
        validatirs=[
            UniqueValidator(queryset=User.objects.all())
        ],
        required=True,
    )

    class Meta:
        fields = '__all__'
        model = User


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('title',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('review',)


class LoginAPISerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
