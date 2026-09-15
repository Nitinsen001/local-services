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

def cleanup_services():
    print("Cleaning up services...")

    try:
        # 1. Remove duplicate services (keep only one instance of each unique service per provider)
        print("\n1. Removing duplicate services...")

        # Get all providers
        providers = User.objects.filter(service__available=True).distinct()

        for provider in providers:
            provider_services = Service.objects.filter(provider=provider, available=True)
            seen_services = {}

            for service in provider_services:
                # Create a unique key based on service name and category
                key = f"{service.name}_{service.category.name}"

                if key in seen_services:
                    # Duplicate found - delete this one
                    print(f"  Deleting duplicate: {service.name} by {provider.username}")
                    service.delete()
                else:
                    seen_services[key] = service

        # 2. Update inappropriate service names and descriptions
        print("\n2. Updating service names and descriptions...")

        # Update the 'chinu' service to have a proper name
        chinu_service = Service.objects.filter(name='chinu', provider__username='chinu_kamvali_01').first()
        if chinu_service:
            chinu_service.name = 'Professional Cleaning Service'
            chinu_service.description = 'Complete home and office cleaning services with professional staff. Thorough cleaning including all areas and appliances.'
            chinu_service.price = Decimal('150.00')
            chinu_service.location = 'Maheshwar and surrounding areas'
            chinu_service.save()
            print(f"  Updated chinu service to: {chinu_service.name}")

        # 3. Show final results
        print("\n3. Final service count:")
        total_services = Service.objects.filter(available=True).count()
        print(f"Total available services: {total_services}")

        print("\nServices by Provider:")
        for provider in User.objects.filter(service__available=True).distinct():
            service_count = provider.service_set.filter(available=True).count()
            print(f"- {provider.username}: {service_count} services")
            for service in provider.service_set.filter(available=True):
                print(f"  • {service.name} ({service.category.name}) - ${service.price}")

        print("\nCleanup completed successfully!")

    except Exception as e:
        print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_services()