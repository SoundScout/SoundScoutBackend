from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Track)
admin.site.register(TrackFeature)
admin.site.register(Interaction)
#admin.site.register(Comment)
admin.site.register(ListeningHistory)
admin.site.register(TrackStatistics)




