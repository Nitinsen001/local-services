from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import models
from services.models import Service, Category
from accounts.models import Profile, Contact
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import ContactForm

def home(request):
    query = request.GET.get('q', '').strip()
    selected_filter = request.GET.get('filter', '')
    featured_services = Service.objects.filter(
        featured=True, available=True
    ).select_related('category', 'provider__profile')
    if query:
        featured_services = featured_services.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query) | Q(provider__profile__service_area__icontains=query))
    if selected_filter == 'new':
        featured_services = featured_services.order_by('-created_at')
    elif selected_filter == 'top_rated':
        featured_services = featured_services.order_by('-provider__profile__rating')
    else:
        featured_services = featured_services.order_by('-created_at')
    featured_services = featured_services[:4]
    categories = Category.objects.annotate(
        service_count=models.Count('service', filter=Q(service__available=True))
    )
    # Only get providers who actually have services and have complete profile information
    top_providers = User.objects.filter(
        profile__is_provider=True,
        service__available=True
    ).annotate(
        service_count=models.Count('service'),
        min_price=models.Min('service__price', filter=Q(service__available=True)),
    ).filter(
        service_count__gt=0
    ).distinct().order_by('-profile__rating')[:4]

    average_rating = Profile.objects.filter(is_provider=True).aggregate(
        avg=models.Avg('rating')
    )['avg'] or 0

    return render(request, 'home.html', {
        'featured_services': featured_services,
        'categories': categories,
        'top_providers': top_providers,
        'query': query,
        'selected_filter': selected_filter,
        'total_services': Service.objects.filter(available=True).count(),
        'total_providers': Profile.objects.filter(is_provider=True).count(),
        'total_categories': categories.count(),
        'average_rating': round(average_rating, 1),
    })

def about(request):
    categories = Category.objects.annotate(
        service_count=models.Count('service', filter=Q(service__available=True))
    )
    average_rating = Profile.objects.filter(is_provider=True).aggregate(
        avg=models.Avg('rating')
    )['avg'] or 0

    return render(request, 'about.html', {
        'total_services': Service.objects.filter(available=True).count(),
        'total_providers': Profile.objects.filter(is_provider=True).count(),
        'total_categories': categories.count(),
        'average_rating': round(average_rating, 1),
    })

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})