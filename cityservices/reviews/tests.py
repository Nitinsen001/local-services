from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from bookings.models import Booking
from services.models import Category, Service

from .models import Review


class ReviewWorkflowTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user('provider', password='pass12345')
        self.profile = Profile.objects.create(user=self.provider, is_provider=True)
        self.customer = User.objects.create_user('customer', password='pass12345')
        category = Category.objects.create(name='Cleaning', icon='fas fa-broom')
        self.service = Service.objects.create(
            name='Home cleaning', description='Cleaning', price=300,
            category=category, provider=self.provider,
        )
        Booking.objects.create(
            user=self.customer, service=self.service,
            date=timezone.now() + timedelta(days=1), status='completed',
        )

    def test_review_recalculates_provider_rating(self):
        self.client.force_login(self.customer)
        response = self.client.post(reverse('reviews:add_review', args=[self.service.id]), {'rating': '5', 'comment': 'Great'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.rating, 5)

        self.assertEqual(Review.objects.filter(service=self.service).count(), 1)
