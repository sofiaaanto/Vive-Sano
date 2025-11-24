from django.db import models
from django.conf import settings


class Producto(models.Model):
    CATEGORIAS = [
        ("abarrotes", "Abarrotes"),
        ("bebidas", "Bebidas"),
        ("aseo", "Aseo"),
        ("lacteos", "Lácteos"),
        ("snacks", "Snacks"),
        ("otros", "Otros"),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="otros")
    activo = models.BooleanField(default=True)

    # 👇 Nuevo campo
    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
    )

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} ({self.stock} en stock)"


class Pedido(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente (sin pago real)"),
        ("pagado", "Pagado (simulado)"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")

    def __str__(self):
        return f"Pedido #{self.id} de {self.usuario.username}"


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"