from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Message, Thread, Reaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .serializers import MessageSerializer, ThreadSerializer
from rest_framework.response import Response
from rest_framework import status

ALLOWED_MEDIA_TYPES = ['image/jpeg', 'image/png', 'video/mp4', 'audio/mpeg', 'application/pdf', 'application/octet-stream']
MAX_MEDIA_SIZE = 200 * 1024**2

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
        if media_file.content_type not in ALLOWED_MEDIA_TYPES:
            return JsonResponse({'error': 'Unsupported media type.'}, status=400)
        
        if media_file.size > MAX_MEDIA_SIZE:
            return JsonResponse({'error': 'Media file exceeds size limit of 200 MB.'}, status=400)

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

    serializer = MessageSerializer(message)
    return JsonResponse({'status': 'success', 'message': serializer.data})

@login_required
@require_http_methods(["GET"])
def get_messages(request):
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse({'messages': serializer.data})

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
@require_http_methods(["POST"])
def create_thread(request):
    participant_ids = request.POST.getlist('participant_ids')
    participants = User.objects.filter(id__in=participant_ids)

    if not participants.exists():
        return JsonResponse({'error': 'At least one valid participant is required.'}, status=400)

    thread = Thread.objects.create()
    thread.participants.set(participants)
    thread.save()

    serializer = ThreadSerializer(thread)
    return JsonResponse({'status': 'success', 'thread': serializer.data})

@login_required
@require_http_methods(["GET"])
def message_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if request.user not in thread.participants.all():
        return JsonResponse({'error': 'You are not a participant in this thread.'}, status=403)

    messages = Message.objects.filter(thread=thread).order_by('-timestamp')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse({'messages': serializer.data})

@login_required
@require_http_methods(["POST"])
def create_group_thread(request):
    participant_ids = request.POST.getlist('participant_ids')
    thread_name = request.POST.get('name')

    if not thread_name:
        return JsonResponse({'error': 'Thread name is required.'}, status=400)

    if not participant_ids:
        return JsonResponse({'error': 'At least one participant is required.'}, status=400)

    participants = User.objects.filter(id__in=participant_ids)
    thread = Thread.objects.create(name=thread_name)
    thread.participants.set(participants)

    serializer = ThreadSerializer(thread)
    return JsonResponse({'status': 'success', 'thread': serializer.data})

@login_required
@require_http_methods(["POST"])
def add_participant_to_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if request.user not in thread.participants.all():
        return JsonResponse({'error': 'You are not a participant in this thread.'}, status=403)

    participant_id = request.POST.get('participant_id')
    participant = get_object_or_404(User, id=participant_id)

    thread.participants.add(participant)

    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(["POST"])
def remove_participant_from_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    if request.user not in thread.participants.all():
        return JsonResponse({'error': 'You are not a participant in this thread.'}, status=403)

    participant_id = request.POST.get('participant_id')
    participant = get_object_or_404(User, id=participant_id)

    thread.participants.remove(participant)

    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(["POST"])
def delete_message(request):
    message_id = request.POST.get('message_id')

    if not message_id:
        return JsonResponse({'error': 'Message ID is required.'}, status=400)

    try:
        message = Message.objects.get(id=message_id, sender=request.user)
        message.delete()
        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found.'}, status=404)

@login_required
@require_http_methods(["POST"])
def forward_message(request):
    original_message_id = request.POST.get('original_message_id')
    new_recipient_id = request.POST.get('recipient_id')

    if not original_message_id or not new_recipient_id:
        return JsonResponse({'error': 'Original message ID and new recipient ID are required.'}, status=400)

    try:
        original_message = Message.objects.get(id=original_message_id)

        new_message = Message.objects.create(
            sender=request.user,
            recipient=get_object_or_404(User, id=new_recipient_id),
            content=original_message.content,
            media_type=original_message.media_type,
            media_url=original_message.media_url,
        )

        serializer = MessageSerializer(new_message)
        return JsonResponse({'status': 'success', 'new_message': serializer.data})
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Original message not found.'}, status=404)

@login_required
@require_http_methods(["POST"])
def react_to_message(request):
    message_id = request.POST.get('message_id')
    reaction_type = request.POST.get('reaction_type')

    if not message_id or not reaction_type:
        return JsonResponse({'error': 'Message ID and reaction type are required.'}, status=400)

    try:
        message = Message.objects.get(id=message_id)

        existing_reaction = Reaction.objects.filter(message=message, user=request.user).first()
        
        if existing_reaction:
            existing_reaction.reaction_type = reaction_type
            existing_reaction.save()
        else:
            Reaction.objects.create(message=message, user=request.user, reaction_type=reaction_type)

        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found.'}, status=404)
