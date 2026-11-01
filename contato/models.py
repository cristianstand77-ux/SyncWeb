from urllib.parse import quote

from django.conf import settings
from django.db import models

from core.choices import Servico


class PedidoOrcamento(models.Model):
    """Cada envio do formulário do site vira um pedido, visível no admin."""

    class Status(models.TextChoices):
        NOVO = "novo", "Novo"
        EM_CONVERSA = "conversa", "Em conversa"
        PROPOSTA = "proposta", "Proposta enviada"
        FECHADO = "fechado", "Fechado"
        PERDIDO = "perdido", "Não fechou"

    nome = models.CharField("nome", max_length=100)
    empresa = models.CharField("empresa", max_length=100, blank=True)
    contato = models.CharField("WhatsApp ou e-mail", max_length=120)
    servico = models.CharField("serviço", max_length=20, choices=Servico.choices)
    mensagem = models.TextField("mensagem", max_length=3000)

    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.NOVO)
    observacoes = models.TextField("anotações internas", blank=True)
    criado_em = models.DateTimeField("recebido em", auto_now_add=True)

    class Meta:
        verbose_name = "pedido de orçamento"
        verbose_name_plural = "pedidos de orçamento"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.nome} · {self.get_servico_display()}"

    def texto_whatsapp(self):
        linhas = [
            "Olá! Acabei de enviar um pedido pelo site da SyncWeb.",
            "",
            f"*Nome:* {self.nome}",
        ]
        if self.empresa:
            linhas.append(f"*Empresa:* {self.empresa}")
        linhas += [f"*Preciso de:* {self.get_servico_display()}", "", self.mensagem]
        return "\n".join(linhas)

    def link_whatsapp(self):
        """Link para o cliente continuar a conversa no WhatsApp da empresa."""
        numero = settings.EMPRESA["whatsapp"]
        return f"https://wa.me/{numero}?text={quote(self.texto_whatsapp())}" if numero else ""
