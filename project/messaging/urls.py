from django.urls import path
from . import views

urlpatterns = [
    path('send-message/', views.SendMessageView.as_view(), name='send-message'),
    path('get-messages/', views.GetMessagesView.as_view(), name='get-messages'),
    path('mark-as-read/', views.MarkAsReadView.as_view(), name='mark-as-read'),
    path('thread/<int:thread_id>/', views.MessageThreadView.as_view(), name='message-thread'),
    path('create-group-thread/', views.CreateGroupThreadView.as_view(), name='create-group-thread'),
    path('thread/<int:thread_id>/add-participant/', views.AddParticipantToThreadView.as_view(), name='add-participant-to-thread'),
    path('thread/<int:thread_id>/remove-participant/', views.RemoveParticipantFromThreadView.as_view(), name='remove-participant-from-thread'),
    path('delete-message/', views.DeleteMessageView.as_view(), name='delete-message'),
    path('forward-message/', views.ForwardMessageView.as_view(), name='forward-message'),
    path('react-to-message/', views.ReactToMessageView.as_view(), name='react-to-message'),
    path('share-media/', views.ShareMediaView.as_view(), name='share-media'),
    path('shared-media/<int:contact_id>/', views.SharedMediaView.as_view(), name='shared-media'),
    path('shared-links/<int:contact_id>/', views.SharedLinksView.as_view(), name='shared-links'),
    path('shared-docs/<int:contact_id>/', views.SharedDocsView.as_view(), name='shared-docs'),
]
