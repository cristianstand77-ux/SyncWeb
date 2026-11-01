from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PaginasSitemap(Sitemap):
    """Lista as páginas públicas para o Google. O domínio vem da própria requisição."""

    changefreq = "monthly"

    def items(self):
        itens = [("core:home", 1.0)]
        if settings.POLITICA_PRIVACIDADE_ATIVA:
            itens.append(("core:politica_privacidade", 0.3))
        return itens

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]
