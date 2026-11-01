"""Rotas do projeto. Cada app tem o seu próprio urls.py."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "SyncWeb · Administração"
admin.site.site_title = "SyncWeb"
admin.site.index_title = "Painel do site"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("contato/", include("contato.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    # em desenvolvimento o Django serve os uploads (prints dos projetos)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
