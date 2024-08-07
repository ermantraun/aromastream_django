from django.contrib import admin
from .models import Video, TimeStamp, ChangeRequest

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'views')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')

@admin.register(TimeStamp)
class TimeStampAdmin(admin.ModelAdmin):
    list_display = ('video', 'aroma', 'moment')
    search_fields = ('video__title', 'aroma')
    list_filter = ('aroma',)

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'field', 'created_at')
    search_fields = ('user__username', 'field')
    list_filter = ('created_at',)