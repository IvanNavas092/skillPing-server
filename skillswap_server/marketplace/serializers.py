from rest_framework import serializers
from .models import User, Skill, Category, Rating
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
        fields = '__all__' 


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
                'rating_count', 'skills', 'interests']

