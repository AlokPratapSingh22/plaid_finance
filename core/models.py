from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extension of default User class"""
    email = models.EmailField(unique=True)
