from django.contrib import admin
from django.utils.html import format_html

from .models import PedidoOrcamento


@admin.register(PedidoOrcamento)
class PedidoOrcamentoAdmin(admin.ModelAdmin):
    list_display = ["nome", "empresa", "contato", "servico", "status", "criado_em"]
    list_filter = ["status", "servico", "criado_em"]
    list_editable = ["status"]
    search_fields = ["nome", "empresa", "contato", "mensagem"]
    date_hierarchy = "criado_em"
    readonly_fields = ["nome", "empresa", "contato", "servico", "mensagem", "criado_em", "responder"]
    fieldsets = [
        ("Pedido", {"fields": ["nome", "empresa", "contato", "servico", "mensagem", "criado_em", "responder"]}),
        ("Acompanhamento", {"fields": ["status", "observacoes"]}),
    ]

    @admin.display(description="responder")
    def responder(self, obj):
        valor = obj.contato
        if "@" in valor:
            return format_html('<a href="mailto:{}">Responder por e-mail</a>', valor)
        numero = "".join(c for c in valor if c.isdigit())
        if not numero.startswith("55"):
            numero = "55" + numero
        return format_html('<a href="https://wa.me/{}" target="_blank" rel="noopener">Abrir no WhatsApp</a>', numero)

    def has_add_permission(self, request):
        return False  # pedidos só chegam pelo site
