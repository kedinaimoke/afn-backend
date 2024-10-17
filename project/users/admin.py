from django.contrib import admin
from .models import Personnel

@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('official_name', 'email', 'rank', 'arm_of_service')
    search_fields = ('offical_name', 'email', 'rank__rank_name')
    list_filter = ('rank', 'arm_of_service')
    ordering = ('official_name',)
    list_per_page = 50
