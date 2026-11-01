import logging

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from core.views import contexto_home

from .forms import PedidoOrcamentoForm

logger = logging.getLogger(__name__)


def avisar_por_email(request, pedido):
    if not settings.CONTATO_DESTINATARIOS:
        return
    link_admin = request.build_absolute_uri(reverse("admin:contato_pedidoorcamento_change", args=[pedido.pk]))
    corpo = (
        f"Novo pedido de orçamento pelo site.\n\n"
        f"Nome: {pedido.nome}\n"
        f"Empresa: {pedido.empresa or '-'}\n"
        f"Contato: {pedido.contato}\n"
        f"Serviço: {pedido.get_servico_display()}\n\n"
        f"{pedido.mensagem}\n\n"
        f"Ver no painel: {link_admin}\n"
    )
    try:
        send_mail(f"Novo pedido: {pedido.nome}", corpo, None, settings.CONTATO_DESTINATARIOS)
    except Exception:
        # o pedido já está salvo; uma falha no e-mail não pode quebrar o site
        logger.exception("Falha ao enviar o aviso do pedido %s por e-mail", pedido.pk)


@require_POST
def enviar(request):
    form = PedidoOrcamentoForm(request.POST)

    if form.eh_spam():
        # finge que deu certo para o robô não tentar de novo
        return redirect(reverse("core:home") + "#contato")

    if not form.is_valid():
        # mostra a página de novo com os erros (o "#contato" no action leva até o formulário)
        return render(request, "core/home.html", contexto_home(request, form=form), status=400)

    pedido = form.save()
    avisar_por_email(request, pedido)
    request.session["pedido_enviado"] = pedido.pk
    return redirect(reverse("core:home") + "#contato")
