from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Profile


class RegistrationTests(TestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse('accounts:register'), SERVER_NAME='localhost')
        self.assertEqual(response.status_code, 200)

    def test_customer_can_register_without_provider_fields(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'customer_one',
                'email': 'customer@example.com',
                'user_type': 'user',
                'password1': 'Strong!Customer2026',
                'password2': 'Strong!Customer2026',
            },
            SERVER_NAME='localhost',
        )
        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(user__username='customer_one')
        self.assertFalse(profile.is_provider)


class DashboardNavigationTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user('nav_customer', password='Strong!Customer2026')
        Profile.objects.create(user=self.customer)
        self.provider = User.objects.create_user('nav_provider', password='Strong!Provider2026')
        Profile.objects.create(user=self.provider, is_provider=True)

    def test_customer_dashboard_destinations_load(self):
        self.client.force_login(self.customer)
        routes = [
            'accounts:user_dashboard', 'bookings:my_bookings', 'services:service_list',
            'accounts:notifications', 'services:favorite_list', 'accounts:profile', 'home',
        ]
        for route in routes:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)

    def test_provider_dashboard_destinations_load(self):
        self.client.force_login(self.provider)
        routes = [
            'accounts:provider_dashboard', 'services:service_list', 'services:add_service',
            'bookings:provider_bookings', 'services:availability', 'accounts:notifications',
            'accounts:profile', 'home',
        ]
        for route in routes:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route)).status_code, 200)

    def test_customer_navbar_does_not_cancel_real_links(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('accounts:user_dashboard'))
        content = response.content.decode()
        self.assertNotIn('e.preventDefault()', content)
        self.assertIn(reverse('bookings:my_bookings'), content)
        self.assertNotIn('window.location.hrbookings', content)
        self.assertIn("window.location.href='" + reverse('bookings:my_bookings') + "'", content)

    def test_profile_sidebar_pages_and_forms_work(self):
        self.client.force_login(self.customer)
        profile_page = self.client.get(reverse('accounts:profile'))
        profile_html = profile_page.content.decode()
        self.assertNotIn('e.preventDefault()', profile_html)
        self.assertNotIn('Avatar upload feature would open here', profile_html)
        self.assertIn(reverse('accounts:account_settings'), profile_html)
        self.assertEqual(self.client.get(reverse('accounts:account_settings')).status_code, 200)
        self.assertEqual(self.client.get(reverse('accounts:privacy_security')).status_code, 200)
        self.assertEqual(self.client.get(reverse('bookings:billing_history')).status_code, 200)

        settings_response = self.client.post(reverse('accounts:account_settings'), {
            'username': 'nav_customer_updated',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Customer',
        })
        self.assertEqual(settings_response.status_code, 302)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.email, 'updated@example.com')

        password_response = self.client.post(reverse('accounts:privacy_security'), {
            'old_password': 'Strong!Customer2026',
            'new_password1': 'New!CustomerPassword2026',
            'new_password2': 'New!CustomerPassword2026',
        })
        self.assertEqual(password_response.status_code, 302)
        self.assertTrue(self.client.login(username='nav_customer_updated', password='New!CustomerPassword2026'))