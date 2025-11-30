from django.urls import path
from . import views

app_name = 'mensajeria'

urlpatterns = [
    path('conversaciones/', views.lista_conversaciones, name='conversaciones'),
    path('buscar-cliente/', views.buscar_cliente_chat, name='buscar_cliente'),
    path('chat/', views.chat, name='chat_default'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path("soporte/", views.soporte_conversaciones, name="soporte_conversaciones"),
]
