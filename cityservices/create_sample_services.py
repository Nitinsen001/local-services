#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cityservices.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from services.models import Service, Category

def create_sample_services():
    print("Creating sample services for service providers...")

    try:
        # Get users
        aakash = User.objects.get(username='Aakash_bhai_01')
        aryan = User.objects.get(username='aryan_002')
        print(f"Found users: {aakash.username}, {aryan.username}")

        # Get categories
        electrical_cat = Category.objects.get(id=2)  # Electrical
        painting_cat = Category.objects.get(id=4)    # Painting
        gardening_cat = Category.objects.get(id=6)   # Gardening

        print("Found categories successfully")

        # Create services for Aakash_bhai_01
        service1 = Service.objects.create(
            name='Professional Electrical Wiring',
            description='Complete electrical wiring services for residential and commercial properties. Safe and certified electrical installations with 2-year warranty.',
            price=Decimal('75.00'),
            category=electrical_cat,
            provider=aakash,
            location='Downtown Area',
            available=True
        )
        print(f"Created service for Aakash: {service1.name}")

        service2 = Service.objects.create(
            name='House Painting Services',
            description='Interior and exterior painting with premium quality paints. Professional finish guaranteed. Free color consultation included.',
            price=Decimal('45.00'),
            category=painting_cat,
            provider=aakash,
            location='City Center',
            available=True
        )
        print(f"Created service for Aakash: {service2.name}")

        # Create service for aryan_002
        service3 = Service.objects.create(
            name='Garden Design & Maintenance',
            description='Complete garden design, landscaping and regular maintenance services. Transform your outdoor space with beautiful, sustainable gardens.',
            price=Decimal('55.00'),
            category=gardening_cat,
            provider=aryan,
            location='Suburban Area',
            available=True
        )
        print(f"Created service for Aryan: {service3.name}")

        print("\nAll sample services created successfully!")

        # Show final count
        total_services = Service.objects.filter(available=True).count()
        print(f"Total available services: {total_services}")

        # Show services by provider
        print("\nServices by Provider:")
        for provider in User.objects.filter(service__available=True).distinct():
            service_count = provider.service_set.filter(available=True).count()
            print(f"- {provider.username}: {service_count} services")

    except User.DoesNotExist as e:
        print(f"Error: User not found - {e}")
    except Category.DoesNotExist as e:
        print(f"Error: Category not found - {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_sample_services()