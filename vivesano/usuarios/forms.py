from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, limpiar_rut, validar_rut

class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ["username", "email", "rut", "tipo_cliente", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Roles que NO se pueden asignar desde el registro público
        ROLES_PROHIBIDOS = ("admin", "atencion_cliente", "empresa")

        # Filtrar choices
        self.fields["tipo_cliente"].choices = [
            (value, label) for value, label in self.fields["tipo_cliente"].choices
            if value not in ROLES_PROHIBIDOS
        ]
    
    def clean_rut(self):
        rut = self.cleaned_data.get("rut")
        if not rut:
            return rut
        rut_limpio = limpiar_rut(rut)
        # Intentamos validar; si falla, lanzamos ValidationError (aparece en el form)
        if not validar_rut(rut_limpio):
            raise forms.ValidationError("El RUT ingresado no es válido.")
        return rut_limpio