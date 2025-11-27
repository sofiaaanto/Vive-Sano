from django.shortcuts import render, redirect, get_object_or_404
from usuarios.decoradores import admin_required
from usuarios.models import Usuario
from .models import Producto
from django.contrib.auth.decorators import login_required
from .carrito import Carrito
from decimal import Decimal
from .models import Producto, Pedido, PedidoItem
from .descuentos import descuento_por_cantidad_empresa
from django.contrib import messages
from mensajeria.models import Message


@admin_required
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, "productos/listar.html", {"productos": productos})

@admin_required
def crear_producto(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        precio = request.POST.get("precio")
        stock = request.POST.get("stock")
        categoria = request.POST.get("categoria")
        descripcion = request.POST.get("descripcion")
        imagen = request.FILES.get("imagen")  # 👈 nuevo

        Producto.objects.create(
            nombre=nombre,
            precio=precio,
            stock=stock,
            categoria=categoria,
            descripcion=descripcion,
            imagen=imagen,   # 👈 nuevo
        )
        return redirect("listar_productos")

    return render(request, "productos/crear.html")

@admin_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    if request.method == "POST":
        producto.nombre = request.POST.get("nombre")
        producto.precio = request.POST.get("precio")
        producto.stock = request.POST.get("stock")
        producto.categoria = request.POST.get("categoria")
        producto.descripcion = request.POST.get("descripcion")

        # 👇 Si viene una nueva imagen, la reemplazamos
        if request.FILES.get("imagen"):
            producto.imagen = request.FILES["imagen"]

        producto.save()
        return redirect("listar_productos")

    return render(request, "productos/editar.html", {"producto": producto})

@admin_required
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    producto.delete()
    return redirect("listar_productos")

@login_required
def catalogo(request):
    """Catálogo de productos para clientes (natural / empresa)."""
    productos = Producto.objects.filter(activo=True)  # Remover: stock__gt=0
    return render(request, "productos/catalogo.html", {"productos": productos})

@login_required
def agregar_al_carrito(request, id):
    producto = get_object_or_404(Producto, id=id, activo=True)
    carrito = Carrito(request)

    if request.method == "POST":
        try:
            cantidad = int(request.POST.get("cantidad", 1))
        except ValueError:
            cantidad = 1
    else:
        cantidad = 1

    carrito.add(producto, cantidad)
    return redirect("ver_carrito")

@login_required
def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, "productos/carrito.html", {"carrito": carrito})

@login_required
def eliminar_del_carrito(request, id):
    producto = get_object_or_404(Producto, id=id)
    carrito = Carrito(request)
    carrito.remove(producto)
    return redirect("ver_carrito")

@login_required
def vaciar_carrito(request):
    carrito = Carrito(request)
    carrito.clear()
    return redirect("ver_carrito")

@login_required
def finalizar_compra(request):
    carrito = Carrito(request)

    if not carrito.cart:
        return redirect("catalogo_productos")

    es_empresa = hasattr(request.user, "es_empresa") and request.user.es_empresa()

    # Crear pedido con total 0, lo calculamos abajo
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=Decimal("0.00"),
        estado="pagado"  # simulado
    )

    total_bruto = Decimal("0.00")      # sin descuento
    total_descuento = Decimal("0.00")  # suma de descuentos
    total_final = Decimal("0.00")      # total a pagar (simulado)

    for item in carrito:
        producto = item["producto"]
        cantidad = item["cantidad"]
        precio = item["precio"]  # Decimal

        # Seguridad extra: no vender más de lo que hay
        if cantidad > producto.stock:
            cantidad = producto.stock

        if cantidad <= 0:
            continue

        # Precio sin descuento de este ítem
        subtotal_bruto = precio * cantidad

        # Descuento solo si el usuario es empresa
        descuento_pct = descuento_por_cantidad_empresa(cantidad) if es_empresa else Decimal("0.00")
        descuento_item = subtotal_bruto * descuento_pct
        subtotal_final = subtotal_bruto - descuento_item

        # Descontar stock REAL
        producto.stock -= cantidad
        producto.save()

        # Crear item del pedido guardando el precio unitario normal
        PedidoItem.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio,
        )

        total_bruto += subtotal_bruto
        total_descuento += descuento_item
        total_final += subtotal_final

    # Guardamos el total final (con descuento si aplica)
    pedido.total = total_final
    pedido.save()

    # Vaciar carrito
    carrito.clear()

    # Pasamos también totales para mostrarlos en la plantilla
    contexto = {
        "pedido": pedido,
        "total_bruto": total_bruto,
        "total_descuento": total_descuento,
        "total_final": total_final,
        "es_empresa": es_empresa,
    }

    return render(request, "productos/compra_exitosa.html", contexto)


@login_required
def solicitar_reserva(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Buscar un usuario del tipo "atencion"
    soporte = Usuario.objects.filter(tipo_cliente="atencion_cliente").first()

    if not soporte:
        messages.error(request, "No existe ningún usuario de atención al cliente.")
        return redirect("catalogo_productos")

    contenido = (
        f"📌 **Solicitud de producto**\n\n ---"
        f"Usuario: {request.user.username}\n ---"
        f"Producto ID: {producto.id}\n ---"
        f"Producto: {producto.nombre}\n ---"
        f"Solicitud enviada automáticamente a atención al cliente. ---"
    )

    Message.objects.create(
        sender=request.user,
        receiver=soporte,
        content=contenido
    )

    messages.success(request, "Tu solicitud fue enviada al equipo de atención al cliente.")
    return redirect("mensajeria:chat", user_id=soporte.id)