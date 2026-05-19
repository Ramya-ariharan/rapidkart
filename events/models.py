from django.db import models
from django.conf import settings  # ← this
from products.models import Product

class UserEvent(models.Model):
    EVENT_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('purchase', 'Purchase'),
        ('search', 'Search'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ← instead of User
        on_delete=models.CASCADE
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    search_query = models.CharField(max_length=255, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'event_type']),
            models.Index(fields=['product', 'event_type']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.event_type} - {self.timestamp}"