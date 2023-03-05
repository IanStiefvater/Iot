from django.db import models


# Create your models here.
class user (models.Model):
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=200)
