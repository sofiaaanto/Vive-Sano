from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from .models import Message

User = get_user_model()


# Selecciona automáticamente al soporte
def obtener_agente_soporte():
    return User.objects.filter(tipo_cliente="atencion_cliente").first()


# Lista de conversaciones del usuario
def lista_conversaciones(request):
    user = request.user

    conversaciones = (
        Message.objects.filter(Q(sender=user) | Q(receiver=user))
        .values("sender", "receiver")
        .annotate(last_msg=Max("timestamp"))
        .order_by("-last_msg")
    )

    # Convertir ids a usuarios evitando duplicados
    usuarios_conversando = []
    ids_agregados = set()

    for conv in conversaciones:
        partner_id = conv["receiver"] if conv["sender"] == user.id else conv["sender"]

        if partner_id not in ids_agregados:
            ids_agregados.add(partner_id)
            usuarios_conversando.append(User.objects.get(id=partner_id))

    return render(request, "mensajeria/lista_conversaciones.html", {
        "usuarios": usuarios_conversando
    })


# ------------------------------------
# Vista del chat
# ------------------------------------
def chat(request, user_id=None):

    # Si no se entrega un id, se abre directamente soporte
    if user_id is None:
        soporte = obtener_agente_soporte()
        if not soporte:
            return render(request, "mensajeria/chat.html", {
                "error": "No hay agentes de soporte disponibles."
            })
        other_user = soporte
    else:
        other_user = get_object_or_404(User, id=user_id)

    # Trae los mensajes entre ambos
    mensajes = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("timestamp")

    # Marcar como leídos
    mensajes.filter(receiver=request.user).update(is_read=True)

    # Enviar mensaje
    if request.method == "POST":
        contenido = request.POST.get("content")
        if contenido and contenido.strip():
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=contenido.strip()
            )
        return redirect("mensajeria:chat", user_id=other_user.id)

    return render(request, "mensajeria/chat.html", {
        "mensajes": mensajes,
        "other_user": other_user
    })

def soporte_conversaciones(request):
    # Solo soporte puede ver esto
    if request.user.tipo_cliente != "atencion_cliente":
        return redirect("mensajeria:conversaciones")

    conversaciones = (
        Message.objects.filter(receiver=request.user)
        .values("sender")
        .annotate(last_msg=Max("timestamp"))
        .order_by("-last_msg")
    )

    clientes = [User.objects.get(id=c["sender"]) for c in conversaciones]

    return render(request, "mensajeria/soporte_conversaciones.html", {
        "clientes": clientes
    })
