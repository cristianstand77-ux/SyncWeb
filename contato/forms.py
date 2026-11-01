from django import forms

from .models import PedidoOrcamento


class PedidoOrcamentoForm(forms.ModelForm):
    # "pega-robô": campo escondido. Pessoas não veem; robôs de spam preenchem.
    site = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = PedidoOrcamento
        fields = ["nome", "empresa", "contato", "servico", "mensagem"]
        labels = {
            "nome": "Seu nome",
            "empresa": "Empresa",
            "contato": "WhatsApp ou e-mail",
            "servico": "O que você precisa?",
            "mensagem": "Conte um pouco sobre o projeto",
        }
        widgets = {
            "nome": forms.TextInput(attrs={"autocomplete": "name"}),
            "empresa": forms.TextInput(attrs={"autocomplete": "organization"}),
            "contato": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "(11) 99999-9999"}),
            "mensagem": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("auto_id", "f-%s")  # ids f-nome, f-servico... (usados pelo script.js)
        super().__init__(*args, **kwargs)
        self.fields["servico"].choices = [("", "Escolha uma opção")] + list(self.fields["servico"].choices)[1:]

    def full_clean(self):
        super().full_clean()
        # marca os campos com erro (borda vermelha e aviso para leitores de tela)
        for nome in self.errors:
            if nome in self.fields:
                self.fields[nome].widget.attrs["aria-invalid"] = "true"

    def eh_spam(self):
        return bool(self.data.get("site"))

    def clean_contato(self):
        valor = self.cleaned_data["contato"].strip()
        digitos = sum(c.isdigit() for c in valor)
        if "@" not in valor and digitos < 10:
            raise forms.ValidationError("Informe um WhatsApp com DDD ou um e-mail válido.")
        return valor
