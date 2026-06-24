from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Built-in Django authentication URLs (login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Connect to our media app routing
    path('', include('media.urls')), 
]

# This serves media files locally. 
# In production on Render, WhiteNoise or a cloud bucket (S3) handles this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)