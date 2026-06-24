from django.contrib import admin
from .models import Folder, MediaFile

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'parent', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name',)

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'folder', 'file_type', 'size', 'uploaded_at')
    list_filter = ('user', 'file_type', 'uploaded_at')
    search_fields = ('title', 'description')
    readonly_fields = ('file_type', 'size') # Prevent manual editing of calculated fields