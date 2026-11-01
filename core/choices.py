from django.db import models


class Servico(models.TextChoices):
    """Tipos de serviço. Usado nos planos (app conteudo) e no formulário (app contato)."""

    SITE = "site", "Site profissional"
    SISTEMA = "sistema", "Sistema sob medida"
    AUTOMACAO = "automacao", "Automação e integrações"
    OUTRO = "outro", "Ainda não sei, quero conversar"
