from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from users.utils import assign_user_role

@receiver(post_save, sender=User)
def set_group_on_user_creation(sender, instance, created, **kwargs):
    if created:
        assign_user_role(instance)