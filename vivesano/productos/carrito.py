from decimal import Decimal
from .models import Producto

class Carrito:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("carrito")
        if not cart:
            cart = self.session["carrito"] = {}
        self.cart = cart

    def add(self, producto: Producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id not in self.cart:
            self.cart[producto_id] = {
                "cantidad": 0,
                "precio": str(producto.precio),  # guardamos como string
                "nombre": producto.nombre,
            }
        self.cart[producto_id]["cantidad"] += cantidad
        # no dejar que pase el stock
        if self.cart[producto_id]["cantidad"] > producto.stock:
            self.cart[producto_id]["cantidad"] = producto.stock
        self.save()

    def remove(self, producto: Producto):
        producto_id = str(producto.id)
        if producto_id in self.cart:
            del self.cart[producto_id]
            self.save()

    def clear(self):
        self.session["carrito"] = {}
        self.session.modified = True

    def save(self):
        self.session["carrito"] = self.cart
        self.session.modified = True

    def __iter__(self):
        """Permite iterar el carrito en las plantillas."""
        producto_ids = self.cart.keys()
        productos = Producto.objects.filter(id__in=producto_ids)
        for producto in productos:
            item = self.cart[str(producto.id)].copy()
            item["producto"] = producto
            item["precio"] = Decimal(item["precio"])
            item["subtotal"] = item["precio"] * item["cantidad"]
            yield item

    def total(self):
        from decimal import Decimal
        return sum(
            Decimal(item["precio"]) * item["cantidad"]
            for item in self.cart.values()
        )
