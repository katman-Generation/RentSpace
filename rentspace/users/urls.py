from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import ProfileView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', ProfileView.as_view()),
]