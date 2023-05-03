from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status, filters
from rest_framework.pagination import (LimitOffsetPagination, PageNumberPagination)
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework import mixins
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.db.utils import IntegrityError

from reviews.models import Category, Genre, Title, Review, User
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly, IsAdminOrSuperUser
from .serializers import (UserSerializer,
                          CategorySerializer, GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer,
                          UserEditSerializer,
                          ReadOnlyTitleSerializer, SignUpSerializer,
                          TokenSerializer, AdminSerializer,)

JWT_SECRET_KEY = settings.SECRET_KEY


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        url_path='me',
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserEditSerializer,
    )
    def users_own_profile(self, request):
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
            serializer.save()
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
        rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class CreateRetrieveViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    pass
#
#
# class SignUp(CreateRetrieveViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# class SignUpViewSet(viewsets.ViewSet):
#     serializer_class = SignUpSerializer
#     permission_classes = [AllowAny, ]
#
#     def create(self, request):
#         serializer = SignUpSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         email = serializer.validated_data.get("email")
#         username = serializer.validated_data.get("username")
#         confirmation_code = User.objects.make_random_password(40)
#         user = User.objects.create_user(username=username, email=email,
#                                         confirmation_code=confirmation_code)
#
#         send_mail(
#             'Confirmation code for YaMDB',
#             f'Your confirmation code for YaMDB is {confirmation_code}',
#             'from@example.com',
#             [user.email],
#             fail_silently=False,
#         )
#
#         return Response({"email": email, "username": username}, status=200)
#
#
# class TokenViewSet(CreateRetrieveViewSet):
#
#     def create(self, request):
#         user = request.user
#         serializer = TokenSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         confirmation_code = serializer.validated_data.get("confirmation_code")
#         username = serializer.validated_data.get("username")
#         if (username == user.username
#                 and confirmation_code == user.confirmation_code):
#             token = AccessToken.for_user(user)
#             return Response({"token": token}, status=200)
#         else:
#             return Response({}, status=400)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAdminOrSuperUser]
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated],
            serializer_class=UserSerializer,
            pagination_class=None)
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    confirmation_code = default_token_generator.make_token(user)
    email = user.email
    send_mail(
        f' Ваш код подтверждения: {confirmation_code}',
        [f'{email}'],
        fail_silently=False,
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer._validated_data['username']
    code = serializer._validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, code):
        token = RefreshToken.for_user(user)
        return Response(str(token.access_token), status=status.HTTP_200_OK)
    return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)