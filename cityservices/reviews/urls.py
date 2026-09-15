from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('add/<int:service_id>/', views.add_review, name='add_review'),
    path('provider/<int:provider_id>/', views.provider_reviews, name='provider_reviews'),
]