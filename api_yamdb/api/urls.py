from django.urls import include, path
from rest_framework.routers import DefaultRouter


from .views import (UserViewSet, CommentViewSet, ReviewViewSet,
                    CategoryViewSet, TitleViewSet, GenreViewSet,
                    signup, token, update_profile)

router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'titles/(?P<titel_id>\d+)/reviews', ReviewViewSet,
                   basename='reviews')
router_v1.register(r'titles/(?P<titel_id>\d+)/reviews/(?P<review_id>\d+)'
                   r'/comments', CommentViewSet, basename='comments')
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'titles', TitleViewSet)
# router_v1.register(r'auth/signup/', signup)
# router_v1.register(r'auth/token/', token)
# router_v1.register(r'users/me/', update_profile)

urlpatterns = [
    path('api/v1/', include(router_v1.urls)),
    path('api/v1/auth/signup/', signup, name='auth_signup'),
    # path('auth/signup/', signup, name='auth_signup'),
    # path('auth/token/', token, name='token'),
    # path('users/me/', update_profile, name='update_profile'),

]
