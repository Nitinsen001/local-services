from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Availability, Favorite, Service, Category
from .forms import AddServiceForm, AvailabilityForm

def service_list(request):
    services = Service.objects.filter(available=True).select_related('category', 'provider__profile')
    categories = Category.objects.all()
    category_filter = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    selected_filter = request.GET.get('filter', '')
    if category_filter:
        category_filter = category_filter.strip()
        if category_filter.isdigit():
            services = services.filter(category_id=int(category_filter))
        else:
            category_name = category_filter.replace('-', ' ')
            services = services.filter(category__name__iexact=category_name)
    if query:
        services = services.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query) | Q(provider__profile__service_area__icontains=query))
    if request.GET.get('provider'):
        services = services.filter(provider_id=request.GET['provider'])
    if selected_filter == 'top_rated':
        services = services.order_by('-provider__profile__rating', '-created_at')
    elif selected_filter == 'near_me' and query:
        services = services.filter(Q(location__icontains=query) | Q(provider__profile__service_area__icontains=query))
    elif selected_filter == 'new':
        services = services.order_by('-created_at')
    else:
        services = services.order_by('-created_at')

    page_obj = Paginator(services, 12).get_page(request.GET.get('page'))

    return render(request, 'services/service_list.html', {
        'services': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_filter,
        'query': query,
        'selected_filter': selected_filter,
    })

def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk, available=True)
    reviews = service.review_set.all().order_by('-created_at')

    # Check if user can review this service
    user_can_review = False
    user_has_reviewed = False
    has_completed_booking = False

    if request.user.is_authenticated and request.user != service.provider:
        # Check if user has completed bookings for this service
        has_completed_booking = service.booking_set.filter(
            user=request.user,
            status='completed'
        ).exists()

        # Check if user has already reviewed this service
        user_has_reviewed = service.review_set.filter(user=request.user).exists()

        # User can review if they have completed booking but haven't reviewed yet
        user_can_review = has_completed_booking and not user_has_reviewed

    return render(request, 'services/service_detail.html', {
        'service': service,
        'reviews': reviews,
        'user_can_review': user_can_review,
        'user_has_reviewed': user_has_reviewed,
        'has_completed_booking': has_completed_booking
    })

@login_required
def add_service(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_provider:
        messages.error(request, 'You need to be a service provider to add services.')
        return redirect('home')

    if request.method == 'POST':
        form = AddServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            messages.success(request, 'Service added successfully!')
            return redirect('services:service_list')
    else:
        form = AddServiceForm()
    return render(request, 'services/add_service.html', {'form': form})


@login_required
def toggle_favorite(request, service_id):
    service = get_object_or_404(Service, pk=service_id, available=True)
    if request.method == 'POST':
        favorite, created = Favorite.objects.get_or_create(user=request.user, service=service)
        if not created:
            favorite.delete()
            messages.info(request, 'Service removed from favorites.')
        else:
            messages.success(request, 'Service added to favorites.')
    return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or 'services:service_list')


@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('service', 'service__provider')
    return render(request, 'services/favorite_list.html', {'favorites': favorites})


@login_required
def manage_availability(request):
    if not getattr(getattr(request.user, 'profile', None), 'is_provider', False):
        messages.error(request, 'Provider account required.')
        return redirect('home')
    if request.method == 'POST':
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.provider = request.user
            slot.save()
            messages.success(request, 'Availability slot added.')
            return redirect('services:availability')
    else:
        form = AvailabilityForm()
    slots = Availability.objects.filter(provider=request.user)
    return render(request, 'services/availability.html', {'form': form, 'slots': slots})
