from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Profile
from services.models import Category, Service

from .forms import BookingForm
from .models import Booking


class BookingWorkflowTests(TestCase):
    def setUp(self):
        self.provider = User.objects.create_user('provider', password='pass12345')
        Profile.objects.create(user=self.provider, is_provider=True)
        self.customer = User.objects.create_user('customer', password='pass12345')
        Profile.objects.create(user=self.customer)
        category = Category.objects.create(name='Plumbing', icon='fas fa-wrench')
        self.service = Service.objects.create(
            name='Pipe repair', description='Repair', price=500,
            category=category, provider=self.provider, location='Delhi',
        )

    def test_booking_form_rejects_past_date(self):
        data = {
            'full_name': 'Customer', 'email': 'customer@example.com', 'phone': '123',
            'address': 'Home', 'date': (timezone.localdate() - timedelta(days=1)).isoformat(),
            'time': '10:00', 'notes': '',
        }
        self.assertFalse(BookingForm(data).is_valid())

    def test_provider_cannot_update_another_providers_booking(self):
        booking = Booking.objects.create(
            user=self.customer, service=self.service,
            date=timezone.now() + timedelta(days=1),
        )
        other = User.objects.create_user('other', password='pass12345')
        Profile.objects.create(user=other, is_provider=True)
        self.client.force_login(other)
        response = self.client.post(reverse('bookings:update_booking_status', args=[booking.id, 'confirmed']), follow=True)
        booking.refresh_from_db()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(booking.status, 'pending')
