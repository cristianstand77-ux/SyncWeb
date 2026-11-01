"""Cadastra os planos e as dúvidas que estavam fixos no HTML do site estático.
Depois disso, tudo pode ser editado pelo admin."""

from django.db import migrations

PLANOS = [
    {
        "ordem": 1,
        "nome": "Site profissional",
        "resumo": "Para quem precisa ser encontrado e passar confiança na internet.",
        "itens": "Site institucional ou página de vendas\nAdaptado para celular, tablet e computador\n"
        "Otimizado para aparecer no Google\nBotão de WhatsApp e formulário de contato",
        "servico": "site",
        "texto_botao": "Quero um site",
        "destaque": False,
    },
    {
        "ordem": 2,
        "nome": "Sistema sob medida",
        "resumo": "Para organizar clientes, vendas e operação num só lugar.",
        "itens": "Cadastro de clientes, pedidos, estoque ou agenda\nPainel com relatórios do seu negócio\n"
        "Acesso com login para a sua equipe\nTreinamento para começar a usar",
        "servico": "sistema",
        "texto_botao": "Quero um sistema",
        "destaque": True,
    },
    {
        "ordem": 3,
        "nome": "Automação e integrações",
        "resumo": "Para acabar com tarefas repetitivas e retrabalho.",
        "itens": "Mapeamento do processo atual\nAutomação de tarefas manuais\n"
        "Integração entre planilhas, sistemas e lojas virtuais\nAcompanhamento após a implantação",
        "servico": "automacao",
        "texto_botao": "Quero automatizar",
        "destaque": False,
    },
]

PERGUNTAS = [
    ("Quanto custa um projeto?",
     "Depende do tamanho e do que precisa ser feito. Depois de uma conversa rápida, enviamos uma proposta com "
     "valor fechado. O orçamento é gratuito e sem compromisso."),
    ("Quanto tempo leva?",
     "Um site costuma levar poucas semanas. Sistemas e automações variam conforme o escopo. O prazo vai escrito "
     "na proposta, antes de começarmos."),
    ("Vocês cuidam da hospedagem e do domínio?",
     "Sim. Ajudamos a registrar o domínio, contratar a hospedagem e deixamos tudo configurado. Você não precisa "
     "entender de tecnologia."),
    ("E depois que o projeto fica pronto?",
     "Oferecemos suporte e manutenção para correções, atualizações e melhorias. Você escolhe se quer um "
     "acompanhamento mensal ou chamar só quando precisar."),
    ("O site ou sistema fica no meu nome?",
     "Sim. O domínio, as contas e o projeto ficam registrados em nome da sua empresa. Você não fica preso a nós."),
    ("Atendem empresas de outras cidades?",
     "Sim. Todo o trabalho pode ser feito a distância, por videochamada e WhatsApp."),
]


def criar(apps, schema_editor):
    Plano = apps.get_model("conteudo", "Plano")
    Pergunta = apps.get_model("conteudo", "Pergunta")
    for dados in PLANOS:
        Plano.objects.create(**dados)
    for i, (pergunta, resposta) in enumerate(PERGUNTAS, start=1):
        Pergunta.objects.create(ordem=i, pergunta=pergunta, resposta=resposta)


def apagar(apps, schema_editor):
    apps.get_model("conteudo", "Plano").objects.filter(nome__in=[p["nome"] for p in PLANOS]).delete()
    apps.get_model("conteudo", "Pergunta").objects.filter(pergunta__in=[p for p, _ in PERGUNTAS]).delete()


class Migration(migrations.Migration):
    dependencies = [("conteudo", "0001_initial")]
    operations = [migrations.RunPython(criar, apagar)]
