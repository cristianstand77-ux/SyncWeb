import json

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import reverse
from django.views.decorators.http import require_GET

from contato.forms import PedidoOrcamentoForm
from contato.models import PedidoOrcamento
from conteudo.models import Depoimento, Pergunta, Plano, Projeto


def dados_estruturados(request):
    """JSON-LD que ajuda o Google a entender quem é a empresa."""
    base = request.build_absolute_uri("/").rstrip("/")
    dados = {
        "@context": "https://schema.org",
        "@type": "ProfessionalService",
        "name": settings.EMPRESA["nome"],
        "url": base + "/",
        "logo": base + static("img/apple-touch-icon.png"),
        "image": base + static("img/og-image.png"),
        "description": (
            "Criamos sites, sistemas de gestão e automações para empresas que querem "
            "organizar processos e vender mais pela internet."
        ),
        "areaServed": "BR",
        "knowsAbout": ["Desenvolvimento de sites", "Sistemas de gestão", "Automação de processos", "Integrações"],
    }
    if settings.EMPRESA["email"]:
        dados["email"] = settings.EMPRESA["email"]
    if settings.EMPRESA["whatsapp"]:
        dados["telephone"] = "+" + settings.EMPRESA["whatsapp"]
    redes = [settings.EMPRESA[r] for r in ("instagram", "linkedin") if settings.EMPRESA[r]]
    if redes:
        dados["sameAs"] = redes
    # "<" escapado: impede que um texto feche a tag <script> por engano
    return json.dumps(dados, ensure_ascii=False).replace("<", "\\u003c")


def contexto_home(request, form=None):
    """Tudo que a página inicial precisa. Também é usado pelo app contato
    quando o formulário volta com erro."""
    pedido_enviado = None
    pedido_id = request.session.pop("pedido_enviado", None)
    if pedido_id:
        pedido_enviado = PedidoOrcamento.objects.filter(pk=pedido_id).first()

    return {
        "planos": Plano.objects.filter(ativo=True),
        "perguntas": Pergunta.objects.filter(ativo=True),
        "projetos": Projeto.objects.filter(ativo=True),
        "depoimentos": Depoimento.objects.filter(ativo=True),
        "form": form or PedidoOrcamentoForm(),
        "pedido_enviado": pedido_enviado,
        "dados_estruturados": dados_estruturados(request),
    }


def home(request):
    return render(request, "core/home.html", contexto_home(request))


def politica_privacidade(request):
    return render(request, "core/politica_privacidade.html")


@require_GET
def robots_txt(request):
    linhas = [
        "User-agent: *",
        "Disallow: /admin/",
        "",
        "Sitemap: " + request.build_absolute_uri(reverse("core:sitemap")),
    ]
    return HttpResponse("\n".join(linhas) + "\n", content_type="text/plain; charset=utf-8")
