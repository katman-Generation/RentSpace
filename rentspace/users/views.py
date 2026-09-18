import logging

from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from google.oauth2 import id_token
from google.auth.transport import requests

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    GoogleLoginSerializer,
)


User = get_user_model()

logger = logging.getLogger(__name__)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = UserProfileSerializer

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "register"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        if not serializer.is_valid():
            logger.info(
                "Register failed",
                extra={
                    "email": request.data.get("email"),
                    "errors": serializer.errors,
                },
            )

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        logger.info(
            "Register succeeded",
            extra={
                "email": user.email,
            },
        )

        return Response(
            {
                "user": serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"
    
class GoogleLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GoogleLoginSerializer
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        credential = serializer.validated_data[
            "credential"
        ]

        try:
            google_client_id = settings.GOOGLE_CLIENT_ID

            google_user = id_token.verify_oauth2_token(
                credential,
                requests.Request(),
                google_client_id,
            )

        except ValueError:
            return Response(
                {
                    "detail":
                    "Invalid Google authentication."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        google_id = google_user.get("sub")
        email = google_user.get("email")
        email_verified = google_user.get(
            "email_verified",
            False
        )

        first_name = google_user.get(
            "given_name",
            ""
        )

        last_name = google_user.get(
            "family_name",
            ""
        )

        if not google_id or not email:
            return Response(
                {
                    "detail":
                    "Google account information is incomplete."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not email_verified:
            return Response(
                {
                    "detail":
                    "Your Google email address must be verified."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(
            google_id=google_id
        ).first()

        if not user:
            user = User.objects.filter(
                email__iexact=email
            ).first()

        if user:
            if not user.google_id:
                user.google_id = google_id
                user.email_verified = True

                user.save(
                    update_fields=[
                        "google_id",
                        "email_verified",
                    ]
                )

        else:
            user = User.objects.create_user(
                email=email,
                password=None,
                first_name=first_name,
                last_name=last_name,
                phone_number=None,
            )

            user.google_id = google_id
            user.email_verified = True

            user.save(
                update_fields=[
                    "google_id",
                    "email_verified",
                ]
            )

        refresh = RefreshToken.for_user(user)

        logger.info(
            "Google login succeeded",
            extra={
                "email": user.email,
            },
        )

        return Response(
            {
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                },
                "access": str(
                    refresh.access_token
                ),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer
    throttle_scope = "password_reset"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = User.objects.filter(
            email__iexact=email,
            is_active=True,
        ).first()

        # Always return the same response.
        # This prevents email/account enumeration.
        if user:
            uid = urlsafe_base64_encode(
                force_bytes(user.pk)
            )

            token = default_token_generator.make_token(user)

            frontend_url = getattr(
                settings,
                "FRONTEND_URL",
                "http://localhost:5173",
            ).rstrip("/")

            reset_url = (
                f"{frontend_url}/reset-password/"
                f"{uid}/{token}"
            )

            send_mail(
                subject="Reset your RentSpace password",
                message=(
                    "You requested a password reset for your "
                    "RentSpace account.\n\n"
                    f"Reset your password here:\n{reset_url}\n\n"
                    "If you did not request this, you can safely "
                    "ignore this email."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            logger.info(
                "Password reset requested",
                extra={
                    "email": user.email,
                },
            )

        return Response(
            {
                "detail": (
                    "If an account exists with that email, "
                    "a password reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    throttle_scope = "password_reset"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        logger.info(
            "Password reset completed",
            extra={
                "email": serializer.validated_data["user"].email,
            },
        )

        return Response(
            {
                "detail": "Your password has been reset successfully."
            },
            status=status.HTTP_200_OK,
        )