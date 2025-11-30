from django.forms import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .forms import RegistroForm
from .decoradores import admin_required

def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                # Intentamos guardar el usuario. Si el modelo lanza ValidationError
                # (por ej. rut inválido) lo capturamos y mostramos en el form.
                form.save()
                # Si quieres enviar mensaje:
                # messages.success(request, "Cuenta creada correctamente.")
                return redirect("login")
            except ValidationError as e:
                # e puede ser ValidationError con message_dict o message
                # Normalizamos y añadimos los errores correspondientes al formulario.

                # Si trae message_dict (ej. {"rut": ["msg"]}), lo usamos:
                if hasattr(e, "message_dict"):
                    for field, msgs in e.message_dict.items():
                        for m in msgs:
                            form.add_error(field, m)
                else:
                    # Mensaje genérico
                    msg = "El RUT ingresado no es válido."
                    form.add_error("rut", msg)
        # si form no es válido, se renderiza nuevamente con errores (incluido rut)
    else:
        form = RegistroForm()

    return render(request, "usuarios/registrar.html", {"form": form})
@login_required
def dashboard(request):
    usuario = request.user
    return render(request, "usuarios/dashboard.html", {"usuario": usuario})

@admin_required
def admin_panel(request):
    return render(request, "usuarios/admin_panel.html")

def logout_view(request):
    logout(request)
    return redirect("login")
