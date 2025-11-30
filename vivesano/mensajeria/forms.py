from django import forms

class BuscarClienteForm(forms.Form):
    query = forms.CharField(
        label="Buscar cliente por RUT o username",
        max_length=50,
        required=True
    )
