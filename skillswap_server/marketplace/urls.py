from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, SkillViewSet, UserViewSet, CategoryViewSet, RatingViewSet, CustomTokenObtainPairView
from .pusher import chat

# webSockets Imports

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'messages', MessageViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('chat', chat, name= 'chat'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]

