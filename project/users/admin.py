from django.contrib import admin
from .models import Personnel

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'middle_name', 'surname', 'email', 'rank', 'arm_of_service')
    search_fields = ('first_name', 'surname', 'email', 'rank__rank_name')
    list_filter = ('rank', 'arm_of_service')
    ordering = ('surname', 'first_name')
