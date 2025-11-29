from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class UsernameOrRutBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):

        # Permitir login con username O con RUT
        try:
            user = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            try:
                user = Usuario.objects.get(rut=username)
            except Usuario.DoesNotExist:
                return None

        if user.check_password(password):
            return user

        return None
