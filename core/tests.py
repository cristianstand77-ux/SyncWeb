from django.test import TestCase
from django.urls import reverse


class PaginasTests(TestCase):
    def test_home_mostra_planos_e_duvidas_cadastrados(self):
        resposta = self.client.get(reverse("core:home"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Sistema sob medida")  # plano criado na migração inicial
        self.assertContains(resposta, "Quanto custa um projeto?")  # dúvida criada na migração inicial
        self.assertNotContains(resposta, 'id="projetos"')  # sem projetos cadastrados, a seção some

    def test_politica_de_privacidade(self):
        self.assertEqual(self.client.get(reverse("core:politica_privacidade")).status_code, 200)

    def test_robots_aponta_para_o_sitemap(self):
        resposta = self.client.get("/robots.txt")
        self.assertContains(resposta, "Sitemap: http://testserver/sitemap.xml")

    def test_sitemap(self):
        resposta = self.client.get("/sitemap.xml")
        self.assertContains(resposta, "<loc>http://testserver/politica-de-privacidade/</loc>")
