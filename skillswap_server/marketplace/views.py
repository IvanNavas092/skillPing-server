from rest_framework import viewsets
from .models import User, Skill, Category, Rating
from .serializers import UserSerializer, SkillSerializer, CategorySerializer, RatingSerializer, userLoginSerializer
# Tokens imports
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# pusher chat
from .pusher import pusher_client

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer



# Autentication Functions
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # autentica el usuario, y genera el token
        jwt_response = super().post(request, *args, **kwargs)
        if jwt_response.status_code == 200:
            User = get_user_model()

            try:
                user = User.objects.get(username = request.data['username'])
                user_data = userLoginSerializer(user).data
                # Construyo mi respuesta personalizada combinando los datos del token y el usuario
                custom_response = ({
                    'access_token' : jwt_response.data['access'],
                    'refresh_token' : jwt_response.data['refresh'],
                    'user': user_data
                })
                print(custom_response)
                return Response(custom_response)
            
            except User.DoesNotExist:
                return Response({'Error: Credenciales incorrectas'}, status= 401)
            
        # si hay error devuelvo el error original
        return jwt_response
    

# CHAT

class messageAPIView(APIView):
    def post(self, request):
        pusher_client.trigger('chat', 'message', {
            'username': request.data['username'],
            'message': request.data['message']
        })
        return Response({'message': 'ok'})