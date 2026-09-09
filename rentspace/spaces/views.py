from django.db.models import Q

from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import (
    Space,
    Category,
    SpaceType,
    Amenity,
    Location,
)

from .serializers import (
    SpaceSerializer,
    CategorySerializer,
    SpaceTypeSerializer,
    AmenitySerializer,
    LocationSerializer,
)


class SpaceListView(generics.ListAPIView):
    queryset = Space.objects.filter(is_available=True)
    serializer_class = SpaceSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "search"

    def get_queryset(self):
        queryset = Space.objects.filter(
            is_available=True
        ).select_related(
            "owner",
            "category",
            "space_type",
            "location",
        ).prefetch_related(
            "amenities",
            "images",
        )

        city = self.request.query_params.get("city")
        if city:
            queryset = queryset.filter(
                location__city__iexact=city
            )

        area = self.request.query_params.get("area")
        if area:
            queryset = queryset.filter(
                location__area__iexact=area
            )

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(
                category__name__iexact=category
            )

        space_type = self.request.query_params.get("space_type")
        if space_type:
            queryset = queryset.filter(
                space_type__name__iexact=space_type
            )

        rental_period = self.request.query_params.get(
            "rental_period"
        )
        if rental_period:
            queryset = queryset.filter(
                rental_period=rental_period
            )

        min_price = self.request.query_params.get(
            "min_price"
        )
        max_price = self.request.query_params.get(
            "max_price"
        )

        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        bedrooms = self.request.query_params.get(
            "bedrooms"
        )
        if bedrooms:
            queryset = queryset.filter(
                bedrooms__gte=bedrooms
            )

        bathrooms = self.request.query_params.get(
            "bathrooms"
        )
        if bathrooms:
            queryset = queryset.filter(
                bathrooms__gte=bathrooms
            )

        furnished = self.request.query_params.get(
            "furnished"
        )
        if furnished is not None:
            queryset = queryset.filter(
                furnished=furnished
            )

        search = self.request.query_params.get(
            "search"
        )

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__city__icontains=search) |
                Q(location__area__icontains=search) |
                Q(category__name__icontains=search) |
                Q(space_type__name__icontains=search)
            )

        return queryset


class SpaceCreateView(generics.CreateAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "write"

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user
        )


class MySpacesView(generics.ListAPIView):
    serializer_class = SpaceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Space.objects.filter(
            owner=self.request.user
        ).select_related(
            "category",
            "space_type",
            "location",
        ).prefetch_related(
            "amenities",
            "images",
        )


class SpaceDetailView(RetrieveAPIView):
    queryset = Space.objects.all().select_related(
        "owner",
        "category",
        "space_type",
        "location",
    ).prefetch_related(
        "amenities",
        "images",
    )

    serializer_class = SpaceSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "detail"

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["include_owner_phone"] = True

        return context


class SpaceUpdateView(generics.UpdateAPIView):
    serializer_class = SpaceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "write"

    def get_queryset(self):
        return Space.objects.filter(
            owner=self.request.user
        )


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "meta"


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "meta"


class SpaceTypeListView(generics.ListAPIView):
    queryset = SpaceType.objects.select_related(
        "category"
    ).all()

    serializer_class = SpaceTypeSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "meta"


class AmenityListView(generics.ListAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "meta"
