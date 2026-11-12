from django.db import models
from django.conf import settings

class Household(models.Model):
    name = models.CharField(max_length=255, default="Mi Hogar")
    admin = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='household')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Member(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)
    relation = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
