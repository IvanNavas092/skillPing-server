from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser


# --------------------
# MODELO DE CATEGORIA
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    
# --------------------
# MODELO DE SKILL
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name="skills", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
    
# --------------------
# MODELO DE VALORACION
class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 - Muy malo'),
        (2, '2 - Malo'),
        (3, '3 - Regular'),
        (4, '4 - Bueno'),
        (5, '5 - Excelente'),
    ]
    # Foráneas
    rated_user = models.ForeignKey('User', related_name='received_ratings', on_delete=models.CASCADE ) # Usuario que recibe la valoración
    rating_user = models.ForeignKey('User', related_name='given_ratings', on_delete=models.SET_NULL, null=True, blank=True ) # Usuario que valora
    # elecciones del usuario (1-5, comentario y fecha)	
    value = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('rated_user', 'rating_user')  # Para evitar múltiples valoraciones del mismo usuario
    
    def __str__(self):
        return f"{self.rating_user} → {self.rated_user}: {self.value}"
    
    

# --------------------
# MODELO DE USUARIO
class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    full_name = models.CharField(max_length=35)
    description = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name="users_with_skill")
    interests = models.ManyToManyField(Skill, related_name="users_interested_in")
    location = models.CharField(max_length=35, blank=True)
    disponibility = models.CharField(max_length=35, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    
    # Campos calculados para valoraciones
    rating_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    
    def update_rating_stats(self):
        """Actualiza las estadísticas de valoración"""
        # aggregate para obtener la media y el contador de opiniones
        stats = self.received_ratings.aggregate(
            average = Avg('value'), # Media
            count = models.Count('id') # Contador de opiniones
        )
        # Asigno al user la media y el contador de opiniones 
        self.average_rating = stats['average'] or 0.00
        self.rating_count = stats['count'] or 0
        self.save()

    def __str__(self):
        return self.username