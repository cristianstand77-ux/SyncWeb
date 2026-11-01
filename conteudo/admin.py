from django.contrib import admin

from .models import Depoimento, Pergunta, Plano, Projeto


class OrdenavelAdmin(admin.ModelAdmin):
    list_editable = ["ordem", "ativo"]
    list_filter = ["ativo"]


@admin.register(Plano)
class PlanoAdmin(OrdenavelAdmin):
    list_display = ["nome", "preco", "servico", "destaque", "ordem", "ativo"]


@admin.register(Pergunta)
class PerguntaAdmin(OrdenavelAdmin):
    list_display = ["pergunta", "ordem", "ativo"]
    search_fields = ["pergunta", "resposta"]


@admin.register(Projeto)
class ProjetoAdmin(OrdenavelAdmin):
    list_display = ["cliente", "tipo", "ordem", "ativo"]
    search_fields = ["cliente", "tipo"]


@admin.register(Depoimento)
class DepoimentoAdmin(OrdenavelAdmin):
    list_display = ["nome", "cargo_empresa", "ordem", "ativo"]
