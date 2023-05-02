from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.db.models import Avg
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import (PageNumberPagination,
                                       LimitOffsetPagination)
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework import mixins
from django.core.mail import send_mail
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Title, Review, User
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (UserSerializer, UserEditSerializer,
                          LoginAPISerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer,
                          ReadOnlyTitleSerializer, SignUpSerializer, TokenSerializer)

JWT_SECRET_KEY = settings.SECRET_KEY


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdmin,)

    @action(
        methods=["get", "patch"], detail=False, url_path="me",
        pagination_class=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer
    )
    def user_own_profile(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.seve()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


'''
class LoginAPI(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginAPISerializer(data = data)
            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']
                user = authenticate(email=email, password=password)
                if user is not None:
                    refresh = RefreshToken.for_user(user)
                    return {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
            return Response(
                'status': 400,
                'message': "Invalid password",
                'data': {},}
            )
'''


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def read_or_create(self):
        if self.request.method in SAFE_METHODS:
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CreateRetrieveViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass
#
#
# class SignUp(CreateRetrieveViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer



class SignUpViewSet(viewsets.ViewSet):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny,]

    def create(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")

        confirmation_code = User.objects.make_random_password(40)
        user = User.objects.create_user(username=username, email=email, confirmation_code=confirmation_code)

        send_mail(
            'Confirmation code for YaMDB',
            f'Your confirmation code for YaMDB is {confirmation_code}',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return Response({"email": email, "username": username}, status=200)

class TokenViewSet(CreateRetrieveViewSet):

    def create(self, request):
        user = request.user
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data.get("confirmation_code")
        username = serializer.validated_data.get("username")
        if username == user.username and confirmation_code == user.confirmation_code:
            token = AccessToken.for_user(user)
            return Response({"token": token}, status=200)
        else:
            return Response({}, status=400)
