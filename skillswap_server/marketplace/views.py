from django.shortcuts import get_object_or_404
import requests
from rest_framework import viewsets
from .models import User, Skill, Category, Rating, Message
from .serializers import MessageSerializer, UserSerializer, SkillSerializer, CategorySerializer, RatingSerializer, userLoginSerializer
# Tokens imports
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
# Chat imports
from rest_framework.decorators import api_view
from django.db.models import Q




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

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer



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
    

@api_view(['GET'])
def get_chat_history(request):
    user1 = request.query_params.get('user1')
    user2 = request.query_params.get('user2')

    if not user1 or not user2:
        return Response({'Error: Faltan usuarios'}, status= 400)
        
    # filter messages between user1 and user2
    messages = Message.objects.filter(
        Q(sender__username=user1, receptor__username=user2) |
        Q(sender__username=user2, receptor__username=user1)
    ).order_by('timestamp')

    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)
        
# take skills from category
@api_view(['GET'])
def users_by_category(request, category_name):
    category = get_object_or_404(Category, name=category_name)
        
    # Obtener skills de esa categoría
    skills_in_category = Skill.objects.filter(category=category)
    # Filtrar usuarios que tienen al menos una de esas skills
    users = User.objects.filter(skills__in=skills_in_category).distinct()
    serialized_users = UserSerializer(users, many=True)
    return Response(serialized_users.data)


# take countries from API
@api_view(['GET'])
def get_countries(request):
    api_url = 'https://restcountries.com/v3.1/all'
    try:
        response = requests.get(api_url)
        countries = sorted([c['name']['common'] for c in response.json()])
        
        print(countries)
        return Response(countries)
    except:
        return Response({'Error: No se pudo obtener los países'})
    
    
# Edit User

