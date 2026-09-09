from rest_framework import serializers

from .models import Conversation, Message
from users.models import User


class MessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.ReadOnlyField(
        source="sender.email"
    )

    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "id",
            "sender_email",
            "sender_name",
            "content",
            "is_read",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "sender_email",
            "sender_name",
            "is_read",
            "created_at",
        ]

    def get_sender_name(self, obj):
        return (
            f"{obj.sender.first_name} "
            f"{obj.sender.last_name}"
        ).strip()


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(
        many=True,
        read_only=True
    )

    renter_email = serializers.ReadOnlyField(
        source="renter.email"
    )

    renter_name = serializers.SerializerMethodField()

    owner_email = serializers.ReadOnlyField(
        source="owner.email"
    )

    owner_name = serializers.SerializerMethodField()

    space_title = serializers.ReadOnlyField(
        source="space.title"
    )

    space_id = serializers.ReadOnlyField(
        source="space.id"
    )

    class Meta:
        model = Conversation
        fields = [
            "id",
            "space_id",
            "space_title",

            "renter_email",
            "renter_name",

            "owner_email",
            "owner_name",

            "created_at",
            "updated_at",

            "messages",
        ]

        read_only_fields = [
            "id",
            "space_id",
            "space_title",
            "renter_email",
            "renter_name",
            "owner_email",
            "owner_name",
            "created_at",
            "updated_at",
            "messages",
        ]

    def get_renter_name(self, obj):
        return (
            f"{obj.renter.first_name} "
            f"{obj.renter.last_name}"
        ).strip()

    def get_owner_name(self, obj):
        return (
            f"{obj.owner.first_name} "
            f"{obj.owner.last_name}"
        ).strip()


class CreateConversationSerializer(serializers.ModelSerializer):
    space_id = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = Conversation
        fields = [
            "space_id",
        ]

    def validate_space_id(self, value):
        from spaces.models import Space

        try:
            space = Space.objects.select_related(
                "owner"
            ).get(
                pk=value,
                is_available=True
            )
        except Space.DoesNotExist:
            raise serializers.ValidationError(
                "This space does not exist or is not available."
            )

        request = self.context.get("request")

        if request and request.user == space.owner:
            raise serializers.ValidationError(
                "You cannot start a conversation with yourself."
            )

        self.space = space

        return value

    def create(self, validated_data):
        request = self.context["request"]
        space = self.space

        conversation, created = Conversation.objects.get_or_create(
            space=space,
            renter=request.user,
            defaults={
                "owner": space.owner,
            }
        )

        return conversation


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "content",
        ]

    def validate_content(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Message cannot be empty."
            )

        return value
