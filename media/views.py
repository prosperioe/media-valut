from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Folder, MediaFile
from .forms import FolderForm, MediaFileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404
import os

def register(request):
    # If a logged-in user tries to visit the register page, redirect them
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after successful registration
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome to MediaVault, {user.username}.")
            return redirect('dashboard')
    else:
        form = UserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    # STRICT ISOLATION: Only fetch root folders and files belonging to the logged-in user.
    # parent__isnull=True ensures i only see top-level folders, not folders inside folders.
    folders = Folder.objects.filter(user=request.user, parent__isnull=True)
    files = MediaFile.objects.filter(user=request.user, folder__isnull=True)
    
    return render(request, 'media/dashboard.html', {
        'folders': folders,
        'files': files
    })

@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            # commit=False pauses the save so i can attach the user securely
            folder = form.save(commit=False)
            folder.user = request.user 
            folder.save()
            messages.success(request, f"Folder '{folder.name}' created.")
            return redirect('dashboard')
    else:
        form = FolderForm()
        
    return render(request, 'media/folder_form.html', {'form': form})


@login_required
def upload_file(request):
    if request.method == 'POST':
        # CRUCIAL: request.FILES is required to parse uploaded binary data
        form = MediaFileForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            media_file = form.save(commit=False)
            media_file.user = request.user
            
            # HARD LIMIT: 10MB maximum file size (10 * 1024 * 1024 bytes)
            if media_file.file.size > 10485760: 
                messages.error(request, "Upload failed: File size exceeds the 10MB limit.")
                return render(request, 'media/upload_form.html', {'form': form})

            media_file.save()
            messages.success(request, f"File '{media_file.title}' secured in the vault.")
            return redirect('dashboard')
    else:
        form = MediaFileForm(user=request.user)
        
    return render(request, 'media/upload_form.html', {'form': form})


@login_required
def file_detail(request, pk):
    # STRICT ISOLATION: Fetch the file ONLY if the logged-in user owns it.
    media_file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    
    return render(request, 'media/file_detail.html', {'file': media_file})

@login_required
def folder_detail(request, pk):
    # STRICT ISOLATION: Fetch the folder ONLY if the logged-in user owns it.
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    
    # Fetch contents that belong to THIS specific folder
    subfolders = Folder.objects.filter(user=request.user, parent=folder)
    files = MediaFile.objects.filter(user=request.user, folder=folder)
    
    return render(request, 'media/folder_detail.html', {
        'folder': folder,
        'subfolders': subfolders,
        'files': files
    })

@login_required
def delete_file(request, pk):
    media_file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Bypassing VS Code strict typing using getattr()
        target_folder_id = getattr(media_file, 'folder_id', None)
        
        media_file.delete() 
        messages.success(request, f"File '{media_file.title}' permanently deleted.")
        
        if target_folder_id:
            return redirect('folder_detail', pk=target_folder_id)
        return redirect('dashboard')
        
    return render(request, 'media/confirm_delete.html', {'item': media_file, 'type': 'File'})

@login_required
def delete_folder(request, pk):
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Bypassing VS Code strict typing using getattr()
        target_parent_id = getattr(folder, 'parent_id', None)
        
        folder.delete()
        messages.success(request, f"Folder '{folder.name}' and all its contents destroyed.")
        
        if target_parent_id:
            return redirect('folder_detail', pk=target_parent_id)
        return redirect('dashboard')
        
    return render(request, 'media/confirm_delete.html', {'item': folder, 'type': 'Folder'})

@login_required
def search(request):
    # i used .get('q') because search forms submit data via the URL (GET request)
    query = request.GET.get('q', '').strip()
    
    files = []
    folders = []
    
    if query:
        # Search Folders: Name matches query AND belongs to user
        folders = Folder.objects.filter(
            name__icontains=query, 
            user=request.user
        )
        
        # Search Files: Title OR Description matches query AND belongs to user
        files = MediaFile.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            user=request.user
        )
        
    return render(request, 'media/search_results.html', {
        'query': query,
        'folders': folders,
        'files': files
    })

@login_required
def secure_download(request, pk):
    #STRICT SECURITY: Verify the file belongs to the logged-in user
    media_file = get_object_or_404(MediaFile, pk=pk, user=request.user)
    
    # Get the physical path on the hard drive
    file_path = media_file.file.path
    
    #Check if the physical file actually exists
    if os.path.exists(file_path):
        # FileResponse efficiently streams the file in chunks to save memory
        return FileResponse(open(file_path, 'rb'))
    else:
        raise Http404("The file could not be found on the server.")