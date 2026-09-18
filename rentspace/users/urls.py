from django.urls import path
from .views import ProfileView, RegisterView, LoginView, RefreshView, PasswordResetConfirmView, PasswordResetRequestView, GoogleLoginView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
    path('google-login/', GoogleLoginView.as_view(), name='google-login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('profile/', ProfileView.as_view()),
]
