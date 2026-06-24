from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('folder/create/', views.create_folder, name='create_folder'),
    path('upload/', views.upload_file, name='upload_file'),
    path('file/<int:pk>/', views.file_detail, name='file_detail'),
    path('folder/<int:pk>/', views.folder_detail, name='folder_detail'),
    #delete routes
    path('file/<int:pk>/delete/', views.delete_file, name='delete_file'),
    path('folder/<int:pk>/delete/', views.delete_folder, name='delete_folder'),
    #search route
    path('search/', views.search, name='search'),
]