from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator

class Folder(models.Model):
    name = models.CharField(max_length=255)
    # 'self' allows a folder to be placed inside another folder (nesting)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class MediaFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files')
    
    # Security: Restrict uploads to safe extensions only
    file = models.FileField(
        upload_to='uploads/%Y/%m/', 
        validators=[FileExtensionValidator(allowed_extensions=[
            'jpg', 'jpeg', 'png', 'gif', 'pdf', 'mp4', 'docx', 'txt', 'csv'
        ])]
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_type = models.CharField(max_length=50, blank=True) 
    size = models.BigIntegerField(null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Automatically extract file size and type before saving to database
        if self.file:
            self.size = self.file.size
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the physical file off the hard drive first
        if self.file:
            self.file.delete(save=False)
        # Then delete the database record
        super().delete(*args, **kwargs) 