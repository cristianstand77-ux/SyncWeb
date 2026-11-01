from django.db import models

from core.choices import Servico


class Ordenavel(models.Model):
    """Campos comuns: ordem de exibição e se aparece no site."""

    ordem = models.PositiveIntegerField("ordem", default=0, help_text="Menor aparece primeiro.")
    ativo = models.BooleanField("aparece no site", default=True)

    class Meta:
        abstract = True
        ordering = ["ordem", "pk"]


class Plano(Ordenavel):
    nome = models.CharField("nome", max_length=80)
    resumo = models.CharField("resumo", max_length=160)
    preco = models.CharField("preço", max_length=40, default="Sob consulta", help_text='Ex.: "Sob consulta" ou "a partir de R$ 1.500".')
    itens = models.TextField("o que inclui", help_text="Um item por linha.")
    servico = models.CharField(
        "serviço", max_length=20, choices=Servico.choices, help_text="Já vem marcado no formulário quando clicam no botão."
    )
    texto_botao = models.CharField("texto do botão", max_length=40, default="Pedir orçamento")
    destaque = models.BooleanField("destacar", default=False, help_text="Card com borda verde e botão cheio.")

    class Meta(Ordenavel.Meta):
        verbose_name = "plano"
        verbose_name_plural = "planos"

    def __str__(self):
        return self.nome

    @property
    def lista_itens(self):
        return [linha.strip() for linha in self.itens.splitlines() if linha.strip()]


class Pergunta(Ordenavel):
    pergunta = models.CharField("pergunta", max_length=160)
    resposta = models.TextField("resposta")

    class Meta(Ordenavel.Meta):
        verbose_name = "dúvida frequente"
        verbose_name_plural = "dúvidas frequentes"

    def __str__(self):
        return self.pergunta


class Projeto(Ordenavel):
    """Portfólio. A seção só aparece no site quando existe pelo menos um projeto ativo."""

    cliente = models.CharField("cliente / projeto", max_length=100)
    tipo = models.CharField("tipo", max_length=60, help_text="Ex.: Site institucional, Sistema de gestão.")
    problema = models.TextField("problema", help_text="O que o cliente precisava.")
    resultado = models.TextField("resultado", help_text="O que mudou depois do projeto.")
    imagem = models.ImageField("print", upload_to="projetos/", blank=True, help_text="Ideal: 1600×1000 px.")
    descricao_imagem = models.CharField("descrição do print", max_length=160, blank=True, help_text="Para leitores de tela e Google.")
    link = models.URLField("link do projeto", blank=True)

    class Meta(Ordenavel.Meta):
        verbose_name = "projeto"
        verbose_name_plural = "projetos (portfólio)"

    def __str__(self):
        return self.cliente


class Depoimento(Ordenavel):
    """Só publique com autorização do cliente. A seção só aparece com pelo menos um ativo."""

    nome = models.CharField("nome", max_length=80)
    cargo_empresa = models.CharField("cargo e empresa", max_length=120, blank=True)
    texto = models.TextField("depoimento")

    class Meta(Ordenavel.Meta):
        verbose_name = "depoimento"
        verbose_name_plural = "depoimentos"

    def __str__(self):
        return f"{self.nome} ({self.cargo_empresa})" if self.cargo_empresa else self.nome
