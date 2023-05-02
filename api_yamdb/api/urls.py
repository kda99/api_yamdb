from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (UserViewSet, CommentViewSet, ReviewViewSet,
                    CategoryViewSet, TitleViewSet, GenreViewSet, SignUpViewSet, TokenViewSet)

router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                   r'/comments', CommentViewSet, basename='comments')
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'auth/signup', SignUpViewSet, basename='auth')
router_v1.register(r'auth/token', TokenViewSet, basename='token')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
