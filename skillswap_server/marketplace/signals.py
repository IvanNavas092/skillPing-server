# marketplace/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Rating

@receiver(post_save, sender=Rating) # post_save -> despues de que un modelo se guarda
def update_rating_stats_on_change(sender, instance, **kwargs):
    """
    Actualiza las estadísticas cuando se crea o modifica una Rating
    """
    instance.rated_user.update_rating_stats()

@receiver(post_delete, sender=Rating) # post_delete -> despues de que un modelo se elimina
def update_rating_stats_on_delete(sender, instance, **kwargs):
    """
    Actualiza las estadísticas cuando se elimina una Rating
    """
    instance.rated_user.update_rating_stats()