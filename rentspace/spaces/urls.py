from django.urls import path
from .views import SpaceListView, SpaceCreateView, MySpacesView, SpaceDetailView, SpaceTypeListView, LocationListView, SpaceUpdateView

urlpatterns = [
    path('', SpaceListView.as_view(), name='space-list'),
    path('<int:pk>/', SpaceDetailView.as_view(), name='space-detail'),
    path('create/', SpaceCreateView.as_view()),
    path('update/<int:pk>/', SpaceUpdateView.as_view(), name='space-update'),
    path('my-spaces/', MySpacesView.as_view()),
    path("locations/", LocationListView.as_view()),
    path("space-types/", SpaceTypeListView.as_view()),
]
