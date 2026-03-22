from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CUSTOMER = "customer"
    ROLE_VENDOR = "vendor"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_VENDOR, "Vendor"),
        (ROLE_ADMIN, "Admin"),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    def __str__(self):
        return self.username
