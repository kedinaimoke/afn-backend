from django.urls import path
from . import views

urlpatterns = [
    path('send-message/', views.send_message, name='send_message'),
    path('get-messages/', views.get_messages, name='get_messages'),
    path('mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('thread/<int:thread_id>/', views.message_thread, name='message_thread'),
]
