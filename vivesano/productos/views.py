from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from usuarios.decoradores import admin_required
from usuarios.models import Usuario
from django.contrib.auth.decorators import login_required
from .carrito import Carrito
from decimal import Decimal
from .models import Producto, Pedido, PedidoItem
from .descuentos import descuento_por_cantidad_empresa
from django.contrib import messages
from mensajeria.models import Message
from django.db.models import Sum

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
        imagen = request.FILES.get("imagen")  

        Producto.objects.create(
            nombre=nombre,
            precio=precio,
            stock=stock,
            categoria=categoria,
            descripcion=descripcion,
            imagen=imagen,   
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


        if request.FILES.get("imagen"):
            producto.imagen = request.FILES["imagen"]

        producto.save()
        return redirect("listar_productos")

    return render(request, "productos/editar.html", {"producto": producto})

@admin_required
def eliminar_producto(request, id):
    try:
        producto = get_object_or_404(Producto, id=id)
        if producto.stock > 0:
            messages.error(request, "No se puede eliminar un producto con stock disponible.")
            return redirect("listar_productos")
        else:
            producto.delete()
            return redirect("listar_productos")
    except Exception as e:
        messages.error(request, f"Error al eliminar el producto: {e}")
        return redirect("listar_productos")


def catalogo(request):
    """Catálogo de productos para clientes (natural / empresa)."""
    productos = Producto.objects.filter(activo=True)  
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
    total_final = Decimal("0.00")      # total a pagar 

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
def solicitar_reembolso(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    # Buscar un usuario del tipo "atencion" de forma aleatoria
    soporte = Usuario.objects.filter(tipo_cliente="atencion_cliente").order_by('?').first()

    if not soporte:
        messages.error(request, "No existe ningún usuario de atención al cliente.")
        return redirect("mis_pedidos")

    contenido = (
        f"📌 **Solicitud de reembolso**\n\n ---"
        f"Usuario: {request.user.username}\n ---"
        f"Pedido ID: {pedido.id}\n ---"
        f"Total: ${pedido.total}\n ---"
        f"Solicitud enviada automáticamente a atención al cliente. ---"
    )

    Message.objects.create(
        sender=request.user,
        receiver=soporte,
        content=contenido
    )

    messages.success(request, "Tu solicitud de reembolso fue enviada al equipo de atención al cliente.")
    return redirect("mensajeria:chat", user_id=soporte.id)

@login_required
def solicitar_reserva(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    # Buscar un usuario del tipo "atencion" de forma aleatoria
    soporte = Usuario.objects.filter(tipo_cliente="atencion_cliente").order_by('?').first()

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

@login_required
def ver_estado_pedido(request, pedido_id):
    """
    Vista para que un usuario vea el estado y detalle de un pedido que ya realizó.
    No altera la lógica de finalizar_compra.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    items = PedidoItem.objects.filter(pedido=pedido)

    context = {
        "pedido": pedido,
        "items": items,
    }

    return render(request, "productos/pedido_detalle.html", context)

@login_required
def mis_pedidos(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by("-creado")
    return render(request, "productos/mis_pedidos.html", {"pedidos": pedidos})

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    if pedido.estado != "pagado":
        messages.error(request, "Solo se pueden cancelar pedidos en estado 'pagado'.")
        return redirect("mis_pedidos")

    pedido.estado = "cancelado"
    pedido.save()

    # Restaurar stock de los productos
    items = PedidoItem.objects.filter(pedido=pedido)
    for item in items:
        producto = item.producto
        producto.stock += item.cantidad
        producto.save()

    messages.success(request, "Tu pedido ha sido cancelado exitosamente.")
    return redirect("mis_pedidos")

@login_required
def listar_pedidos(request):
    """Vista para que el admin vea todos los pedidos realizados."""
    pedidos = Pedido.objects.all().order_by("-creado").exclude(estado='cancelado')
    return render(request, "productos/listar_pedidos.html", {"pedidos": pedidos})

@login_required
def editar_pedido(request, id):
    pedido = get_object_or_404(Pedido, id=id)
    items = PedidoItem.objects.filter(pedido=pedido)  # ESTO ES LO IMPORTANTE

    return render(request, 'productos/editar_pedido.html', {
        'pedido': pedido,
        'items': items,
    })
@login_required
def eliminar_pedido(request, id):
    try:
        pedido = get_object_or_404(Pedido, id=id)
        pedido.delete()
        return redirect("listar_pedidos")
    except Exception as e:
        messages.error(request, f"Error al eliminar el pedido: {e}")
        return redirect("listar_pedidos")
    
@login_required
def editar_estado_pedido(request, id):
    if request.user.tipo_cliente != "admin":
        return HttpResponseForbidden("No tienes permiso para modificar pedidos.")

    else:
        pedido = get_object_or_404(Pedido, id=id)

        if request.method == "POST":
            nuevo_estado = request.POST.get("estado")

            if nuevo_estado not in dict(Pedido.ESTADOS):
                messages.error(request, "Estado inválido.")
                return redirect("listar_pedidos")

            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, "Estado actualizado correctamente.")
            return redirect("listar_pedidos")

        return redirect("listar_pedidos")




