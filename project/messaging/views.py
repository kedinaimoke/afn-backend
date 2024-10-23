from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Message, Thread, Reaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from .serializers import MessageSerializer, ThreadSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from users.models import Personnel
import firebase_admin
from firebase_admin import credentials, messaging

# cred = credentials.Certificate('path/to/the/serviceAccountKey.json')
# firebase_admin.initialize_app(cred)

ALLOWED_MEDIA_TYPES = ['image/jpeg', 'image/png', 'video/mp4', 'audio/mpeg', 'application/pdf', 'application/octet-stream']
MAX_MEDIA_SIZE = 1024 * 1024**2

class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
        recipient_id = request.data.get('recipient_id')
        content = request.data.get('content')
        media_file = request.FILES.get('media_file')

        if not recipient_id:
            return JsonResponse({'error': 'Recipient is required.'}, status=status.HTTP_400_BAD_REQUEST)

        recipient = get_object_or_404(User, id=recipient_id)

        media_url = None
        media_type = None

        if media_file:
            if media_file.content_type not in ALLOWED_MEDIA_TYPES:
                return JsonResponse({'error': 'Unsupported media type.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if media_file.size > MAX_MEDIA_SIZE:
                return JsonResponse({'error': 'Media file exceeds size limit of 200 MB.'}, status=status.HTTP_400_BAD_REQUEST)

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

class GetMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Method: GET
        Description: Retrieves all messages sent to the logged-in user, ordered by timestamp (most recent first).
        Response:
        200 OK: A list of messages that have been sent to the user, serialized with details like sender, content, media type, media URL, and timestamp.
        """
        messages = Message.objects.filter(recipient=request.user).order_by('-timestamp')
        serializer = MessageSerializer(messages, many=True)
        return JsonResponse({'messages': serializer.data})

class MarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
        message_id = request.data.get('message_id')

        if not message_id:
            return JsonResponse({'error': 'Message ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(id=message_id, recipient=request.user)
            message.is_read = True
            message.save()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)


class CreateThreadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Method: POST

        Description: Creates a new message thread with one or more participants.
        Parameters:
        participant_ids: A list of user IDs to be added as participants in the thread.

        Response:
        200 OK: Returns the created thread data, including participants and thread ID.
        400 Error: Returns an error if no valid participants are provided.
        """
        participant_ids = request.data.getlist('participant_ids')
        participants = User.objects.filter(id__in=participant_ids)

        if not participants.exists():
            return JsonResponse({'error': 'At least one valid participant is required.'}, status=status.HTTP_400_BAD_REQUEST)

        thread = Thread.objects.create()
        thread.participants.set(participants)
        thread.save()

        serializer = ThreadSerializer(thread)
        return JsonResponse({'status': 'success', 'thread': serializer.data})

class MessageThreadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, thread_id, *args, **kwargs):
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
            return JsonResponse({'error': 'You are not a participant in this thread.'}, status=status.HTTP_403_FORBIDDEN)

        messages = Message.objects.filter(thread=thread).order_by('-timestamp')
        serializer = MessageSerializer(messages, many=True)
        return JsonResponse({'messages': serializer.data})

class CreateGroupThreadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
        participant_ids = request.data.getlist('participant_ids')
        thread_name = request.data.get('name')

        if not thread_name:
            return JsonResponse({'error': 'Thread name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not participant_ids:
            return JsonResponse({'error': 'At least one participant is required.'}, status=status.HTTP_400_BAD_REQUEST)

        participants = User.objects.filter(id__in=participant_ids)
        thread = Thread.objects.create(name=thread_name)
        thread.participants.set(participants)

        serializer = ThreadSerializer(thread)
        return JsonResponse({'status': 'success', 'thread': serializer.data})


class AddParticipantToThreadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, thread_id, *args, **kwargs):
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
            return JsonResponse({'error': 'You are not a participant in this thread.'}, status=status.HTTP_403_FORBIDDEN)

        participant_id = request.data.get('participant_id')
        participant = get_object_or_404(User, id=participant_id)

        thread.participants.add(participant)

        return JsonResponse({'status': 'success'})

class RemoveParticipantFromThreadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, thread_id, *args, **kwargs):
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
            return JsonResponse({'error': 'You are not a participant in this thread.'}, status=status.HTTP_403_FORBIDDEN)

        participant_id = request.data.get('participant_id')
        participant = get_object_or_404(User, id=participant_id)

        thread.participants.remove(participant)

        return JsonResponse({'status': 'success'})

class DeleteMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Method: POST

        Description: Deletes a message sent by the authenticated user.

        Parameters:
        message_id (required): The ID of the message to delete.

        Response:
        200 OK: Returns a success message when the message is deleted.
        400 Error: Returns an error if the message does not exist or if the user is not the sender.
        """
        message_id = request.data.get('message_id')

        if not message_id:
            return JsonResponse({'error': 'Message ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(id=message_id, sender=request.user)
            message.delete()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Message, Reaction
from django.contrib.auth.models import User
from rest_framework import status

class ForwardMessageView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures user must be authenticated to access this view

    def post(self, request, *args, **kwargs):
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
        original_message_id = request.data.get('original_message_id')
        new_recipient_id = request.data.get('recipient_id')

        if not original_message_id or not new_recipient_id:
            return JsonResponse({'error': 'Original message ID and new recipient ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

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
            return JsonResponse({'error': 'Original message not found.'}, status=status.HTTP_404_NOT_FOUND)

class ReactToMessageView(APIView):
    permission_classes = [IsAuthenticated]  # Ensures user must be authenticated to access this view

    def post(self, request, *args, **kwargs):
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
        message_id = request.data.get('message_id')
        reaction_type = request.data.get('reaction_type')

        if not message_id or not reaction_type:
            return JsonResponse({'error': 'Message ID and reaction type are required.'}, status=status.HTTP_400_BAD_REQUEST)

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
            return JsonResponse({'error': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)


class SendMessageView(generics.CreateAPIView):
    """
    View to send a message between users.

    This view allows authenticated users to send messages. The sender of the message is automatically
    set to the currently authenticated user.

    HTTP Methods:
    - POST: Create a new message.

    Request Body:
    The request body should contain the following fields:
        - recipient: The email or ID of the user to whom the message is being sent (required).
        - content: The text content of the message (optional).
        - media_type: The type of media attached to the message (optional; choices are 'text', 'image', 'video', 'file', 'audio').
        - media_url: The URL of the media attached to the message (optional).

    Response:
    - On success, returns a 201 status code with the created message data.
    - On failure, returns an appropriate error response.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        recipient_phone_number = self.request.data.get('recipient_phone_number')
        recipient = get_object_or_404(Personnel, phone_number=recipient_phone_number)
        serializer.save(sender=self.request.user, recipient=recipient)

class GetMessagesView(generics.ListAPIView):
    """
    View to retrieve messages for the authenticated user.

    This view allows authenticated users to retrieve a list of messages sent to them.

    HTTP Methods:
    - GET: Retrieve a list of messages.

    Response:
    - On success, returns a 200 status code with a list of messages.
    - On failure, returns an appropriate error response.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user)

# def send_push_notification(token, title, body):
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body,
#         ),
#         token=token,
#     )
#     response = messaging.send(message)
#     print('Successfully sent message:', response)


class ShareMediaView(generics.CreateAPIView):
    """
    Method: POST
    
    Description: Shares a media message (image, video, audio, or document)
    from the authenticated user to a specified recipient.
    
    Permissions: Requires the user to be authenticated.
    
    Request Body:
    - recipient_id: The ID of the user to whom the media is being sent.
    - media: The media file to share (uploaded file).
    - media_type: The type of media (e.g., image, video, audio, document).
    
    Response: Returns the created message data or errors if validation fails.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        recipient_id = request.data.get('recipient_id')
        media = request.FILES.get('media')
        media_type = request.data.get('media_type')

        if not recipient_id or not media or not media_type:
            return Response({'error': 'recipient_id, media, and media_type are required.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = self.ALLOWED_MEDIA_TYPES.get(media_type)
        if not allowed_types or media.content_type not in allowed_types:
            return Response({'error': f'Invalid media type. Allowed types for {media_type} are: {", ".join(allowed_types)}.'}, status=status.HTTP_400_BAD_REQUEST)

        if media.size > self.MAX_FILE_SIZE:
            return Response({'error': 'File size exceeds the maximum limit of 5 MB.'}, status=status.HTTP_400_BAD_REQUEST)

        media_url = default_storage.save(media.name, media)

        message = Message.objects.create(
            sender=request.user,
            recipient_id=recipient_id,
            media_type=media_type,
            media_url=media_url,
        )

        serializer = self.get_serializer(message)
        return Response({'status': 'success', 'message': serializer.data}, status=status.HTTP_201_CREATED)

class SharedMediaView(generics.ListAPIView):
    """
    Method: GET
    
    Description: Retrieves media messages (images, videos, audio files, and documents) 
    shared between the authenticated user and a specified contact.
    
    URL Pattern: shared-media/<int:contact_id>/
    
    Permissions: Requires the user to be authenticated.
    
    Parameters:
    contact_id: The ID of the contact with whom media was shared.
    
    Response: Returns a list of media messages ordered by timestamp (most recent first).
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        contact_id = self.kwargs['contact_id']
        return Message.objects.filter(
            sender=self.request.user, recipient_id=contact_id
        ).filter(
            media_type__in=['image', 'video', 'audio', 'file']
        ).order_by('-timestamp')

class SharedLinksView(generics.ListAPIView):
    """
    Method: GET
    
    Description: Retrieves link messages shared between the authenticated user and a specified contact.
    
    URL Pattern: shared-links/<int:contact_id>/
    
    Permissions: Requires the user to be authenticated.
    
    Parameters:
    contact_id: The ID of the contact with whom links were shared.
    
    Response: Returns a list of link messages ordered by timestamp (most recent first).
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        contact_id = self.kwargs['contact_id']
        return Message.objects.filter(
            sender=self.request.user, recipient_id=contact_id
        ).filter(media_type='link').order_by('-timestamp')

class SharedDocsView(generics.ListAPIView):
    """
    Method: GET

    Description: Retrieves document messages shared between the authenticated 
    user and a specified contact.
    
    URL Pattern: shared-docs/<int:contact_id>/
    
    Permissions: Requires the user to be authenticated.
    
    Parameters:
    contact_id: The ID of the contact with whom documents were shared.
    
    Response: Returns a list of document messages ordered by timestamp (most recent first).
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        contact_id = self.kwargs['contact_id']
        return Message.objects.filter(
            sender=self.request.user, recipient_id=contact_id
        ).filter(media_type='document').order_by('-timestamp')
    
class StarMessageView(APIView):
    """
    Method: POST

    Description: Marks a specified message as starred by the authenticated user.
    
    URL Pattern: star-message/<int:message_id>/
    
    Permissions: Requires the user to be authenticated.
    
    Parameters:
    message_id: The ID of the message to be starred.
    
    Response:
    Success: Returns a message indicating that the message has been starred.
    Failure: Returns an error if the message is not found.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, message_id):
        """
        Mark a message as starred by the current user.
        """
        try:
            message = Message.objects.get(id=message_id)
            message.starred_by.add(request.user)
            return Response({"status": "Message starred"}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)
        
class UnstarMessageView(APIView):
    """
    Method: POST

    Description: Removes a star from a specified message for the authenticated user.
    
    URL Pattern: unstar-message/<int:message_id>/
    
    Permissions: Requires the user to be authenticated.
    
    Parameters:
    message_id: The ID of the message to unstar.
    
    Response:
    Success: Returns a message indicating that the message has been unstarred.
    Failure: Returns an error if the message is not found.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, message_id):
        """
        Remove a star from a message for the current user.
        """
        try:
            message = Message.objects.get(id=message_id)
            message.starred_by.remove(request.user)
            return Response({"status": "Message unstarred"}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

class StarredMessagesView(generics.ListAPIView):
    """
    Method: GET
    
    Description: Retrieves all messages that have been starred by the authenticated user.
    
    URL Pattern: starred-messages/
    
    Permissions: Requires the user to be authenticated.
    
    Response: Returns a list of starred messages ordered by timestamp (most recent first).
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """
        Return all the messages starred by the current user.
        """
        return Message.objects.filter(starred_by=self.request.user).order_by('-timestamp')