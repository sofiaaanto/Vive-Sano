from django.contrib.auth.models import AbstractUser
from django.db import models
import re

def limpiar_rut(rut: str) -> str:
    return rut.replace(".", "").replace(" ", "").upper()

def calcular_dv(numero: str) -> str:
    reversed_digits = map(int, reversed(numero))
    factores = [2, 3, 4, 5, 6, 7]
    suma = 0
    i = 0
    for d in reversed_digits:
        suma += d * factores[i]
        i = (i + 1) % len(factores)
    resto = suma % 11
    dv_calc = 11 - resto
    if dv_calc == 11:
        return "0"
    if dv_calc == 10:
        return "K"
    return str(dv_calc)

def validar_rut(rut: str) -> bool:
    rut = limpiar_rut(rut)
    if not re.match(r"^\d+-[\dK]$", rut):
        return False
    num, dv = rut.split("-")
    return calcular_dv(num) == dv


class Usuario(AbstractUser):
    TIPO_CLIENTE = [
        ("natural", "Persona Natural"),
        ("empresa", "Empresa"),
        ("admin", "Administrador"),
        ("soporte", "Atención al Cliente"),
    ]

    rut = models.CharField(max_length=12, unique=True, blank=True, null=True)
    tipo_cliente = models.CharField(
        max_length=20,
        choices=TIPO_CLIENTE,
        default="natural"
    )

    def save(self, *args, **kwargs):
        if self.rut:
            if not validar_rut(self.rut):
                raise ValueError("El RUT ingresado no es válido.")
            self.rut = limpiar_rut(self.rut)

        if self.is_superuser and not self.tipo_cliente:
            self.tipo_cliente = "admin"

        super().save(*args, **kwargs)

    def __str__(self):
        if self.rut:
            return f"{self.username} ({self.rut})"
        return self.username

    def es_empresa(self):
        return self.tipo_cliente == "empresa"

    def es_natural(self):
        return self.tipo_cliente == "natural"

    def es_admin(self):
        return self.tipo_cliente == "admin"

    def es_soporte(self):
        return self.tipo_cliente == "soporte"
