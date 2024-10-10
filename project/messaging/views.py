from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Message, Thread
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.storage import default_storage

@login_required
@require_http_methods(["POST"])
def send_message(request):
    recipient_id = request.POST.get('recipient_id')
    content = request.POST.get('content')
    media_file = request.FILES.get('media_file')

    if not recipient_id:
        return JsonResponse({'error': 'Recipient is required.'}, status=400)

    recipient = get_object_or_404(User, id=recipient_id)

    media_url = None
    media_type = None

    if media_file:
        media_url = default_storage.save(f'media/{media_file.name}', media_file)
        if media_file.content_type.startswith('image'):
            media_type = 'image'
        elif media_file.content_type.startswith('video'):
            media_type = 'video'
        elif media_file.content_type.startswith('audio'):
            media_type = 'audio'
        else:
            media_type = 'file'

    message = Message.objects.create(
        sender=request.user,
        recipient=recipient,
        content=content,
        media_type=media_type,
        media_url=media_url,
    )

    return JsonResponse({'status': 'success', 'message_id': message.id})

@login_required
@require_http_methods(["GET"])
def get_messages(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')

    messages_data = [{
        'id': message.id,
        'sender': message.sender.username,
        'content': message.content,
        'media_type': message.media_type,
        'media_url': message.media_url,
        'timestamp': message.timestamp,
        'is_read': message.is_read,
    } for message in messages]

    return JsonResponse({'messages': messages_data})


@login_required
@require_http_methods(["POST"])
def mark_as_read(request):
    message_id = request.POST.get('message_id')

    if not message_id:
        return JsonResponse({'error': 'Message ID is required.'}, status=400)

    try:
        message = Message.objects.get(id=message_id, recipient=request.user)
        message.is_read = True
        message.save()
        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found.'}, status=404)

@login_required
@require_http_methods(["GET"])
def message_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)
    
    if request.user not in thread.participants.all():
        return JsonResponse({'error': 'You are not a participant in this thread.'}, status=403)

    messages = Message.objects.filter(sender__in=thread.participants.all(), recipient__in=thread.participants.all()).order_by('-timestamp')

    messages_data = [{
        'id': message.id,
        'sender': message.sender.username,
        'recipient': message.recipient.username,
        'content': message.content,
        'timestamp': message.timestamp,
        'is_read': message.is_read,
    } for message in messages]

    return JsonResponse({'messages': messages_data})
