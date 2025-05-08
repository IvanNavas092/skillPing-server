from rest_framework import serializers
from .models import Avatar, User, Skill, Category, Rating, Message
from django.contrib.auth.hashers import make_password

# 
# Skill Serializer 
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"

# Category Serializer     
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# Rating Serializer 
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
        

        
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    # 2 tipos de serializers
    # campos de solo lectura para mostrar detalles
    skills_details = SkillSerializer(source='skills', many=True, read_only=True)
    interests_details = SkillSerializer(source='interests', many=True, read_only=True)

    # Campo de escritura para crear usuarios con sus respectivos skills e intereses para no cargar todo el objeto
    skills = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, write_only=True)
    interests = serializers.PrimaryKeyRelatedField(queryset=Skill.objects.all(), many=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 
                'description', 'average_rating',
                'rating_count', 'skills', 'interests', 'skills_details',
                'interests_details', 'location', 'avatar', 'gender',
                'age', 'last_login', 'password']


    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    

# Serliazer para autenticar usuarios
class userLoginSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    interests = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 
                'description', 'average_rating',
                'rating_count', 'skills', 'interests', 'location',
                'avatar', 'gender', 'age']
        
class updateUserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    interests = SkillSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 
                'description', 'average_rating',
                'rating_count', 'skills', 'interests', 'location',
                'avatar', 'gender', 'age']

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username')
    receptor = serializers.CharField(source='receptor.username')
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receptor', 'message', 'timestamp']
        
class avatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = ['id', 'name', 'img', 'selected']

