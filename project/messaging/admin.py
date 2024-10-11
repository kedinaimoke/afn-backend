from django.contrib import admin
from .models import Message, Thread, Reaction

class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'recipient', 'content', 'media_type', 'timestamp', 'is_read']
    search_fields = ['content', 'sender__username', 'recipient__username']
    list_filter = ['media_type', 'timestamp', 'is_read']
    readonly_fields = ['timestamp']

class ThreadAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    filter_horizontal = ['participants']
    readonly_fields = ['created_at']

class ReactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'user', 'reaction_type']
    search_fields = ['message__content', 'user__username']
    list_filter = ['reaction_type']

admin.site.register(Message, MessageAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Reaction, ReactionAdmin)
