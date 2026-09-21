"""URL configuration for the Coderr project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('auth_app.api.urls')),
    path('api/', include('profile_app.api.urls')),
    path('api/', include('offers_app.api.urls')),
]

# Serves uploaded images while DEBUG is on.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
