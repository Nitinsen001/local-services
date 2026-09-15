from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from services.models import Service
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from accounts.notifications import notify

@login_required
def add_review(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    # Check if user has booked this service
    has_booked = service.booking_set.filter(user=request.user, status='completed').exists()
    if not has_booked:
        messages.error(request, 'You can only review services you have completed bookings for.')
        return redirect('services:service_detail', pk=service_id)

    # Check if review already exists
    existing_review = Review.objects.filter(user=request.user, service=service).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this service.')
        return redirect('services:service_detail', pk=service_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            review = Review.objects.create(
                user=request.user,
                service=service,
                rating=int(rating),
                comment=comment
            )
            summary = Review.objects.filter(service__provider=service.provider).aggregate(average=Avg('rating'), count=Count('id'))
            service.provider.profile.rating = summary['average'] or 0
            service.provider.profile.review_count = summary['count'] or 0
            service.provider.profile.save(update_fields=['rating', 'review_count'])
            notify(service.provider, f'New review received for {service.name}.', 'review', f'/reviews/provider/{service.provider_id}/')
            messages.success(request, 'Review added successfully!')
            return redirect('services:service_detail', pk=service_id)
        else:
            messages.error(request, 'Please provide both rating and comment.')

    return render(request, 'reviews/add_review.html', {'service': service})

def provider_reviews(request, provider_id):
    provider = get_object_or_404(User, pk=provider_id)
    reviews = Review.objects.filter(service__provider=provider).select_related('service', 'user')
    summary = reviews.aggregate(average=Avg('rating'), total=Count('id'))
    total = summary['total'] or 0
    positive = reviews.filter(rating__gte=4).count() if total else 0

    # Rating distribution for the 5 -> 1 star breakdown, computed from real data.
    distribution = []
    for stars in range(5, 0, -1):
        count = reviews.filter(rating=stars).count() if total else 0
        distribution.append({
            'stars': stars,
            'count': count,
            'percent': round(count * 100 / total) if total else 0,
        })

    return render(request, 'reviews/provider_reviews.html', {
        'reviews': reviews,
        'provider': provider,
        'total_reviews': total,
        'average_rating': round(summary['average'] or 0, 1),
        'distribution': distribution,
        'positive_percent': round(positive * 100 / total) if total else 0,
    })
