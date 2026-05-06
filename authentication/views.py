import logging
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

from .firebase import verify_firebase_token
from .models import OTPVerification
from .serializers import (
    EmailSerializer,
    FirebaseLoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    SignupCompleteSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    DEPRECATED: Use the OTP-verified signup flow instead:
    1. POST /api/auth/signup/send-otp/ - Send OTP to email
    2. POST /api/auth/signup/verify-otp/ - Verify OTP 
    3. POST /api/auth/signup/complete/ - Complete signup with username/password
    
    This endpoint is disabled to enforce OTP verification.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        return Response(
            {"detail": "Direct registration disabled. Use OTP-verified signup: /api/auth/signup/send-otp/"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class FirebaseLoginView(generics.GenericAPIView):
    serializer_class = FirebaseLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["id_token"]
        requested_provider = serializer.validated_data.get("provider")

        try:
            decoded = verify_firebase_token(token)
        except Exception as exc:
            return Response({"detail": f"Invalid Firebase token: {exc}"}, status=status.HTTP_400_BAD_REQUEST)

        firebase_provider = decoded.get("firebase", {}).get("sign_in_provider")
        if requested_provider and requested_provider != firebase_provider:
            return Response(
                {"detail": f"Provider mismatch. Token provider is {firebase_provider}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if firebase_provider not in ("google.com", "apple.com"):
            return Response({"detail": "Only Google and Apple login are supported."}, status=status.HTTP_400_BAD_REQUEST)

        email = decoded.get("email")
        if not email:
            return Response({"detail": "Email not found in Firebase token."}, status=status.HTTP_400_BAD_REQUEST)

        username_base = email.split("@")[0]
        username = username_base
        counter = 1
        while User.objects.filter(username=username).exclude(email=email).exists():
            counter += 1
            username = f"{username_base}{counter}"

        full_name = decoded.get("name", "")
        picture = decoded.get("picture", "")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "full_name": full_name,
                "avatar": picture,
                "is_verified": True,
            },
        )

        if not created:
            changed = False
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if picture and user.avatar != picture:
                user.avatar = picture
                changed = True
            if not user.is_verified:
                user.is_verified = True
                changed = True
            if changed:
                user.save(update_fields=["full_name", "avatar", "is_verified"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "provider": firebase_provider,
                "user": UserSerializer(user).data,
            }
        )


def _create_and_send_otp(email: str, purpose: str):
    otp = f"{random.randint(0, 99999):05d}"
    expires_at = timezone.now() + timedelta(minutes=10)
    OTPVerification.objects.filter(email=email, purpose=purpose, is_used=False).update(is_used=True)
    OTPVerification.objects.create(email=email, code=otp, purpose=purpose, expires_at=expires_at)

    try:
        from django.conf import settings
        logger.info(f"📧 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        logger.info(f"📧 EMAIL_HOST: {settings.EMAIL_HOST}")
        logger.info(f"📧 EMAIL_PORT: {settings.EMAIL_PORT}")
        logger.info(f"📧 EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"📧 EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        
        # Use the authenticated email as from_email if using SMTP with Gmail
        # Gmail doesn't allow sending from a different address
        from_email = settings.EMAIL_HOST_USER if "gmail" in settings.EMAIL_HOST else settings.DEFAULT_FROM_EMAIL
        
        sent = send_mail(
            subject="Break Free OTP Code",
            message=f"Your OTP code is {otp}. It will expire in 10 minutes.",
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info(f"✅ Email sent successfully to {email}. Messages sent: {sent}")
    except Exception as e:
        logger.error(f"❌ Failed to send OTP to {email} for {purpose}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    return otp


def _validate_otp(email: str, otp: str, purpose: str):
    otp_row = (
        OTPVerification.objects.filter(
            email=email,
            code=otp,
            purpose=purpose,
            is_used=False,
            expires_at__gte=timezone.now(),
        )
        .order_by("-created_at")
        .first()
    )
    return otp_row


class SignupSendOTPView(generics.GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"SignupSendOTP validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data["email"].lower().strip()
        
        if User.objects.filter(email=email).exists():
            logger.warning(f"Signup attempt with existing email: {email}")
            return Response({"detail": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        otp = _create_and_send_otp(email=email, purpose="signup")
        payload = {"detail": "OTP sent to email.", "otp_length": 5}
        
        # Always show OTP in development mode for easier testing
        from django.conf import settings
        if settings.DEBUG or request.query_params.get("debug") == "1":
            payload["otp_debug"] = otp
            logger.info(f"🔐 OTP for {email}: {otp}")
        
        logger.info(f"OTP sent to {email}")
        return Response(payload, status=status.HTTP_200_OK)


class SignupVerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_row = _validate_otp(
            email=serializer.validated_data["email"].lower().strip(),
            otp=serializer.validated_data["otp"],
            purpose="signup",
        )
        if not otp_row:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "OTP verified."}, status=status.HTTP_200_OK)


class SignupCompleteView(generics.GenericAPIView):
    serializer_class = SignupCompleteSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"SignupComplete validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        email = data["email"].lower().strip()

        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email already registered."}, status=status.HTTP_400_BAD_REQUEST)

        otp_row = _validate_otp(email=email, otp=data["otp"], purpose="signup")
        if not otp_row:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=data["username"]).exists():
            return Response({"detail": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            username=data["username"],
            email=email,
            full_name=data.get("full_name", ""),
            phone=data.get("phone", ""),
            is_verified=True,
        )
        user.set_password(data["password"])
        user.save()
        otp_row.is_used = True
        otp_row.save(update_fields=["is_used"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "detail": "Account created successfully.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ForgotPasswordSendOTPView(generics.GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"ForgotPasswordSendOTP validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data["email"].lower().strip()
        if not User.objects.filter(email=email).exists():
            logger.warning(f"Password reset attempt with non-existent email: {email}")
            return Response({"detail": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)

        otp = _create_and_send_otp(email=email, purpose="forgot_password")
        payload = {"detail": "OTP sent to email.", "otp_length": 5}
        
        # Always show OTP in development mode for easier testing
        from django.conf import settings
        if settings.DEBUG or request.query_params.get("debug") == "1":
            payload["otp_debug"] = otp
            logger.info(f"🔐 Password Reset OTP for {email}: {otp}")
        
        logger.info(f"Password reset OTP sent to {email}")
        return Response(payload, status=status.HTTP_200_OK)


class ForgotPasswordVerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_row = _validate_otp(
            email=serializer.validated_data["email"].lower().strip(),
            otp=serializer.validated_data["otp"],
            purpose="forgot_password",
        )
        if not otp_row:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "OTP verified."}, status=status.HTTP_200_OK)


class ForgotPasswordResetView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower().strip()
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        otp_row = _validate_otp(email=email, otp=otp, purpose="forgot_password")
        if not otp_row:
            return Response({"detail": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        otp_row.is_used = True
        otp_row.save(update_fields=["is_used"])

        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)


class DebugGetOTPView(generics.GenericAPIView):
    """
    Development-only endpoint to retrieve OTP codes.
    Returns the last valid OTP for an email.
    
    SECURITY: Remove this view in production!
    
    Usage: GET /api/auth/debug/get-otp/<email>/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, email: str, *args, **kwargs):
        from django.conf import settings
        
        if not settings.DEBUG:
            return Response(
                {"detail": "This endpoint is only available in development mode."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        email = email.lower().strip()
        otp_row = OTPVerification.objects.filter(
            email=email,
            is_used=False,
            expires_at__gte=timezone.now()
        ).order_by("-created_at").first()
        
        if not otp_row:
            return Response(
                {"detail": f"No valid OTP found for {email}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            "email": email,
            "otp": otp_row.code,
            "purpose": otp_row.purpose,
            "expires_at": otp_row.expires_at,
            "created_at": otp_row.created_at,
        })
