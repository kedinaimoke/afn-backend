from rest_framework import serializers
from .models import Message, Thread, Reaction
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Purpose: Defines a serializer for the User model.
    
    Functionality: Converts User objects into a JSON representation 
    suitable for transmission over the wire.
    
    Fields:
    id: The unique identifier of the user.
    username: The username of the user.
    """
    class Meta:
        model = User
        fields = ['id', 'username']

class MessageSerializer(serializers.ModelSerializer):
    """
    Purpose: Defines a serializer for the Message model.
    
    Functionality: Converts Message objects into a JSON representation suitable for transmission over the wire.
    
    Fields:
    id: The unique identifier of the message.
    sender: A nested serializer for the User object representing the sender of the message.
    recipient: A nested serializer for the User object representing the recipient of the message.
    content: The text content of the message.
    media_type: The type of media attached to the message (e.g., "image", "video").
    media_url: The URL of the media file attached to the message.
    is_read: Indicates whether the message has been read by the recipient.
    timestamp: The timestamp when the message was sent.
    """
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    is_starred = serializers.SerializerMethodField()
    
    media_url = serializers.URLField(required=False)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'media_type', 'media_url', 'is_read', 'timestamp']
        read_only_fields = ['sender', 'recipient', 'timestamp']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'recipient' in validated_data and validated_data['recipient'] != self.context['request'].user:
            raise serializers.ValidationError("You do not have permission to modify this message.")
        
        instance.content = validated_data.get('content', instance.content)
        instance.media_type = validated_data.get('media_type', instance.media_type)
        instance.media_url = validated_data.get('media_url', instance.media_url)
        instance.is_read = validated_data.get('is_read', instance.is_read)
        instance.save()
        return instance
    
    def get_is_starred(self, obj):
        request = self.context.get('request')
        if request:
            return request.user in obj.starred_by.all()
        return False

class ThreadSerializer(serializers.ModelSerializer):
    """
    Purpose: Defines a serializer for the Thread model.

    Functionality: Converts Thread objects into a JSON representation suitable 
    for transmission over the wire.
    
    Fields:
    id: The unique identifier of the thread.
    participants: A list of nested serializers for the User objects involved in the thread.
    created_at: The timestamp when the thread was created.
    name: The name of the thread.
    """
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'participants', 'created_at', 'name']

class ReactionSerializer(serializers.ModelSerializer):
    """
    Purpose: Defines a serializer for the Reaction model.

    Functionality: Converts Reaction objects into a JSON representation suitable 
    for transmission over the wire.
    
    Fields:
    id: The unique identifier of the reaction.
    message: A nested serializer for the Message object that the reaction is associated with.
    user: A nested serializer for the User object who created the reaction.
    reaction_type: The type of reaction (e.g., "like")
    """
    class Meta:
        model = Reaction
        fields = ['id', 'message', 'user', 'reaction_type']
