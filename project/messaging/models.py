from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Message(models.Model):
    """
    Represents a message sent between two users.

    Fields:
        - sender: The user who sent the message.
        - recipient: The user who received the message.
        - content: The text content of the message (optional).
        - media_type: The type of media attached to the message (optional).
        - media_url: The URL of the media attached to the message (optional).
        - is_read: Indicates if the recipient has read the message.
        - timestamp: The timestamp when the message was sent.
        - starred_by: The users who have starred (marked) the message.
    """
    MEDIA_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('audio', 'Audio'),
        ('link', 'Link'),
        ('document', 'Document'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    starred_by = models.ManyToManyField(User, related_name='starred_messages', blank=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.recipient}"

class Thread(models.Model):
    """
    Represents a conversation thread between multiple users.

    Fields:
        - name: An optional name for the thread.
        - participants: The users involved in the thread.
        - created_at: The timestamp when the thread was created.
    """
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name='threads')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thread {' '.join(str(participant) for participant in self.participants.all())} ({self.name or 'Group Chat'})"

class Reaction(models.Model):
    """
    Represents a reaction to a message.

    Fields:
        - message: The message being reacted to.
        - user: The user who added the reaction.
        - reaction_type: The type of reaction (e.g. like).
        - timestamp: The timestamp when the reaction was added.
    """
    message = models.ForeignKey(Message, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
