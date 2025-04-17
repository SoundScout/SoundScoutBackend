# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from users.models import User
from users.utils import assign_group  # your helper

@receiver(post_save, sender=User)
def sync_user_group(sender, instance, **kwargs):
    """
    After any User.save(), ensure their group matches their role.
    """
    assign_group(instance)