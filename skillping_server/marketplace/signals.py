from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Rating

@receiver(post_save, sender=Rating) # post_save -> after a model is saved
def update_rating_stats_on_change(sender, instance, **kwargs):
    """
    Update statistics when a Rating is created or modified
    """
    instance.rated_user.update_rating_stats()

@receiver(post_delete, sender=Rating) # post_delete -> after a model is deleted
def update_rating_stats_on_delete(sender, instance, **kwargs):
    """
    Update statistics when a Rating is removed or modified
    """
    instance.rated_user.update_rating_stats()