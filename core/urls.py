from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import PaginasSitemap

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("politica-de-privacidade/", views.politica_privacidade, name="politica_privacidade"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": {"paginas": PaginasSitemap}}, name="sitemap"),
]
