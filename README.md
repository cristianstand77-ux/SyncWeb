# SyncWeb Solutions: site

Site institucional em Django 6.1 (Python 3.14).

## Estrutura

```
Sync/          configurações do projeto (settings.py, urls.py)
core/          páginas, SEO (sitemap.xml, robots.txt), dados da empresa nos templates
conteudo/      planos, dúvidas, projetos e depoimentos (editáveis no /admin)
contato/       formulário de orçamento: salva o pedido e avisa por e-mail
templates/     HTML (base.html, core/home.html, 404.html...)
static/        CSS, JS, three.js, fontes e imagens
```

## Rodar no computador

```bash
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # cria o seu login do /admin
python manage.py runserver
```

Site: http://127.0.0.1:8000 · Painel: http://127.0.0.1:8000/admin

As configurações ficam no arquivo `.env` (modelo completo em `.env.example`).

## Testes

```bash
python manage.py test
```

## Publicar (produção)

1. Copie `.env.example` para `.env` no servidor e preencha (chave nova, `DJANGO_DEBUG=False`, domínio, WhatsApp, e-mail).
2. `pip install -r requirements.txt gunicorn`
3. `python manage.py migrate`
4. `python manage.py collectstatic --noinput` (com o `.env` de produção, ou seja, DEBUG=False)
5. Rode com `gunicorn Sync.wsgi` atrás de HTTPS.
6. Faça backup do `db.sqlite3` e da pasta `media/` (pedidos e prints dos projetos).
