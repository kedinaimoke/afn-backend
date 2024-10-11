from django.urls import path
from . import views

urlpatterns = [
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
    path('mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('thread/<int:thread_id>/', views.message_thread, name='message_thread'),
    path('create-group-thread/', views.create_group_thread, name='create_group_thread'),
    path('thread/<int:thread_id>/add-participant/', views.add_participant_to_thread, name='add_participant_to_thread'),
    path('thread/<int:thread_id>/remove-participant/', views.remove_participant_from_thread, name='remove_participant_from_thread'),
    path('shared-media/<int:contact_id>/', views.SharedMediaView.as_view(), name='shared_media'),
    path('shared-links/<int:contact_id>/', views.SharedLinksView.as_view(), name='shared_links'),
    path('shared-docs/<int:contact_id>/', views.SharedDocsView.as_view(), name='shared_docs'),
]
