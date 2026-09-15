from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('add/', views.add_service, name='add_service'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('<int:service_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('availability/', views.manage_availability, name='availability'),
]