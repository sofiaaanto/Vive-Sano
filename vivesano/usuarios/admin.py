from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que se muestran en la tabla de lista
    list_display = ("username", "email", "rut", "tipo_cliente", "is_staff", "is_superuser")
    list_filter = ("tipo_cliente", "is_staff", "is_superuser", "is_active")

    # Campos extra que agregamos al formulario del admin
    fieldsets = UserAdmin.fieldsets + (
        ("Datos adicionales", {"fields": ("rut", "tipo_cliente")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("rut", "tipo_cliente")}),
    )
