from django.test import TestCase, override_settings
from django.urls import reverse

from .models import PedidoOrcamento

DADOS = {
    "nome": "Maria",
    "empresa": "Loja da Maria",
    "contato": "(11) 98765-4321",
    "servico": "site",
    "mensagem": "Preciso de um site para a minha loja.",
}


@override_settings(CONTATO_DESTINATARIOS=["equipe@exemplo.com"])
class FormularioTests(TestCase):
    def test_pedido_valido_e_salvo_e_mostra_confirmacao(self):
        resposta = self.client.post(reverse("contato:enviar"), DADOS, follow=True)
        self.assertEqual(PedidoOrcamento.objects.count(), 1)
        self.assertContains(resposta, "Recebemos o seu pedido, Maria!")

    def test_aviso_por_email(self):
        from django.core import mail

        self.client.post(reverse("contato:enviar"), DADOS)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Maria", mail.outbox[0].subject)

    def test_campos_obrigatorios(self):
        resposta = self.client.post(reverse("contato:enviar"), {**DADOS, "nome": ""})
        self.assertEqual(resposta.status_code, 400)
        self.assertEqual(PedidoOrcamento.objects.count(), 0)
        self.assertContains(resposta, 'aria-invalid="true"', status_code=400)

    def test_contato_invalido(self):
        resposta = self.client.post(reverse("contato:enviar"), {**DADOS, "contato": "123"})
        self.assertContains(resposta, "WhatsApp com DDD", status_code=400)

    def test_robo_de_spam_e_ignorado(self):
        self.client.post(reverse("contato:enviar"), {**DADOS, "site": "http://spam.com"})
        self.assertEqual(PedidoOrcamento.objects.count(), 0)

    def test_get_nao_e_permitido(self):
        self.assertEqual(self.client.get(reverse("contato:enviar")).status_code, 405)
