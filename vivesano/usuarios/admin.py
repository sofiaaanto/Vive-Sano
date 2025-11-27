from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
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

    # Evitar que usuarios que NO son superusuarios cambien el tipo de cliente
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ("tipo_cliente",)
        return ()

    # Control de guardado: solo superusuario puede asignar tipos especiales
    def save_model(self, request, obj, form, change):
        if obj.tipo_cliente in ("admin", "atencion_cliente") and not request.user.is_superuser:
            raise PermissionDenied("Solo el superusuario puede asignar este tipo de usuario.")
        super().save_model(request, obj, form, change)
