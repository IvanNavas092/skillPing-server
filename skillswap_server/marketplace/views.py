import json
from django.shortcuts import get_object_or_404
import requests
from rest_framework import viewsets
from .models import *
from .serializers import *
from django.utils import timezone   
from django.db.models import Count
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.authentication import SessionAuthentication
from django.middleware.csrf import get_token

# si mi usuario no tiene token CSRF, se genera automáticamente
from django.views.decorators.csrf import ensure_csrf_cookie


from django.db.models import Q


from marketplace.pusher import pusher_client


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]


class UpdateUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = updateUserSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]


# method to get csrf token
# asegura que siempre haya un token CSRF
@ensure_csrf_cookie
@api_view(["GET"])
def csrf_token_view(request):
    token = get_token(request)
    return Response({"csrfToken": token})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# -----------------
# CHANGE PASSWORD
# -----------------
@api_view(["PUT"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )

    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Contraseña cambiada correctamente."}, status=200)

    return Response(serializer.errors, status=400)


# -----------------
# LOGIN / LOGOUT API
# -----------------


@api_view(["POST"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        user_data = userLoginSerializer(user).data
        return Response({"message": "Login correcto", "user": user_data})
    else:
        return Response({"error": "Credenciales incorrectas"}, status=401)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response({"message": "Logout correcto"})


# -----------------
# GET USERS BY CATEGORY
# -----------------
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def users_by_category(request, category_name):
    category = get_object_or_404(Category, name=category_name)

    skills_in_category = Skill.objects.filter(category=category)
    users = User.objects.filter(skills__in=skills_in_category).distinct()
    serialized_users = UserSerializer(users, many=True)
    return Response(serialized_users.data)


# -----------------
# GET COUNTRIES LIST
# -----------------
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_countries(request):
    api_url = "https://restcountries.com/v3.1/all"
    try:
        response = requests.get(api_url)
        countries = sorted([c["name"]["common"] for c in response.json()])
        return Response(countries)

    except requests.RequestException as e:
        return Response({"error": str(e)}, status=502)


# -----------------
# GET USER BY ID
# -----------------
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_user_by_id(request, id):
    try:
        user = User.objects.get(id=id)
        user_data = UserSerializer(user).data
        return Response(user_data)
    except User.DoesNotExist:
        return Response({"Error: Usuario no encontrado"}, status=404)


# -----------------
# GET USER RATINGS
# -----------------
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_user_ratings(request, id):
    try:
        user = User.objects.get(id=id)
        ratings = Rating.objects.filter(rated_user=user).order_by("-created_at")

        rating_data = []
        for rating in ratings:
            rating_data.append(
                {
                    "rating_user": rating.rating_user.username,
                    "avatar": rating.rating_user.avatar,
                    "value": rating.value,
                    "comment": rating.comment,
                    "created_at": rating.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        return Response(rating_data)
    except User.DoesNotExist:
        return Response({"Error: Usuario no encontrado"}, status=404)


# CHAT VIEWS


# -----------------
# GET CONVERSATION BETWEEN TWO USERS
# -----------------
@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_chat_history(request):
    user1 = request.query_params.get("user1")
    user2 = request.query_params.get("user2")

    if not user1 or not user2:
        return Response({"Error: Faltan usuarios"}, status=400)

    messages = Message.objects.filter(
        Q(sender__username=user1, receptor__username=user2)
        | Q(sender__username=user2, receptor__username=user1)
    ).order_by("timestamp")

    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)


# -----------------
# SEND MESSAGE, COUNT, INTERACTIONS, ETC...
# -----------------
@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Envía un mensaje privado entre dos usuarios, notifica vía Pusher
    y devuelve el ID del mensaje y el nuevo contador de no leídos.
    """
    data = request.data
    sender_username = data.get('sender')
    receptor_username = data.get('receptor')
    content = data.get('message')

    # Validación de campos requeridos
    if not sender_username or not receptor_username or content is None:
        return Response(
            {"error": "Debe proporcionar 'sender', 'receptor' y 'message'."},
            status=400
        )

    # Recuperar instancias de usuario
    try:
        sender = User.objects.get(username=sender_username)
        receptor = User.objects.get(username=receptor_username)
    except User.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado."},
            status=404
        )

    # Crear y guardar el mensaje
    new_message = Message.objects.create(
        sender=sender,
        receptor=receptor,
        message=content,
        is_read=False
    )

    # Contar total de mensajes intercambiados
    total_msgs = Message.objects.filter(
        sender__in=[sender, receptor],
        receptor__in=[sender, receptor]
    ).count()

    # Incrementar interacciones si llegan a 11 mensajes
    if total_msgs == 11:
        sender.interactions += 1
        sender.save(update_fields=["interactions"])

    # Contar no leídos del receptor
    unread_count = Message.objects.filter(
        receptor=receptor,
        is_read=False
    ).count()

    # Generar ID de sala
    room_id = f"room-chat-{sorted([sender.username, receptor.username])[0]}_{sorted([sender.username, receptor.username])[1]}"

    # Notificar nuevo mensaje por Pusher
    pusher_client.trigger(
        room_id,
        "new-message",
        {
            "sender": sender.username,
            "receptor": receptor.username,
            "message": content,
            "timestamp": timezone.now().isoformat()
        }
    )

    # Notificar al receptor de nuevos no leídos
    pusher_client.trigger(
        f"notifications-{receptor.username}",
        "unread-messages",
        {
            "unread_counts": unread_count,
            "sender": sender.username,
        }
    )

    return Response(
        {
            "status": "ok",
            "message_id": new_message.id,
            "unread_count": unread_count
        },
        status=201
    )


# -----------------
# MARK MESSAGES AS READ
# -----------------
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def mark_messages_as_read(request):
    # 1) Usa request.data en lugar de leer request.body
    current_username = request.data.get("current_user")
    sender_username = request.data.get("sender")

    if not current_username or not sender_username:
        return Response(
            {"error": 'Debe proporcionar "current_user" y "sender".'},
            status=400,
        )

    try:
        current_user = User.objects.get(username=current_username)
        sender = User.objects.get(username=sender_username)
    except User.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado."}, status=404
        )

    # Marcar como leídos
    Message.objects.filter(sender=sender, receptor=current_user, is_read=False).update(
        is_read=True
    )

    # Nuevo conteo de no leídos
    unread_count = Message.objects.filter(receptor=current_user, is_read=False).count()

    # Notificar cambio por Pusher
    pusher_client.trigger(
        f"notifications-{current_user.username}",
        "unread-messages",
        {"unread_counts": unread_count, "sender": sender.username},
    )

    return Response({"status": "success", "new_unread_count": unread_count})


# -----------------
# GET UNREAD COUNTS FOR A USER
# -----------------
@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_unread_counts(request):
    # 1) Validamos que venga 'username'
    username = request.data.get("username")
    if not username:
        return Response({"error": 'Falta el parámetro "username".'}, status=400)

    # 2) Intentamos recuperar el usuario
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({"error": "Usuario no encontrado."}, status=400)

    # 3) Calculamos totales y por remitente
    total_unread = Message.objects.filter(receptor=user, is_read=False).count()

    senders_unread = (
        Message.objects.filter(receptor=user, is_read=False)
        .values("sender__username")
        .annotate(count=Count("id"))
    )

    return Response(
        {
            "status": "success",
            "total_unread": total_unread,
            "by_sender": list(senders_unread),
        }
    )
