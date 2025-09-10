from django.contrib import admin
from .models import UserProfile, Follow, Duel

admin.site.register(UserProfile)
admin.site.register(Follow)
admin.site.register(Duel)