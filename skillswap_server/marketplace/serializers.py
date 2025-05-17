from rest_framework import serializers
from .models import *
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
        fields = "rated_user", "rating_user", "value", "comment"

    # validate if user has already rated
    def validate(self, data):
        if Rating.objects.filter(
            rating_user=data["rating_user"], rated_user=data["rated_user"]
        ).exists():
            raise serializers.ValidationError(
                # error non field errors for angular message
                {"non_field_errors": ["Ya has valorado a este usuario."]}
            )
        return data


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    # 2 tipos de serializers
    # campos de solo lectura para mostrar detalles
    skills_details = SkillSerializer(source="skills", many=True, read_only=True)
    interests_details = SkillSerializer(source="interests", many=True, read_only=True)

    # Campo de escritura para crear usuarios con sus respectivos skills e intereses para no cargar todo el objeto
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True
    )
    interests = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "description",
            "average_rating",
            "rating_count",
            "skills",
            "interests",
            "skills_details",
            "interests_details",
            "location",
            "avatar",
            "gender",
            "age",
            "last_login",
            "password",
            "interactions",
        ]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual no es correcta.")
        return value


# Serliazer para autenticar usuarios
class userLoginSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    interests = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "description",
            "average_rating",
            "rating_count",
            "skills",
            "interests",
            "location",
            "avatar",
            "gender",
            "age",
            "interactions",
        ]


class updateUserSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    interests = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "description",
            "average_rating",
            "rating_count",
            "skills",
            "interests",
            "location",
            "avatar",
            "gender",
            "age",
        ]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="sender.username")
    receptor = serializers.CharField(source="receptor.username")

    class Meta:
        model = Message
        fields = ["id", "sender", "receptor", "message", "timestamp", "is_read"]
