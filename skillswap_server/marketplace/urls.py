from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SkillViewSet, UserViewSet, CategoryViewSet, RatingViewSet, CustomTokenObtainPairView, messageAPIView

# webSockets Imports

router = DefaultRouter()
router.register(r'skills', SkillViewSet)
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'ratings', RatingViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('chat', messageAPIView.as_view()),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
]

