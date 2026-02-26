from rest_framework import serializers
from .models import Location, SpaceType, Space, SpaceImage


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        
        
class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = '__all__'
        

class SpaceImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SpaceImage
        fields = ['id', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

        
class SpaceSerializer(serializers.ModelSerializer):
    images = SpaceImageSerializer(many=True, read_only=True)
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    owner_phone = serializers.SerializerMethodField()

    # READ
    location = LocationSerializer(read_only=True)
    space_type = SpaceTypeSerializer(read_only=True)

    # WRITE
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source="location",
        write_only=True
    )
    space_type_id = serializers.PrimaryKeyRelatedField(
        queryset=SpaceType.objects.all(),
        source="space_type",
        write_only=True
    )

    class Meta:
        model = Space
        fields = [
            'id',
            'title',
            'description',
            'price',
            'location',
            'location_id',
            'space_type',
            'space_type_id',
            'images',
            'is_available',
            'created_at',
            'owner',
            'is_owner',
            'owner_phone',
        ]

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.owner == request.user
        return False

    def get_owner_phone(self, obj):
        request = self.context.get('request')
        include_owner_phone = self.context.get('include_owner_phone', False)
        if not include_owner_phone or not request or not request.user.is_authenticated:
            return None

        profile = getattr(obj.owner, "userprofile", None)
        return profile.phone_number if profile else None

    def _attach_images(self, space):
        request = self.context.get("request")
        if not request:
            return

        for uploaded_image in request.FILES.getlist("images"):
            SpaceImage.objects.create(space=space, image=uploaded_image)

    def create(self, validated_data):
        space = super().create(validated_data)
        self._attach_images(space)
        return space

    def update(self, instance, validated_data):
        space = super().update(instance, validated_data)
        self._attach_images(space)
        return space
