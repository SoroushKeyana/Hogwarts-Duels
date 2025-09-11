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
    

class Duel(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('finished', 'Finished'),
        ('cancelled', 'Cancelled'),
    )

    challenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="duels_started")
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="duels_received")
    
    challenger_health = models.IntegerField(default=10)
    opponent_health = models.IntegerField(default=10)
    
    last_spell_cast = models.CharField(max_length=50, null=True, blank=True)
    last_defender_spell = models.CharField(max_length=50, null=True, blank=True)
    last_attack_timestamp = models.DateTimeField(null=True, blank=True)

    current_turn = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="duel_turns")
    
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="duels_won")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Duel: {self.challenger.username} vs {self.opponent.username} ({self.status})"

class HousePoints(models.Model):
    house = models.CharField(max_length=20, choices=HOUSES, unique=True)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.house}: {self.points} points"

    class Meta:
        verbose_name = 'House Point'
        verbose_name_plural = 'House Points'

    