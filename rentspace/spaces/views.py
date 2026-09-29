from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.db.models import Count

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import (
    Space,
    Category,
    SpaceType,
    Amenity,
    Location,
    Institution,
)

from .serializers import (
    SpaceSerializer,
    CategorySerializer,
    SpaceTypeSerializer,
    AmenitySerializer,
    LocationSerializer,
    InstitutionSerializer
)


class SpaceListView(generics.ListAPIView):
    serializer_class = SpaceSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "search"

    def get_queryset(self):
        queryset = (
            Space.objects
            .filter(is_available=True)
            .select_related(
                "owner",
                "category",
                "space_type",
                "location",
                "student_details",
                "student_details__institution",
            )
            .prefetch_related(
                "amenities",
                "images",
            )
        )

        params = self.request.query_params

        # --------------------------------------------------
        # LOCATION
        # --------------------------------------------------

        city = params.get("city")
        if city:
            queryset = queryset.filter(
                location__city__iexact=city.strip()
            )

        area = params.get("area")
        if area:
            queryset = queryset.filter(
                location__area__iexact=area.strip()
            )

        province = params.get("province")
        if province:
            queryset = queryset.filter(
                location__province__iexact=province.strip()
            )

        # --------------------------------------------------
        # CATEGORY
        # --------------------------------------------------

        category = params.get("category")
        if category:
            queryset = queryset.filter(
                category__slug__iexact=category.strip()
            )

        # --------------------------------------------------
        # SPACE TYPE
        # --------------------------------------------------

        space_type = params.get("space_type")
        if space_type:
            queryset = queryset.filter(
                space_type__name__iexact=space_type.strip()
            )

        # --------------------------------------------------
        # LISTING PURPOSE
        # rent / sale
        # --------------------------------------------------

        listing_purpose = params.get("listing_purpose")
        if listing_purpose in {"rent", "sale"}:
            queryset = queryset.filter(
                listing_purpose=listing_purpose
            )

        # --------------------------------------------------
        # RENTAL PERIOD
        # --------------------------------------------------

        rental_period = params.get("rental_period")
        if rental_period:
            queryset = queryset.filter(
                rental_period=rental_period.strip()
            )

        # --------------------------------------------------
        # CURRENCY
        # --------------------------------------------------

        currency = params.get("currency")
        if currency:
            queryset = queryset.filter(
                currency__iexact=currency.strip()
            )

        # --------------------------------------------------
        # PRICE
        # --------------------------------------------------

        min_price = params.get("min_price")
        if min_price:
            queryset = queryset.filter(
                price__gte=min_price
            )

        max_price = params.get("max_price")
        if max_price:
            queryset = queryset.filter(
                price__lte=max_price
            )

        # --------------------------------------------------
        # BEDROOMS
        # --------------------------------------------------

        bedrooms = params.get("bedrooms")
        if bedrooms:
            queryset = queryset.filter(
                bedrooms__gte=bedrooms
            )

        # --------------------------------------------------
        # BATHROOMS
        # --------------------------------------------------

        bathrooms = params.get("bathrooms")
        if bathrooms:
            queryset = queryset.filter(
                bathrooms__gte=bathrooms
            )

        # --------------------------------------------------
        # FURNISHED
        # --------------------------------------------------

        furnished = params.get("furnished")

        if furnished is not None:
            furnished_value = furnished.lower()

            if furnished_value in {"true", "1", "yes"}:
                queryset = queryset.filter(
                    furnished=True
                )

            elif furnished_value in {"false", "0", "no"}:
                queryset = queryset.filter(
                    furnished=False
                )

        # --------------------------------------------------
        # VERIFICATION
        # --------------------------------------------------

        verified = params.get("verified")

        if verified is not None:
            verified_value = verified.lower()

            if verified_value in {"true", "1", "yes"}:
                queryset = queryset.filter(
                    verification_status="verified"
                )

            elif verified_value in {"false", "0", "no"}:
                queryset = queryset.exclude(
                    verification_status="verified"
                )

        # --------------------------------------------------
        # AMENITIES
        # Example:
        # ?amenity=Wi-Fi
        # --------------------------------------------------

        amenity = params.get("amenity")

        if amenity:
            queryset = queryset.filter(
                amenities__name__iexact=amenity.strip()
            )

        # --------------------------------------------------
        # STUDENT ACCOMMODATION
        # --------------------------------------------------

        institution = params.get("institution")

        if institution:
            queryset = queryset.filter(
                student_details__institution__slug__iexact=(
                    institution.strip()
                )
            )

        room_type = params.get("room_type")

        if room_type:
            queryset = queryset.filter(
                student_details__room_type=room_type.strip()
            )

        bathroom_type = params.get("bathroom_type")

        if bathroom_type:
            queryset = queryset.filter(
                student_details__bathroom_type=(
                    bathroom_type.strip()
                )
            )

        meal_plan = params.get("meal_plan")

        if meal_plan:
            queryset = queryset.filter(
                student_details__meal_plan=meal_plan.strip()
            )

        max_distance = params.get("max_distance")

        if max_distance:
            queryset = queryset.filter(
                student_details__distance_to_campus_km__lte=(
                    max_distance
                )
            )

        # --------------------------------------------------
        # SEARCH
        # --------------------------------------------------

        search = params.get("search")

        if search:
            search = search.strip()

            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__city__icontains=search)
                | Q(location__area__icontains=search)
                | Q(location__province__icontains=search)
                | Q(category__name__icontains=search)
                | Q(space_type__name__icontains=search)
            )

        return queryset.distinct()


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
        return (
            Space.objects
            .filter(owner=self.request.user)
            .select_related(
                "category",
                "space_type",
                "location",
                "student_details",
                "student_details__institution",
            )
            .prefetch_related(
                "amenities",
                "images",
            )
        )


class SpaceDetailView(RetrieveAPIView):
    queryset = (
        Space.objects
        .all()
        .select_related(
            "owner",
            "category",
            "space_type",
            "location",
            "student_details",
            "student_details__institution",
        )
        .prefetch_related(
            "amenities",
            "images",
        )
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
    queryset = (
        SpaceType.objects
        .select_related("category")
        .all()
    )

    serializer_class = SpaceTypeSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "meta"


class AmenityListView(generics.ListAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "meta"
    
class InstitutionListView(generics.ListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [permissions.AllowAny]
    
    
class DashboardView(generics.GenericAPIView):
    """
    Founder/Admin dashboard statistics.
    Only accessible to staff users.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        User = get_user_model()

        now = timezone.now()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # ==================================================
        # USERS
        # User model uses date_joined
        # ==================================================

        total_users = User.objects.count()

        new_users_today = User.objects.filter(
            date_joined__date=today
        ).count()

        new_users_week = User.objects.filter(
            date_joined__gte=week_ago
        ).count()

        new_users_month = User.objects.filter(
            date_joined__gte=month_ago
        ).count()

        # ==================================================
        # SPACES
        # Space model uses created_at
        # ==================================================

        total_spaces = Space.objects.count()

        available_spaces = Space.objects.filter(
            is_available=True
        ).count()

        unavailable_spaces = Space.objects.filter(
            is_available=False
        ).count()

        verified_spaces = Space.objects.filter(
            verification_status="verified"
        ).count()

        unverified_spaces = Space.objects.exclude(
            verification_status="verified"
        ).count()

        new_spaces_today = Space.objects.filter(
            created_at__date=today
        ).count()

        new_spaces_week = Space.objects.filter(
            created_at__gte=week_ago
        ).count()

        new_spaces_month = Space.objects.filter(
            created_at__gte=month_ago
        ).count()

        # ==================================================
        # LISTING PURPOSE
        # ==================================================

        rent_spaces = Space.objects.filter(
            listing_purpose="rent"
        ).count()

        sale_spaces = Space.objects.filter(
            listing_purpose="sale"
        ).count()

        # ==================================================
        # STUDENT ACCOMMODATION
        # ==================================================

        student_spaces = Space.objects.filter(
            student_details__isnull=False
        ).count()

        # ==================================================
        # LISTINGS BY CITY
        # ==================================================

        listings_by_city = (
            Space.objects
            .values("location__city")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        listings_by_city = [
            {
                "city": item["location__city"],
                "count": item["count"],
            }
            for item in listings_by_city
        ]

        # ==================================================
        # USERS - LAST 30 DAYS
        # User model uses date_joined
        # ==================================================

        users_by_day = (
            User.objects
            .filter(date_joined__gte=month_ago)
            .annotate(
                day=TruncDate("date_joined")
            )
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        users_by_day_dict = {
            item["day"].isoformat(): item["count"]
            for item in users_by_day
        }

        users_growth = []

        for i in range(30):
            day = today - timedelta(days=29 - i)

            users_growth.append({
                "date": day.isoformat(),
                "count": users_by_day_dict.get(
                    day.isoformat(),
                    0
                ),
            })

        # ==================================================
        # SPACES - LAST 30 DAYS
        # Space model uses created_at
        # ==================================================

        spaces_by_day = (
            Space.objects
            .filter(created_at__gte=month_ago)
            .annotate(
                day=TruncDate("created_at")
            )
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        spaces_by_day_dict = {
            item["day"].isoformat(): item["count"]
            for item in spaces_by_day
        }

        spaces_growth = []

        for i in range(30):
            day = today - timedelta(days=29 - i)

            spaces_growth.append({
                "date": day.isoformat(),
                "count": spaces_by_day_dict.get(
                    day.isoformat(),
                    0
                ),
            })

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response({
            "users": {
                "total": total_users,
                "today": new_users_today,
                "this_week": new_users_week,
                "this_month": new_users_month,
            },

            "spaces": {
                "total": total_spaces,
                "available": available_spaces,
                "unavailable": unavailable_spaces,
                "verified": verified_spaces,
                "unverified": unverified_spaces,
                "today": new_spaces_today,
                "this_week": new_spaces_week,
                "this_month": new_spaces_month,
            },

            "listing_purpose": {
                "rent": rent_spaces,
                "sale": sale_spaces,
            },

            "student_accommodation": student_spaces,

            "listings_by_city": listings_by_city,

            "growth": {
                "users": users_growth,
                "spaces": spaces_growth,
            },
        })