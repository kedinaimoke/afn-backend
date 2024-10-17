from django.urls import path
from . import views
from .views import register, login, CheckRegisteredUsers

urlpatterns = [
    path('check_service_number/', views.CheckServiceNumberAPIView.as_view(), name='check_service_number'),
    path('check_official_name/', views.CheckOfficialNameView.as_view(), name='check_official_name'),
    path('check_phone_number/', views.CheckPhoneNumberView.as_view(), name='check_phone_number'),
    path('verify_phone_otp/', views.VerifyPhoneOTPView.as_view(), name='verify_phone_otp'),
    path('check_email/', views.CheckEmailView.as_view(), name='check_email'),
    path('verify_email_otp/', views.VerifyEmailOTPView.as_view(), name='verify_email_otp'),
    path('set_password/', views.SetPasswordView.as_view(), name='set_password'),
    path('request-password-reset/', views.RequestPasswordResetView.as_view(), name='request_password_reset'),
    path('reset-password/<uidb36>/<token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('api/register/', register, name='register'),
    path('api/login/', login, name='login'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/upload-picture/', views.update_profile_picture, name='update_profile_picture'),
    path('personnel/', views.PersonnelListCreateView.as_view(), name='personnel-list-create'),
    path('personnel/<int:pk>/', views.PersonnelDetailView.as_view(), name='personnel-detail'),
    path('check-registered-users/', CheckRegisteredUsers.as_view(), name='check-registered-users'),
]
