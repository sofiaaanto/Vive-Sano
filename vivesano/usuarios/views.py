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
            form.save()
            messages.success(request, "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            return redirect("login")
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
