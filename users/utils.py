from django.contrib.auth.models import Group

def assign_user_role(user):
    try:
        group = Group.objects.get(name=user.role)
        user.groups.add(group)
    except Group.DoesNotExist:
        pass