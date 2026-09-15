from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.account_settings, name='account_settings'),
    path('privacy/', views.privacy_security, name='privacy_security'),
    path('dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
    path('notifications/', views.notifications, name='notifications'),
]