from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    FirebaseLoginView,
    ForgotPasswordResetView,
    ForgotPasswordSendOTPView,
    ForgotPasswordVerifyOTPView,
    MeView,
    RegisterView,
    SignupCompleteView,
    SignupSendOTPView,
    SignupVerifyOTPView,
    DebugGetOTPView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("signup/send-otp/", SignupSendOTPView.as_view(), name="signup-send-otp"),
    path("signup/verify-otp/", SignupVerifyOTPView.as_view(), name="signup-verify-otp"),
    path("signup/complete/", SignupCompleteView.as_view(), name="signup-complete"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("firebase-login/", FirebaseLoginView.as_view(), name="firebase-login"),
    path("forgot-password/send-otp/", ForgotPasswordSendOTPView.as_view(), name="forgot-password-send-otp"),
    path("forgot-password/verify-otp/", ForgotPasswordVerifyOTPView.as_view(), name="forgot-password-verify-otp"),
    path("forgot-password/reset/", ForgotPasswordResetView.as_view(), name="forgot-password-reset"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("debug/get-otp/<str:email>/", DebugGetOTPView.as_view(), name="debug-get-otp"),
]
