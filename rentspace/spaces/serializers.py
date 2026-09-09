from rest_framework import serializers

from .models import (
    Location,
    Category,
    SpaceType,
    Amenity,
    Space,
    SpaceImage,
)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = "__all__"


class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class SpaceImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SpaceImage
        fields = ["id", "image"]

    def get_image(self, obj):
        request = self.context.get("request")

        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url if obj.image else None


class SpaceSerializer(serializers.ModelSerializer):

    images = SpaceImageSerializer(
        many=True,
        read_only=True
    )

    owner = serializers.ReadOnlyField(
        source="owner.email"
    )

    owner_name = serializers.SerializerMethodField()

    is_owner = serializers.SerializerMethodField()

    owner_phone = serializers.SerializerMethodField()

    # READ
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

    # WRITE
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

    class Meta:
        model = Space

        fields = [
            "id",

            "title",
            "description",

            "category",
            "category_id",

            "space_type",
            "space_type_id",

            "location",
            "location_id",

            "rental_period",
            "price",
            "deposit",

            "available_from",
            "is_available",

            "bedrooms",
            "bathrooms",
            "parking_spaces",
            "floor_area",
            "furnished",
            "capacity",

            "amenities",
            "amenity_ids",

            "images",

            "owner",
            "owner_name",
            "owner_phone",
            "is_owner",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "owner",
            "owner_name",
            "owner_phone",
            "is_owner",
            "created_at",
            "updated_at",
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip()

    def get_is_owner(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return obj.owner == request.user

        return False

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
    
    def validate(self, attrs):
        category = attrs.get(
            "category",
            getattr(self.instance, "category", None)
        )

        space_type = attrs.get(
            "space_type",
            getattr(self.instance, "space_type", None)
        )

        if category and space_type:
            if space_type.category_id != category.id:
                raise serializers.ValidationError({
                    "space_type_id": (
                        "This space type does not belong to the selected category."
                    )
                })

        return attrs

    def _attach_images(self, space):
        request = self.context.get("request")

        if not request:
            return

        for uploaded_image in request.FILES.getlist("images"):
            SpaceImage.objects.create(
                space=space,
                image=uploaded_image
            )

    def create(self, validated_data):
        amenities = validated_data.pop(
            "amenities",
            []
        )

        space = super().create(validated_data)

        if amenities:
            space.amenities.set(amenities)

        self._attach_images(space)

        return space

    def update(self, instance, validated_data):
        amenities = validated_data.pop(
            "amenities",
            None
        )

        space = super().update(
            instance,
            validated_data
        )

        if amenities is not None:
            space.amenities.set(amenities)

        self._attach_images(space)

        return space
