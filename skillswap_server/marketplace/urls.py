from django.urls import path, include
from . import views
from .views import *
from . import views_api_view
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"users", UserViewSet, basename="user")
router.register(r"update-user", UpdateUserViewSet , basename="update-user")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"ratings", RatingViewSet, basename="rating")
router.register(r"messages", MessageViewSet, basename="message")

urlpatterns = [
    # api endpoints
    path("", include(router.urls)),
    # other endpoints
    # current user
    path('current-user/', views_api_view.current_user),
    # LOGIN / LOGOUT API
    path("login/", views_api_view.login_view, name="login"),
    path("logout/", views_api_view.logout_view, name="logout"),
    # CHANGE PASSWORD
    path("change-password/", views_api_view.change_password, name="change_password"),
    # GET USER BY ID
    path("get-user/<int:id>/", views_api_view.get_user_by_id, name="get_user_by_id"),
    # GET RATINGS BY USER
    path("user-ratings/<int:id>/", views_api_view.get_user_ratings, name="get_user_ratings"),
    # GET USERS BY CATEGORY
    path(
        "users-by-category/<str:category_name>/",
        views_api_view.users_by_category,
        name="users_by_category",
    ),
    # GET COUNTRIES
    path("get-countries/", views_api_view.get_countries, name="get_countries"),
    # CHAT VIEWS
    path("chat-history/", views_api_view.get_chat_history, name="get_chat_history"),
    path("chat/send/", views_api_view.chat, name="chat_send"),
    path("chat/mark-messages-as-read/", views_api_view.mark_messages_as_read, name="mark_messages_as_read"),
    path("chat/get-unread-counts/", views_api_view.get_unread_counts, name="get_unread_counts"),
]
