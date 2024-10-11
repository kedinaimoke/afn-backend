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
    """
    Method: POST
    Description: Sends a message from the logged-in user to a specified recipient. The message can include text content and/or a media file.
    Parameters:
    recipient_id (required): The ID of the user who will receive the message.
    content (optional): The text content of the message.
    media_file (optional): A media file (image, video, audio, or document) to send along with the message.
    Response:
    200 OK: If the message is successfully sent. The response includes the serialized message data.
    400 Bad Request: If the recipient is not provided or if the media file is not of an allowed type or exceeds the size limit.
    """
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
    """
    Method: GET
    Description: Retrieves all messages sent to the logged-in user, ordered by timestamp (most recent first).
    Parameters: None.
    Response:
    200 OK: A list of messages that have been sent to the user, serialized with details like sender, content, media type, media URL, and timestamp.
    """
    messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse({'messages': serializer.data})

@login_required
@require_http_methods(["POST"])
def mark_as_read(request):
    """
    Method: POST
    Description: Marks a specific message as read by the logged-in user.
    Parameters:
    message_id (required): The ID of the message to mark as read.
    Response:
    200 OK: If the message is successfully marked as read.
    400 Bad Request: If the message ID is not provided.
    404 Not Found: If the message does not exist or if the user is not the recipient.
    """
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
    """
    Method: POST

    Description: Creates a new message thread with one or more participants.
    Parameters:
    participant_ids: A list of user IDs to be added as participants in the thread.
    
    Response:
    200 OK: Returns the created thread data, including participants and thread ID.
    400 Error: Returns an error if no valid participants are provided.
    """
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
    """
    Method: GET

    Description: Retrieves all messages from a specific thread that the user is a participant in.

    Parameters:
    thread_id: The ID of the thread to retrieve messages from.
    
    Response:
    200 OK: Returns a list of messages in the thread.
    400 Error: Returns an error if the user is not a participant in the thread or the thread does not exist.
    """
    thread = get_object_or_404(Thread, id=thread_id)

    if request.user not in thread.participants.all():
        return JsonResponse({'error': 'You are not a participant in this thread.'}, status=403)

    messages = Message.objects.filter(thread=thread).order_by('-timestamp')
    serializer = MessageSerializer(messages, many=True)
    return JsonResponse({'messages': serializer.data})

@login_required
@require_http_methods(["POST"])
def create_group_thread(request):
    """
    Method: POST

    Description: Creates a new group thread with multiple participants and a name.

    Parameters:
    participant_ids (required): A list of participant user IDs.
    name (required): The name of the group thread.

    Response:
    200 OK: Returns the created group thread data, including participants and thread name.
    400 Error: Returns an error if the thread name or participant list is missing.
    """
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
    """
    Method: POST

    Description: Adds a new participant to an existing thread, given the user is already a participant in the thread.

    Parameters:
    thread_id (required): The ID of the thread.
    participant_id (required): The ID of the participant to add.

    Response:
    200 OK: Returns a success message when the participant is added.
    400 Error: Returns an error if the user is not a participant in the thread or if the participant or thread does not exist.
    """
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
    """
    Method: POST

    Description: Removes a participant from a thread, given the user is a participant in the thread.

    Parameters:
    thread_id (required): The ID of the thread.
    participant_id (required): The ID of the participant to remove.
    
    Response:
    200 OK: Returns a success message when the participant is removed.
    400 Error: Returns an error if the user is not a participant in the thread or if the participant or thread does not exist.
    """
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
    """
    Method: POST

    Description: Deletes a message sent by the authenticated user.

    Parameters:
    message_id (required): The ID of the message to delete.

    Response:
    200 OK: Returns a success message when the message is deleted.
    400 Error: Returns an error if the message does not exist or if the user is not the sender.
    """
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
    """
    Method: POST

    Description: Forwards an existing message to a new recipient.

    Parameters:
    original_message_id (required): The ID of the original message to forward.
    recipient_id (required): The ID of the new recipient.

    Response:
    200 OK: Returns the forwarded message data.
    400 Error: Returns an error if the original message or recipient is not found.
    """
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
    """
    Method: POST

    Description: Adds or updates a reaction (like, emoji, etc.) to a message.

    Parameters:
    message_id (required): The ID of the message to react to.
    reaction_type (required): The type of reaction (e.g., like, etc.).
    
    Response:
    200 OK: Returns a success message when the reaction is added or updated.
    400 Error: Returns an error if the message does not exist or if the required parameters are missing.
    """
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
