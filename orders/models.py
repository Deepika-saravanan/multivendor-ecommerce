from django.db import models

# Create your models here.
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
]

status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')