from django.urls import path

from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    MessageCreateView,
    MessageReadView,
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
        "messages/<int:pk>/read/",
        MessageReadView.as_view(),
        name="message-read",
    ),
]
