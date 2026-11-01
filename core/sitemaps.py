from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PaginasSitemap(Sitemap):
    """Lista as páginas públicas para o Google. O domínio vem da própria requisição."""

    changefreq = "monthly"

    def items(self):
        return [("core:home", 1.0), ("core:politica_privacidade", 0.3)]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]
