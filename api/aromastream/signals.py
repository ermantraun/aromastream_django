from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Subscription

User = get_user_model()

@receiver(post_save, sender=User)
def user_created(**kwargs):
    if kwargs['created']:
        Subscription.objects.create(user=kwargs['instance'])
        