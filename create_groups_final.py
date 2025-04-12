
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from users.models import User, Follow
from music.models import Track, Interaction, TrackFeature
from playlists.models import Playlist
from subscriptions.models import Subscription, SubscriptionPlan

# Create or get groups
roles = ['listener', 'artist', 'moderator', 'admin']
groups = {role: Group.objects.get_or_create(name=role)[0] for role in roles}

# Helper function to get permission safely
def get_perm(model, codename):
    ct = ContentType.objects.get_for_model(model)
    return Permission.objects.get(codename=codename, content_type=ct)

# Listener permissions
listener_perms = [
    get_perm(User, 'view_user'),
    get_perm(Track, 'view_track'),
    get_perm(Interaction, 'view_interaction'),
    get_perm(Interaction, 'add_interaction'),
    get_perm(Interaction, 'delete_interaction'),
    get_perm(Follow, 'add_follow'),
    get_perm(Follow, 'delete_follow'),
    get_perm(Playlist, 'view_playlist'),
]
groups['listener'].permissions.set(listener_perms)

# Artist = Listener + add/delete tracks, view analytics
artist_perms = listener_perms + [
    get_perm(Track, 'add_track'),
    get_perm(Track, 'delete_track'),
    get_perm(Track, 'change_track'),
    get_perm(TrackFeature, 'view_trackfeature'),
    get_perm(SubscriptionPlan, 'view_subscriptionplan'),
    get_perm(Subscription, 'add_subscription'),
    get_perm(Subscription, 'delete_subscription'),
    get_perm(Subscription, 'view_subscription'),
]
groups['artist'].permissions.set(artist_perms)

# Moderator = Listener + approve/reject tracks and artist accounts
moderator_perms = listener_perms + [
    get_perm(Track, 'change_track'),
    get_perm(User, 'change_user'),
    get_perm(SubscriptionPlan, 'add_subscriptionplan'),
    get_perm(SubscriptionPlan, 'delete_subscriptionplan'),
    get_perm(SubscriptionPlan, 'view_subscriptionplan'),
    get_perm(Subscription, 'add_subscription'),
    get_perm(Subscription, 'delete_subscription'),
    get_perm(Subscription, 'view_subscription'),
    get_perm(Playlist, 'change_playlist'),
]
groups['moderator'].permissions.set(moderator_perms)

# Admin gets all
groups['admin'].permissions.set(Permission.objects.all())

print("✅ Groups and permissions successfully created.")
