from django.shortcuts import render
from reviews.models import Category, Genre, Title, Review, Comment
from rest_framework import pagination, permissions, viewsets
from django.shortcuts import get_object_or_404
# from .permissions import IsAdminUserOrReadOnly
# from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
#                           ReviewSerializer, CommentSerializer)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    # serializer_class = CategorySerializer
    # permission_classes = (permissions.IsAdminUserOrReadOnly,)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    # serializer_class = GenreSerializer
    # permission_classes = (permissions.IsAdminUserOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    # serializer_class = TitleSerializer
    # permission_classes = (permissions.IsAdminUserOrReadOnly,)
    # pagination_class = pagination.LimitOffsetPagination - не забыть прописать в settings

    def perform_create(self, serializer):
        serializer.save


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    # serializer_class = ReviewSerializer
    # permission_classes = (IsAuthorOrReadOnly,)
    # pagination_class = pagination.LimitOffsetPagination - не забыть прописать в settings

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    # serializer_class = CommentSerializer
    # permission_classes = (IsAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()
