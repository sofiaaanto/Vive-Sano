from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from usuarios.backends import Usuario
from .models import Message
from django.contrib import messages
from .models import Message
from .forms import BuscarClienteForm

User = get_user_model()

def buscar_cliente_chat(request):
    # Solo atención al cliente
    if not request.user.is_authenticated or request.user.tipo_cliente != "atencion_cliente":
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect("dashboard")

    form = BuscarClienteForm(request.GET or None)
    resultados = Usuario.objects.none()

    if form.is_valid():
        query = form.cleaned_data["query"].strip()

        resultados = Usuario.objects.filter(
            Q(rut__icontains=query) |
            Q(username__icontains=query)
        ).exclude(tipo_cliente="atencion_cliente")

        if not resultados.exists():
            messages.warning(request, "No se encontró ningún cliente con ese RUT o usuario.")

    return render(request, "mensajeria/buscar_cliente.html", {
        "form": form,
        "resultados": resultados,
    })
    
def iniciar_chat_con_cliente(request, id_cliente):
    if request.user.tipo_cliente != "atencion_cliente":
        messages.error(request, "No tienes permiso.")
        return redirect("dashboard")

    cliente = get_object_or_404(Usuario, id=id_cliente)

    # Buscar chat existente
    chat, creado = Message.objects.get_or_create(
        usuario=cliente,
        soporte=request.user
    )

    return redirect("chat_detalle", chat_id=chat.id)


# Selecciona automáticamente al soporte
def obtener_agente_soporte():
    return User.objects.filter(tipo_cliente="atencion_cliente").order_by('?').first()

def lista_conversaciones(request):
    user = request.user

    conversaciones = (
        Message.objects.filter(Q(sender=user) | Q(receiver=user))
        .values("sender", "receiver")
        .annotate(last_msg=Max("timestamp"))
        .order_by("-last_msg")
    )

    usuarios_conversando = []
    ids_agregados = set()

    for conv in conversaciones:
        partner_id = conv["receiver"] if conv["sender"] == user.id else conv["sender"]

        if partner_id not in ids_agregados:
            ids_agregados.add(partner_id)

            partner = User.objects.get(id=partner_id)

            # Contar no leídos de ese usuario → hacia ti
            partner.unread_count = Message.objects.filter(
                sender=partner,
                receiver=user,
                is_read=False
            ).count()

            usuarios_conversando.append(partner)

    return render(request, "mensajeria/lista_conversaciones.html", {
        "usuarios": usuarios_conversando
    })


# ------------------------------------
# Vista del chat
# ------------------------------------
def chat(request, user_id=None):

    user = request.user

    # 1. Cliente sin user_id → asignar soporte automáticamente
    if user.tipo_cliente != "atencion_cliente" and user_id is None:
        soporte = obtener_agente_soporte()
        if not soporte:
            return render(request, "mensajeria/chat.html", {
                "error": "No hay agentes de soporte disponibles."
            })
        other_user = soporte

    # 2. Soporte sin user_id → NO puede abrir chat sin elegir cliente
    elif user.tipo_cliente == "atencion_cliente" and user_id is None:
        return redirect("mensajeria:soporte_conversaciones")

    # 3. Chat normal con user_id
    else:
        other_user = get_object_or_404(User, id=user_id)

    # Obtener mensajes reales
    mensajes = Message.objects.filter(
        Q(sender=user, receiver=other_user) |
        Q(sender=other_user, receiver=user)
    ).order_by("timestamp")

    # Marcar mensajes recibidos como leídos
    mensajes.filter(receiver=user).update(is_read=True)

    # Enviar mensaje
    if request.method == "POST":
        texto = request.POST.get("mensaje") or request.POST.get("content")

        if texto and texto.strip():
            Message.objects.create(
                sender=user,
                receiver=other_user,
                content=texto.strip()
            )

        return redirect("mensajeria:chat", user_id=other_user.id)

    return render(request, "mensajeria/chat.html", {
        "mensajes": mensajes,
        "other_user": other_user
    })


def soporte_conversaciones(request):
    conversaciones = (
        Message.objects.filter(receiver=request.user)
        .values("sender")
        .annotate(last_msg=Max("timestamp"))
        .order_by("-last_msg")
    )

    clientes = []
    for conv in conversaciones:
        cliente = User.objects.get(id=conv["sender"])
        cliente.unread_count = Message.objects.filter(
            sender=cliente,
            receiver=request.user,
            is_read=False
        ).count()
        clientes.append(cliente)

    return render(request, "mensajeria/soporte_conversaciones.html", {
        "clientes": clientes
    })
