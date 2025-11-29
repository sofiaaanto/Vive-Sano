from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from .models import Message

User = get_user_model()


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
