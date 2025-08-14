from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modelo de usuário customizado para suportar diferentes tipos de usuários.
    """
    class UserType(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        PROFISSIONAL = "PROFISSIONAL", "Profissional"

    # O email será usado para login
    email = models.EmailField("e-mail", unique=True)
    user_type = models.CharField("tipo de usuário", max_length=12, choices=UserType.choices, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]
