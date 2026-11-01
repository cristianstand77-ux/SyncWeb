from urllib.parse import quote

from django.conf import settings


def site(request):
    """Deixa os dados da empresa disponíveis em todos os templates como {{ empresa }}."""
    empresa = dict(settings.EMPRESA)
    numero = empresa["whatsapp"]
    empresa["whatsapp_link"] = (
        f"https://wa.me/{numero}?text="
        + quote("Olá! Vim pelo site da SyncWeb e gostaria de um orçamento.")
        if numero
        else ""
    )
    return {
        "empresa": empresa,
        "plausible_domain": settings.PLAUSIBLE_DOMAIN,
        "politica_ativa": settings.POLITICA_PRIVACIDADE_ATIVA,
    }
