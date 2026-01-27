from rest_framework import generics, permissions
from django.db.models import Q
from rest_framework.generics import RetrieveAPIView
from .models import Space, SpaceType, Location
from .serializers import SpaceSerializer, SpaceImageSerializer, LocationSerializer, SpaceTypeSerializer


class SpaceListView(generics.ListCreateAPIView):
    queryset = Space.objects.filter(is_available=True)
    serializer_class = SpaceSerializer
    
    def get_queryset(self):
        queryset = Space.objects.filter(is_available=True)
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(location__city__iexact=city)
        area = self.request.query_params.get('area')
        if area:
            queryset = queryset.filter(location__area__iexact=area)
        space_type = self.request.query_params.get('space_type')
        if space_type:
            queryset = queryset.filter(space_type__name__iexact=space_type)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__city__icontains=search) |
                Q(location__area__icontains=search)
            )

        return queryset
    
    
class SpaceCreateView(generics.CreateAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
class MySpacesView(generics.ListAPIView):
    serializer_class = SpaceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Space.objects.filter(owner=self.request.user)
    
class SpaceDetailView(RetrieveAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    
class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class SpaceTypeListView(generics.ListAPIView):
    queryset = SpaceType.objects.all()
    serializer_class = SpaceTypeSerializer

class SpaceUpdateView(generics.UpdateAPIView):
    serializer_class = SpaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Space.objects.filter(owner=self.request.user)