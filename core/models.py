from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

HOUSES = (
    ('Gryffindor', 'Gryffindor'),   
    ('Hufflepuff', 'Hufflepuff'),
    ('Ravenclaw', 'Ravenclaw'),
    ('Slytherin', 'Slytherin'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    house = models.CharField(max_length=20, choices=HOUSES)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    house_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.house}"
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL , related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"