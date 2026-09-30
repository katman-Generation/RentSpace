from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Conversation, Message

from .serializers import (
    ConversationSerializer,
    CreateConversationSerializer,
    MessageSerializer,
    CreateMessageSerializer,
)


class ConversationListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(
                renter=self.request.user
            )
            .select_related(
                "space",
                "renter",
                "owner",
            )
            .prefetch_related(
                "messages__sender"
            )
        ) | (
            Conversation.objects
            .filter(
                owner=self.request.user
            )
            .select_related(
                "space",
                "renter",
                "owner",
            )
            .prefetch_related(
                "messages__sender"
            )
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateConversationSerializer

        return ConversationSerializer


class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Conversation.objects
            .filter(
                renter=self.request.user
            )
            .select_related(
                "space",
                "renter",
                "owner",
            )
            .prefetch_related(
                "messages__sender"
            )
        ) | (
            Conversation.objects
            .filter(
                owner=self.request.user
            )
            .select_related(
                "space",
                "renter",
                "owner",
            )
            .prefetch_related(
                "messages__sender"
            )
        )


class MessageCreateView(generics.CreateAPIView):
    serializer_class = CreateMessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_conversation(self):
        return get_object_or_404(
            Conversation,
            pk=self.kwargs["conversation_id"],
        )

    def perform_create(self, serializer):
        conversation = self.get_conversation()

        if (
            conversation.renter != self.request.user
            and conversation.owner != self.request.user
        ):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "You are not a participant in this conversation."
            )

        serializer.save(
            conversation=conversation,
            sender=self.request.user,
        )


class MessageReadView(generics.UpdateAPIView):
    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_queryset(self):
        return Message.objects.filter(
            conversation__renter=self.request.user
        ) | Message.objects.filter(
            conversation__owner=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(is_read=True)


class ConversationReadView(APIView):
    """
    Mark all unread incoming messages in a conversation
    as read.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation,
            pk=conversation_id,
        )

        if (
            conversation.renter != request.user
            and conversation.owner != request.user
        ):
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "You are not a participant in this conversation."
            )

        updated_count = (
            conversation.messages
            .filter(
                is_read=False
            )
            .exclude(
                sender=request.user
            )
            .update(
                is_read=True
            )
        )

        return Response({
            "success": True,
            "marked_read": updated_count,
        })


class UnreadMessageCountView(APIView):
    """
    Return the total number of unread incoming messages
    for the authenticated user.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        unread_count = (
            Message.objects
            .filter(
                conversation__renter=request.user,
                is_read=False,
            )
            .exclude(
                sender=request.user
            )
            .count()
        )

        unread_count += (
            Message.objects
            .filter(
                conversation__owner=request.user,
                is_read=False,
            )
            .exclude(
                sender=request.user
            )
            .count()
        )

        return Response({
            "unread_count": unread_count,
        })