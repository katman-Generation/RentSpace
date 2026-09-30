from django.urls import path

from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageCreateView,
    MessageReadView,
    ConversationReadView,
    UnreadMessageCountView,
)


urlpatterns = [
    path(
        "conversations/",
        ConversationListCreateView.as_view(),
        name="conversation-list-create",
    ),

    path(
        "conversations/<int:pk>/",
        ConversationDetailView.as_view(),
        name="conversation-detail",
    ),

    path(
        "conversations/<int:conversation_id>/messages/",
        MessageCreateView.as_view(),
        name="message-create",
    ),

    path(
        "conversations/<int:conversation_id>/read/",
        ConversationReadView.as_view(),
        name="conversation-read",
    ),

    path(
        "messages/<int:pk>/read/",
        MessageReadView.as_view(),
        name="message-read",
    ),

    path(
        "unread-count/",
        UnreadMessageCountView.as_view(),
        name="unread-message-count",
    ),
]