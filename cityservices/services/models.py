from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    # Used when a category has no icon stored in the database, so the UI never
    # renders an empty icon placeholder.
    ICON_FALLBACKS = {
        'plumbing': 'fas fa-wrench',
        'electrical': 'fas fa-bolt',
        'cleaning': 'fas fa-broom',
        'painting': 'fas fa-paint-roller',
        'carpentry': 'fas fa-hammer',
        'gardening': 'fas fa-seedling',
        'beauty': 'fas fa-spa',
        'beauty & wellness': 'fas fa-spa',
        'moving': 'fas fa-truck',
        'appliance repair': 'fas fa-plug',
        'other': 'fas fa-tools',
    }

    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="FontAwesome icon class (e.g., fas fa-wrench)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def icon_class(self):
        """Return the saved FontAwesome class, or a sensible icon based on the name."""
        if self.icon:
            return self.icon
        return self.ICON_FALLBACKS.get(self.name.strip().lower(), 'fas fa-tools')

    class Meta:
        verbose_name_plural = "Categories"

class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    featured = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    @property
    def review_count(self):
        return self.review_set.count()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_services')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'service'], name='unique_favorite_per_user_service'),
        ]
        ordering = ['-created_at']


class Availability(models.Model):
    WEEKDAYS = [(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])]

    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['provider', 'weekday', 'start_time', 'end_time'], name='unique_provider_availability'),
        ]
