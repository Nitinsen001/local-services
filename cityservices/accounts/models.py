from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    # Service categories for providers
    SERVICE_CATEGORIES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('cleaning', 'Cleaning'),
        ('painting', 'Painting'),
        ('carpentry', 'Carpentry'),
        ('gardening', 'Gardening'),
        ('beauty', 'Beauty & Wellness'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(blank=True)
    is_provider = models.BooleanField(default=False)
    rating = models.FloatField(default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=100, blank=True)

    # Provider-specific fields
    service_category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    service_area = models.CharField(max_length=100, blank=True)
    service_description = models.TextField(blank=True)
    experience = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.email}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('booking', 'Booking'),
        ('status', 'Booking Status'),
        ('review', 'Review'),
        ('message', 'Message'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
