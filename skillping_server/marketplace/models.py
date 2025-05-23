from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser


# --------------------
# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
    
# --------------------
# Skill Model
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name="skills", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
    
# --------------------
# Rating Model
class Rating(models.Model):
    RATING_CHOICES = [
        (1, '1 - Muy malo'),
        (2, '2 - Malo'),
        (3, '3 - Regular'),
        (4, '4 - Bueno'),
        (5, '5 - Excelente'),
    ]
    # Foreign Keys
    rated_user = models.ForeignKey('User', related_name='received_ratings', on_delete=models.CASCADE ) # User receiving the rating
    rating_user = models.ForeignKey('User', related_name='given_ratings', on_delete=models.SET_NULL, null=True, blank=True ) # User who values
    # user elections (1-5, comment and date)	
    value = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('rated_user', 'rating_user')  # To avoid multiple ratings from the same user
    
    def __str__(self):
        return f"{self.rating_user} → {self.rated_user}: {self.value}"
    
# --------------------
# User Model
class User(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    AVATAR_CHOICES = [
        (1, 'Héctor'),
        (2, 'Manuel'),
        (3, 'Ana'),
        (4, 'Ingrid'),
    ]

    avatar = models.CharField(max_length=35, choices=AVATAR_CHOICES, blank=True, null=True)
    full_name = models.CharField(max_length=35)
    age = models.CharField(max_length=2, null=True, blank=True) 
    location = models.CharField(max_length=35, blank=True, default="No especificado")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    description = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name="users_with_skill")
    interests = models.ManyToManyField(Skill, related_name="users_interested_in")
    interactions = models.PositiveIntegerField(default=0, blank=True)
    # ratings
    rating_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    

    # convert first letter to uppercase -> juan perez -> Juan Perez
    def save(self, *args, **kwargs):
        if self.full_name:
            self.full_name = self.full_name.title()
        super().save(*args, **kwargs)
        
    def update_rating_stats(self):
        """Update statistics"""
        # aggregate for obtain avg and counter of opinions
        stats = self.received_ratings.aggregate(
            average = Avg('value'), # Media
            count = models.Count('id') # ratings counter
        )
        # asign user avg and counter of opinions
        self.average_rating = stats['average'] or 0.00
        self.rating_count = stats['count'] or 0
        self.save()

    def __str__(self):
        return self.username
    
# Message Model
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receptor = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']