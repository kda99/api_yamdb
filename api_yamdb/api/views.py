from django.db.models import Avg
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, viewsets, status
from rest_framework.pagination import (PageNumberPagination,
                                       LimitOffsetPagination)
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS

from reviews.models import Category, Genre, Title, Review, User
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (UserSerializer, UserEditSerializer,
                          CategorySerializer, GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer,
                          ReadOnlyTitleSerializer)


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

    def perform_create(self, serializer):
        serializer.save()


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
    permission_classes = (IsAuthorOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
