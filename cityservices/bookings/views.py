from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from accounts.notifications import notify
from services.models import Availability, Service
from .forms import BookingForm
from .models import Booking, Payment
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id, available=True)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking_date = form.cleaned_data['date']
            weekday = booking_date.weekday()
            time = booking_date.time()
            provider_slots = Availability.objects.filter(provider=service.provider, is_active=True)
            availability = provider_slots.filter(
                provider=service.provider, weekday=weekday, is_active=True,
                start_time__lte=time, end_time__gte=time,
            ).exists() if provider_slots.exists() else True
            already_booked = Booking.objects.filter(
                service=service, date=booking_date,
                status__in=['pending', 'confirmed', 'in_progress'],
            ).exists()
            if not availability:
                form.add_error('date', 'The provider is not available at this time.')
            elif already_booked:
                form.add_error('date', 'That time slot is already booked.')
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.service = service
                booking.save()
                Payment.objects.create(booking=booking, amount=service.price)
                notify(service.provider, f'New booking request for {service.name}.', 'booking', f'/bookings/provider/{booking.id}/')
                messages.success(request, 'Booking request sent successfully!')
                return redirect('bookings:my_bookings')
    else:
        form = BookingForm(initial={'full_name': request.user.get_full_name(), 'email': request.user.email})
    return render(request, 'bookings/book_service.html', {'service': service, 'form': form})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('service', 'service__provider')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def billing_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related('service').prefetch_related('payment')
    return render(request, 'bookings/billing_history.html', {'bookings': bookings})


@login_required
def provider_bookings(request):
    bookings = Booking.objects.filter(service__provider=request.user).select_related('service', 'user')
    return render(request, 'bookings/provider_bookings.html', {'bookings': bookings})


@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id, service__provider=request.user)
    allowed = {
        'pending': {'confirmed', 'cancelled'},
        'confirmed': {'in_progress', 'cancelled'},
        'in_progress': {'completed'},
    }
    if request.method == 'POST' and status in allowed.get(booking.status, set()):
        booking.status = status
        booking.save(update_fields=['status', 'updated_at'])
        notify(booking.user, f'Your booking for {booking.service.name} is now {status.replace("_", " ")}.', 'status', '/bookings/my/')
        messages.success(request, 'Booking status updated.')
    else:
        messages.error(request, 'That status transition is not allowed.')
    return redirect('bookings:provider_bookings')


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if request.method == 'POST' and booking.status in {'pending', 'confirmed'} and booking.date > timezone.now():
        booking.status = 'cancelled'
        booking.save(update_fields=['status', 'updated_at'])
        notify(booking.service.provider, f'A booking for {booking.service.name} was cancelled.', 'status', '/bookings/provider/')
        messages.success(request, 'Booking cancelled.')
    else:
        messages.error(request, 'This booking can no longer be cancelled.')
    return redirect('bookings:my_bookings')


@login_required
def create_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment, _ = Payment.objects.get_or_create(booking=booking, defaults={'amount': booking.service.price})
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        messages.info(request, 'Pay-after-service is enabled. No online payment is required.')
        return redirect('bookings:my_bookings')
    import razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({'amount': int(payment.amount * 100), 'currency': 'INR', 'receipt': f'booking-{booking.id}'})
    payment.gateway_transaction_id = order['id']
    payment.save(update_fields=['gateway_transaction_id', 'updated_at'])
    return JsonResponse({'order_id': order['id'], 'amount': order['amount'], 'key_id': settings.RAZORPAY_KEY_ID})


@csrf_exempt
def payment_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'POST required'}, status=405)
    import json
    payload = json.loads(request.body or '{}')
    order_id = payload.get('payload', {}).get('payment', {}).get('entity', {}).get('order_id')
    if order_id:
        payment = Payment.objects.filter(gateway_transaction_id=order_id).first()
        if payment:
            payment.status = 'paid'
            payment.save(update_fields=['status', 'updated_at'])
    return JsonResponse({'status': 'ok'})
