from django.contrib.auth import authenticate
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, pagination, viewsets
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, User
from .serializers import UserSerializers, CommentSerializer, ReviewSerializer
'''
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
                          ReviewSerializer, CommentSerializer, ReadOnlyTitleSerializer)
'''

from .serializers import LoginAPISerializer


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializers


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.review.all()


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
            return Response({
                'status': 400,
                'message': "Invalid password",
                'data': {},}
            )

'''
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    # serializer_class = CategorySerializer
    # permission_classes = (permissions.IsAdminOrReadOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    # serializer_class = GenreSerializer
    # permission_classes = (permissions.IsAdminOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    # serializer_class = TitleSerializer
    # permission_classes = (permissions.IsAdminOrReadOnly,)
    # pagination_class = pagination.LimitOffsetPagination - не забыть прописать в settings

    def read_or_create(self):
        if self.request.method in SAFE_METHODS:
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    # serializer_class = ReviewSerializer
    # permission_classes = (IsAuthorOrReadOnly,)
    # pagination_class = pagination.LimitOffsetPagination - не забыть прописать в settings

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    # serializer_class = CommentSerializer
    # permission_classes = (IsAuthorOrReadOnly,)
    # pagination_class = pagination.LimitOffsetPagination - не забыть прописать в settings

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs['review_id'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.all()
'''
