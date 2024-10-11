from django.urls import path
from . import views
from .views import register, login, check_registered_users

urlpatterns = [
    path('check_service_number/', views.check_service_number, name='check_service_number'),
    path('check_official_name/', views.check_official_name, name='check_official_name'),
    path('check_phone_number/', views.check_phone_number, name='check_phone_number'),
    path('verify_phone_otp/', views.verify_phone_otp, name='verify_phone_otp'),
    path('check_email/', views.check_email, name='check_email'),
    path('verify_email_otp/', views.verify_email_otp, name='verify_email_otp'),
    path('set_password/', views.set_password, name='set_password'),
    path('request-password-reset/', views.request_password_reset, name='request_password_reset'),
    path('reset-password/<uidb36>/<token>/', views.reset_password, name='reset_password'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/upload-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('personnel/', views.PersonnelListCreateView.as_view(), name='personnel-list-create'),
    path('personnel/<int:pk>/', views.PersonnelDetailView.as_view(), name='personnel-detail'),
    path('check_registered_users/', check_registered_users, name='check_registered_users'),
]
