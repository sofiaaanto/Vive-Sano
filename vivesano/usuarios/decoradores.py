from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def rol_requerido(roles_permitidos):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("login")

            # superusuario siempre pasa
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if user.tipo_cliente not in roles_permitidos:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    return rol_requerido(["admin"])(view_func)

def soporte_required(view_func):
    return rol_requerido(["atencion_cliente"])(view_func)

def empresa_required(view_func):
    return rol_requerido(["empresa"])(view_func)

def natural_required(view_func):
    return rol_requerido(["natural"])(view_func)
