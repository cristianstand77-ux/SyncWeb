from django.test import TestCase, override_settings
from django.urls import reverse


class PaginasTests(TestCase):
    def test_home_sem_cnpj_horario_e_titulo_curto(self):
        resposta = self.client.get(reverse("core:home"))
        self.assertContains(resposta, "<title>SyncWeb Solutions</title>")
        self.assertNotContains(resposta, "CNPJ")
        self.assertNotContains(resposta, "Horário")

    def test_servicos_e_planos_desligados(self):
        with self.settings(SECAO_SERVICOS_ATIVA=False, SECAO_PLANOS_ATIVA=False):
            resposta = self.client.get(reverse("core:home"))
        self.assertNotContains(resposta, 'id="servicos"')
        self.assertNotContains(resposta, 'id="planos"')
        self.assertNotContains(resposta, 'href="#servicos"')
        self.assertNotContains(resposta, 'href="#planos"')

    @override_settings(SECAO_SERVICOS_ATIVA=True, SECAO_PLANOS_ATIVA=True)
    def test_home_mostra_planos_e_duvidas_cadastrados(self):
        resposta = self.client.get(reverse("core:home"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Sistema sob medida")  # plano criado na migração inicial
        self.assertContains(resposta, "Quanto custa um projeto?")  # dúvida criada na migração inicial
        self.assertNotContains(resposta, 'id="projetos"')  # sem projetos cadastrados, a seção some

    def test_politica_desligada_nao_aparece(self):
        with self.settings(POLITICA_PRIVACIDADE_ATIVA=False):
            self.assertEqual(self.client.get(reverse("core:politica_privacidade")).status_code, 404)
            self.assertNotContains(self.client.get(reverse("core:home")), "Política de privacidade")
            self.assertNotContains(self.client.get("/sitemap.xml"), "politica-de-privacidade")

    @override_settings(POLITICA_PRIVACIDADE_ATIVA=True)
    def test_politica_ligada(self):
        self.assertEqual(self.client.get(reverse("core:politica_privacidade")).status_code, 200)
        self.assertContains(self.client.get(reverse("core:home")), "Política de privacidade")

    def test_robots_aponta_para_o_sitemap(self):
        resposta = self.client.get("/robots.txt")
        self.assertContains(resposta, "Sitemap: http://testserver/sitemap.xml")

    def test_sitemap(self):
        self.assertContains(self.client.get("/sitemap.xml"), "<loc>http://testserver/</loc>")
