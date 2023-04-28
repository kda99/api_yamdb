from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, CommentViewSet, ReviewViewSet

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('review', ReviewViewSet, basename='review')
router_v1.register('posts/(?P<post_id>\\d+)/comments', CommentViewSet,
                   basename='comments')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    #path('v1/', include('djoser.urls.jwt')),
]
