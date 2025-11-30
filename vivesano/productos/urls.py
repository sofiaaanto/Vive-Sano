from django.urls import path
from . import views

urlpatterns = [
    # CRUD admin
    path("admin-lista/", views.listar_productos, name="listar_productos"),
    path("admin-crear/", views.crear_producto, name="crear_producto"),
    path("admin-editar/<int:id>/", views.editar_producto, name="editar_producto"),
    path("admin-eliminar/<int:id>/", views.eliminar_producto, name="eliminar_producto"),
    path("admin-lista-pedidos/", views.listar_pedidos, name="listar_pedidos"),
    path("editar-pedido/<int:id>/", views.editar_pedido, name="editar_pedido"),
    path("eliminar-pedido/<int:id>/", views.eliminar_pedido, name="eliminar_pedido"),
    path("editar-estado-pedido/<int:id>/", views.editar_estado_pedido, name="editar_estado_pedido"),


    # Catálogo
    path("catalogo/", views.catalogo, name="catalogo_productos"),

    # Carrito
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/eliminar/<int:id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/solicitar_reserva/<int:producto_id>/", views.solicitar_reserva, name="solicitar_reserva"),#nose
    path("carrito/vaciar/", views.vaciar_carrito, name="vaciar_carrito"),
    path("carrito/finalizar/", views.finalizar_compra, name="finalizar_compra"),
    path('solicitar-reserva/<int:producto_id>/', views.solicitar_reserva, name='solicitar_reserva'),
    path('solicitar-reembolso/<int:pedido_id>/', views.solicitar_reembolso, name='solicitar_reembolso'),
    path("pedido/<int:pedido_id>/", views.ver_estado_pedido, name="ver_estado_pedido"),
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path("cancelar-pedido/<int:pedido_id>/", views.cancelar_pedido, name="cancelar_pedido"),


]
