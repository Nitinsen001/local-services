from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('billing/', views.billing_history, name='billing_history'),
    path('provider/', views.provider_bookings, name='provider_bookings'),
    path('provider/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('<int:booking_id>/payment/', views.create_payment, name='create_payment'),
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
]