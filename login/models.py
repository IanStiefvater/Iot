from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, password=None):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, apellido=apellido)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, apellido, password=None):
        user = self.create_user(email, nombre, apellido, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class usuarios(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    type = models.CharField(max_length=250)
    token = models.CharField(max_length=250, default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre", "apellido"]


class delete_notes(models.Model):
    line = models.CharField(max_length=255)
    note = models.CharField(max_length=255)


class log_users(models.Model):
    id_user = models.ForeignKey(usuarios, on_delete=models.CASCADE, null=True)
    entry = models.DateTimeField()
    exit = models.DateTimeField(null=True)
