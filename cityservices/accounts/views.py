from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .forms import RegisterForm, LoginForm, AccountSettingsForm
from .models import Notification, Profile
from services.models import Service
from bookings.models import Booking

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Get user type from form
            user_type = form.cleaned_data.get('user_type')
            is_provider = (user_type == 'provider')

            # Get provider-specific data
            service_category = form.cleaned_data.get('service_category') if is_provider else ''
            hourly_rate = form.cleaned_data.get('hourly_rate') if is_provider else None
            service_area = form.cleaned_data.get('service_area') if is_provider else ''
            service_description = form.cleaned_data.get('service_description') if is_provider else ''
            experience = form.cleaned_data.get('experience') if is_provider else ''

            # Create profile with appropriate provider status and data
            Profile.objects.create(
                user=user,
                is_provider=is_provider,
                service_category=service_category,
                hourly_rate=hourly_rate,
                service_area=service_area,
                service_description=service_description,
                experience=experience
            )

            login(request, user)
            messages.success(request, 'Registration successful!')

            # Redirect based on user type
            if is_provider:
                return redirect('accounts:provider_dashboard')
            else:
                return redirect('accounts:user_dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')
                # Check if user is a provider and redirect accordingly
                try:
                    profile = user.profile
                    if profile.is_provider:
                        return redirect('accounts:provider_dashboard')
                    else:
                        return redirect('accounts:user_dashboard')
                except Profile.DoesNotExist:
                    # If no profile exists, treat as regular user
                    return redirect('accounts:user_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


@login_required
def account_settings(request):
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account settings updated.')
            return redirect('accounts:account_settings')
    else:
        form = AccountSettingsForm(instance=request.user)
    return render(request, 'accounts/account_settings.html', {'form': form})


@login_required
def privacy_security(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:privacy_security')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/privacy_security.html', {'form': form})

@login_required
def provider_dashboard(request):
    # Check if user is a provider
    try:
        profile = request.user.profile
        if not profile.is_provider:
            messages.error(request, 'Access denied. Provider account required.')
            return redirect('home')
    except Profile.DoesNotExist:
        messages.error(request, 'Please complete your profile setup first.')
        return redirect('profile')

    # Get dashboard statistics
    total_bookings = Booking.objects.filter(service__provider=request.user).count()
    active_services_count = Service.objects.filter(provider=request.user, available=True).count()

    # Calculate total earnings (sum of all completed bookings)
    completed_bookings = Booking.objects.filter(
        service__provider=request.user,
        status='completed'
    ).select_related('service')

    total_earnings = sum(booking.service.price for booking in completed_bookings)

    # Get user rating from profile
    user_rating = profile.rating if profile.rating > 0 else 4.8  # Default rating if not set

    # Get recent services (last 4)
    recent_services = Service.objects.filter(provider=request.user)[:4]

    # Get recent bookings (last 5)
    recent_bookings = Booking.objects.filter(service__provider=request.user).select_related('user', 'service')[:5]

    context = {
        'total_bookings': total_bookings,
        'total_earnings': total_earnings,
        'user_rating': user_rating,
        'active_services_count': active_services_count,
        'recent_services': recent_services,
        'recent_bookings': recent_bookings,
    }

    return render(request, 'accounts/provider_dashboard.html', context)

@login_required
def user_dashboard(request):
    # Check if user is NOT a provider (i.e., a regular user)
    try:
        profile = request.user.profile
        if profile.is_provider:
            messages.error(request, 'Access denied. User account required.')
            return redirect('accounts:provider_dashboard')
    except Profile.DoesNotExist:
        # If no profile exists, treat as regular user
        pass

    # Get dashboard statistics for user
    active_bookings_count = Booking.objects.filter(user=request.user, status__in=['pending', 'confirmed', 'in_progress']).count()
    completed_bookings_count = Booking.objects.filter(user=request.user, status='completed').count()

    # Calculate total spent (sum of all completed bookings)
    completed_bookings = Booking.objects.filter(user=request.user, status='completed').select_related('service')
    total_spent = sum(booking.service.price for booking in completed_bookings)

    # For now, set favorite providers count to 0 (can be implemented later with a favorite system)
    favorite_providers_count = request.user.favorite_services.count()

    # Get recent bookings (last 5)
    recent_bookings = Booking.objects.filter(user=request.user).select_related('service__provider')[:5]

    # Count pending bookings for notification badge
    pending_bookings_count = Booking.objects.filter(user=request.user, status='pending').count()

    context = {
        'active_bookings_count': active_bookings_count,
        'completed_bookings_count': completed_bookings_count,
        'total_spent': total_spent,
        'favorite_providers_count': favorite_providers_count,
        'recent_bookings': recent_bookings,
        'pending_bookings_count': pending_bookings_count,
    }

    return render(request, 'accounts/user_dashboard.html', context)


@login_required
def notifications(request):
    items = request.user.notifications.all()
    items.filter(is_read=False).update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': items})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')
