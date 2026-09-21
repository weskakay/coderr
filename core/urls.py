"""URL configuration for the Coderr project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Serves uploaded images while DEBUG is on.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
