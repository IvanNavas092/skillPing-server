from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .chat_views import *

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
    # chat
    path('chat/send', chat, name= 'send-message'),
    path('chat/mark-messages-as-read', mark_messages_as_read, name='mark-messages-as-read'),
    path('chat/get-unread-counts', get_unread_counts, name='get-unread-counts'),
    path('chat/history/', get_chat_history, name='get-chat-history'),
    # autentication
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    # categories
    path('users/by-category/<category_name>', users_by_category, name='users-by-category'),
    # countries
    path('countries/', get_countries, name='get-countries'),
    # search users by id
    path('users/<int:id>', getUserById, name='get-user-by-id'),
    # search rating
    path('ratings/<str:id>', get_user_ratings, name='get-user-ratings'),
    path('change-password/', change_password, name='change-password'),
]

