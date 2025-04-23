from django.contrib import admin
from .models import Skill, User, Category, Rating
# Register your models here.



admin.site.register(Skill)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Rating)
