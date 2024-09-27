from django.urls import path
from . import views

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
]
