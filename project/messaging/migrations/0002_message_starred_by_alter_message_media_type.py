# Generated by Django 5.1.1 on 2024-10-11 11:28

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='starred_by',
            field=models.ManyToManyField(blank=True, related_name='starred_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='media_type',
            field=models.CharField(blank=True, choices=[('text', 'Text'), ('image', 'Image'), ('video', 'Video'), ('file', 'File'), ('audio', 'Audio'), ('link', 'Link'), ('document', 'Document')], max_length=10, null=True),
        ),
    ]
