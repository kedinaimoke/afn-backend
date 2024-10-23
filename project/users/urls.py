from django.urls import path
from . import views
from .views import CheckRegisteredUsers

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('check_service_number/', views.CheckServiceNumberAPIView.as_view(), name='check-service-number'),
    path('check_official_name/', views.CheckOfficialNameView.as_view(), name='check-official-name'),
    path('check_phone_number/', views.CheckPhoneNumberView.as_view(), name='check-phone-number'),
    path('verify_phone_otp/', views.VerifyPhoneOTPView.as_view(), name='verify-phone-otp'),
    path('check_email/', views.CheckEmailView.as_view(), name='check-email'),
    path('verify_email_otp/', views.VerifyEmailOTPView.as_view(), name='verify-email-otp'),
    path('set_password/', views.SetPasswordView.as_view(), name='set-password'),
    path('request-password-reset/', views.RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('reset-password/<uidb36>/<token>/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/upload-picture/', views.UpdateProfilePictureView.as_view(), name='update-profile-picture'),
    path('personnel/', views.PersonnelListCreateView.as_view(), name='personnel-list-create'),
    path('personnel/<int:pk>/', views.PersonnelDetailView.as_view(), name='personnel-detail'),
    path('check-registered-users/', CheckRegisteredUsers.as_view(), name='check-registered-users'),
]
