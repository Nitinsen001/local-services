from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Profile

from .models import Category, Favorite, Service


class ServiceFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('customer', password='pass12345')
        Profile.objects.create(user=self.user)
        provider = User.objects.create_user('provider', password='pass12345')
        Profile.objects.create(user=provider, is_provider=True, service_area='Delhi')
        category = Category.objects.create(name='Plumbing', icon='fas fa-wrench')
        self.service = Service.objects.create(
            name='Emergency pipe repair', description='Fast plumbing', price=100,
            category=category, provider=provider, location='Delhi',
        )

    def test_search_finds_service_by_location(self):
        response = self.client.get(reverse('services:service_list'), {'q': 'Delhi'}, follow=True)
        self.assertContains(response, 'Emergency pipe repair')

    def test_category_filter_accepts_category_name(self):
        response = self.client.get(reverse('services:service_list'), {'category': 'plumbing'}, follow=True)
        self.assertContains(response, 'Emergency pipe repair')

    def test_favorite_toggle_is_unique_and_removable(self):
        self.client.force_login(self.user)
        url = reverse('services:toggle_favorite', args=[self.service.id])
        self.client.post(url, follow=True)
        self.assertEqual(Favorite.objects.filter(user=self.user, service=self.service).count(), 1)
        self.client.post(url, follow=True)
        self.assertFalse(Favorite.objects.filter(user=self.user, service=self.service).exists())