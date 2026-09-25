import json

from django.db import transaction
from rest_framework import serializers


from .models import (
    Location,
    Category,
    SpaceType,
    Amenity,
    Space,
    SpaceImage,
    Institution,
    StudentAccommodation,
)


# ============================================================
# LOCATION
# ============================================================

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = "__all__"


# ============================================================
# CATEGORY
# ============================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


# ============================================================
# SPACE TYPE
# ============================================================

class SpaceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SpaceType
        fields = "__all__"


# ============================================================
# AMENITY
# ============================================================

class AmenitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Amenity
        fields = "__all__"


# ============================================================
# INSTITUTION
# ============================================================

class InstitutionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Institution
        fields = "__all__"


# ============================================================
# STUDENT ACCOMMODATION
# ============================================================

class StudentAccommodationSerializer(serializers.ModelSerializer):

    institution = InstitutionSerializer(
        read_only=True
    )

    institution_id = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(),
        source="institution",
        write_only=True
    )

    class Meta:
        model = StudentAccommodation

        fields = [
            "id",
            "institution",
            "institution_id",
            "campus",
            "distance_to_campus_km",
            "room_type",
            "rooms_available",
            "bathroom_type",
            "meal_plan",
        ]


# ============================================================
# SPACE IMAGE
# ============================================================

class SpaceImageSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = SpaceImage

        fields = [
            "id",
            "image",
        ]

    def get_image(self, obj):

        request = self.context.get("request")

        if request and obj.image:
            return request.build_absolute_uri(
                obj.image.url
            )

        return obj.image.url if obj.image else None


# ============================================================
# SPACE
# ============================================================

class SpaceSerializer(serializers.ModelSerializer):

    # --------------------------------------------------------
    # Images
    # --------------------------------------------------------

    images = SpaceImageSerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # Owner
    # --------------------------------------------------------

    owner = serializers.ReadOnlyField(
        source="owner.email"
    )

    owner_name = serializers.SerializerMethodField()

    owner_phone = serializers.SerializerMethodField()

    is_owner = serializers.SerializerMethodField()

    # --------------------------------------------------------
    # Related objects
    # --------------------------------------------------------

    location = LocationSerializer(
        read_only=True
    )

    category = CategorySerializer(
        read_only=True
    )

    space_type = SpaceTypeSerializer(
        read_only=True
    )

    amenities = AmenitySerializer(
        many=True,
        read_only=True
    )

    # --------------------------------------------------------
    # Student details
    # --------------------------------------------------------

    student_details = StudentAccommodationSerializer(
        required=False,
        allow_null=True
    )

    # --------------------------------------------------------
    # Write-only relationship IDs
    # --------------------------------------------------------

    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True
    )

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True
    )

    space_type_id = serializers.PrimaryKeyRelatedField(
        queryset=SpaceType.objects.all(),
        source="space_type",
        write_only=True
    )

    amenity_ids = serializers.PrimaryKeyRelatedField(
        queryset=Amenity.objects.all(),
        source="amenities",
        many=True,
        write_only=True,
        required=False
    )

    # --------------------------------------------------------
    # Verification
    # --------------------------------------------------------

    verification_status = serializers.CharField(
        read_only=True
    )

    verified_at = serializers.DateTimeField(
        read_only=True
    )

    # --------------------------------------------------------
    # Meta
    # --------------------------------------------------------

    class Meta:
        model = Space

        fields = [
            "id",

            # Basic information
            "title",
            "description",

            # Classification
            "category",
            "category_id",
            "space_type",
            "space_type_id",

            # Location
            "location",
            "location_id",

            # Buy / Rent
            "listing_purpose",
            "rental_period",

            # Pricing
            "price",
            "currency",
            "deposit",

            # Availability
            "available_from",
            "is_available",

            # Property details
            "bedrooms",
            "bathrooms",
            "parking_spaces",
            "floor_area",
            "furnished",
            "capacity",

            # Amenities
            "amenities",
            "amenity_ids",

            # Student accommodation
            "student_details",

            # Images
            "images",

            # Verification
            "verification_status",
            "verified_at",

            # Owner
            "owner",
            "owner_name",
            "owner_phone",
            "is_owner",

            # Timestamps
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "owner",
            "owner_name",
            "owner_phone",
            "is_owner",
            "verification_status",
            "verified_at",
            "created_at",
            "updated_at",
        ]

    # ========================================================
    # OWNER
    # ========================================================

    def get_owner_name(self, obj):

        return (
            f"{obj.owner.first_name} "
            f"{obj.owner.last_name}"
        ).strip()

    # ========================================================
    # IS OWNER
    # ========================================================

    def get_is_owner(self, obj):

        request = self.context.get("request")

        if (
            request
            and request.user.is_authenticated
        ):
            return obj.owner == request.user

        return False

    # ========================================================
    # OWNER PHONE
    # ========================================================

    def get_owner_phone(self, obj):

        request = self.context.get("request")

        include_owner_phone = self.context.get(
            "include_owner_phone",
            False
        )

        if (
            not include_owner_phone
            or not request
            or not request.user.is_authenticated
        ):
            return None

        return obj.owner.phone_number

    # ========================================================
    # VALIDATION
    # ========================================================
    def to_internal_value(self, data):
        
        if hasattr(data, "lists"):
            data = {
                key: values[-1] if len(values) == 1 else values
                for key, values in data.lists()
            }
        else:
            data = data.copy()

        student_details = data.get("student_details")

        if isinstance(student_details, str):

            try:
                data["student_details"] = json.loads(student_details)

            except json.JSONDecodeError:

                raise serializers.ValidationError({
                    "student_details": (
                        "Student accommodation details "
                        "must be valid JSON."
                    )
                })

        return super().to_internal_value(data)
    
    def validate(self, attrs):

        category = attrs.get(
            "category",
            getattr(
                self.instance,
                "category",
                None
            )
        )

        space_type = attrs.get(
            "space_type",
            getattr(
                self.instance,
                "space_type",
                None
            )
        )

        listing_purpose = attrs.get(
            "listing_purpose",
            getattr(
                self.instance,
                "listing_purpose",
                None
            )
        )

        student_details = attrs.get(
            "student_details"
        )

        # ----------------------------------------------------
        # Space type must belong to category
        # ----------------------------------------------------

        if category and space_type:

            if space_type.category_id != category.id:

                raise serializers.ValidationError({
                    "space_type_id": (
                        "This space type does not belong "
                        "to the selected category."
                    )
                })

        # ----------------------------------------------------
        # Category / listing purpose rules
        # ----------------------------------------------------

        if category and listing_purpose:

            if category.slug == "buy":

                if listing_purpose != "sale":

                    raise serializers.ValidationError({
                        "listing_purpose": (
                            "Buy listings must be marked "
                            "as For Sale."
                        )
                    })

            elif category.slug in [
                "rent",
                "student-accommodation",
            ]:

                if listing_purpose != "rent":

                    raise serializers.ValidationError({
                        "listing_purpose": (
                            "This category is for rental "
                            "listings."
                        )
                    })

        # ----------------------------------------------------
        # Student accommodation rules
        # ----------------------------------------------------

        if category:

            is_student_category = (
                category.slug == "student-accommodation"
            )

            if is_student_category and not student_details:

                raise serializers.ValidationError({
                    "student_details": (
                        "Student accommodation listings "
                        "must include student accommodation "
                        "details."
                    )
                })

            if (
                not is_student_category
                and student_details
            ):

                raise serializers.ValidationError({
                    "student_details": (
                        "Student accommodation details "
                        "can only be used with the "
                        "Student Accommodation category."
                    )
                })

        return attrs

    # ========================================================
    # IMAGES
    # ========================================================

    def _attach_images(self, space):

        request = self.context.get("request")

        if not request:
            return

        for uploaded_image in request.FILES.getlist(
            "images"
        ):

            SpaceImage.objects.create(
                space=space,
                image=uploaded_image
            )

    # ========================================================
    # CREATE
    # ========================================================

    @transaction.atomic
    def create(self, validated_data):

        student_details = validated_data.pop(
            "student_details",
            None
        )

        amenities = validated_data.pop(
            "amenities",
            []
        )

        space = super().create(
            validated_data
        )

        if amenities:
            space.amenities.set(
                amenities
            )

        if student_details:
            StudentAccommodation.objects.create(
                space=space,
                **student_details
            )

        self._attach_images(space)

        return space

    # ========================================================
    # UPDATE
    # ========================================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data
    ):

        student_details = validated_data.pop(
            "student_details",
            None
        )

        amenities = validated_data.pop(
            "amenities",
            None
        )

        space = super().update(
            instance,
            validated_data
        )

        if amenities is not None:

            space.amenities.set(
                amenities
            )

        if student_details is not None:

            student_accommodation = getattr(
                space,
                "student_details",
                None
            )

            if student_accommodation:

                for attr, value in student_details.items():

                    setattr(
                        student_accommodation,
                        attr,
                        value
                    )

                student_accommodation.save()

            else:

                StudentAccommodation.objects.create(
                    space=space,
                    **student_details
                )

        self._attach_images(space)

        return space