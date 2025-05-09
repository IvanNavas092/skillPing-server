from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .pusher import *

# webSockets Imports

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'users', UserViewSet, basename='users')
router.register(r'categories', CategoryViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'users/update-user', updateUserViewSet, basename='update-user')


urlpatterns = [
    path('', include(router.urls)),
    path('chat/send', chat, name= 'send-message'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('users/by-category/<category_name>', users_by_category, name='users-by-category'),
    path('chat/history/', get_chat_history, name='get-chat-history'),
    path('countries/', get_countries, name='get-countries'),
    path('users/<int:id>', getUserById, name='get-user-by-id'),
]

