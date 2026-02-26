from django.urls import path
from .views import ProfileView, RegisterView, LoginView, RefreshView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', RefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view()),
]
