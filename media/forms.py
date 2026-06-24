from django import forms
from .models import Folder, MediaFile


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']

class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        # We exclude size, file_type, and user because the backend handles them
        fields = ['file', 'title', 'description', 'folder']

    def __init__(self, *args, **kwargs):
        # Extract the user from the kwargs before initializing the form
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # SECURITY: Limit the dropdown to only folders owned by this user
            self.fields['folder'].queryset = Folder.objects.filter(user=user)
        # i explicitly exclude 'user' and 'parent' because i will handle 
        # those securely in the background, out of the user's control.