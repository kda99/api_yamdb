from django.db.models import Avg
#from django.shortcuts import get_object_or_404
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status
from rest_framework.pagination import (PageNumberPagination,
                                       LimitOffsetPagination)
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import SAFE_METHODS
from django.core.mail import send_mail
import jwt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from reviews.models import Category, Genre, Title, Review, User
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (UserSerializer, UserEditSerializer,
                          CategorySerializer, GenreSerializer,
                          TitleSerializer, ReviewSerializer,
                          CommentSerializer, ReadOnlyTitleSerializer,)

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



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
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
    pagination_class = LimitOffsetPagination

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return self.get_title().reviews.all().annotate(int(Avg('score')))


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()


@api_view(['POST'])
def signup(request):
    email = request.POST.get('email')
    username = request.POST.get('username')

    # Validate username
    if username == 'me':
        return Response({'error': 'The use of the name "me" is not allowed.'}, status=400)

    # Validate input data
    if not email or not username:
        return Response({'error': 'Email and username are required.'}, status=400)

    # Create user object with is_active=False, which means the user is not yet verified.
    user = User.objects.create_user(username=username, email=email, is_active=False)

    # Generate confirmation code and send to the user's email.
    confirmation_code_payload = {'user_id': str(user.id)}
    confirmation_code = jwt.encode(confirmation_code_payload, JWT_SECRET_KEY).decode()
    message = f'Your confirmation code is {confirmation_code}.'
    send_mail('Confirm your account', message, from_email=None, recipient_list=[email], fail_silently=False)

    return Response({"email": email, "username": username}, status=201)

@api_view(['POST'])
def token(request):
    username = request.POST.get('username')
    confirmation_code = request.POST.get('confirmation_code')

    # Validate input data
    if not username or not confirmation_code:
        return Response({'error': 'Username and confirmation code are required.'}, status=400)

    # Verify the confirmation code and retrieve the user object.
    try:
        payload = jwt.decode(confirmation_code.encode(), JWT_SECRET_KEY)
        user_id = payload['user_id']
        user = User.objects.get(id=user_id, username=username, is_active=False)
    except Exception:
        return Response({'error': 'Invalid confirmation code.'}, status=400)

    # Activate the user and generate a JWT token.
    user.is_active = True
    user.save()
    token_payload = {'user_id': str(user.id)}
    token = jwt.encode(token_payload, JWT_SECRET_KEY).decode()

    return Response({'token': token}, status=200)

# @permission_classes([IsAuthenticated])
@api_view(['GET','PATCH'])
def update_profile(request):
    if request.method == 'PATCH':
        # Retrieve authenticated user from request object.
        user = request.user

        # Сheck user activation
        if not user.is_active:
            return Response({'message': 'Confirm your account.'}, status=400)

        # Update profile fields based on input data.
        if username := request.POST.get('username'):
            user.username = username
        if email := request.POST.get('email'):
            user.email = email
        if bio := request.POST.get('bio'):
            user.bio = bio
        if first_name := request.POST.get('first_name'):
            user.first_name = first_name
        if last_name := request.POST.get('last_name'):
            user.last_name = last_name

        # Save updated profile fields to database.
        user.save()

        return Response({
                        "username": username,
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "bio": bio,
                        },
                        status=200
        )

    return Response({
        "username": request.POST.get('username'),
        "email": request.POST.get('email'),
        "first_name": request.POST.get("first_name"),
        "last_name": request.POST.get("last_name"),
        "bio": request.POST.get("bio"),
    },
        status=200
    )

