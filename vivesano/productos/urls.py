from django.urls import path
from . import views

urlpatterns = [
    # CRUD admin
    path("admin-lista/", views.listar_productos, name="listar_productos"),
    path("admin-crear/", views.crear_producto, name="crear_producto"),
    path("admin-editar/<int:id>/", views.editar_producto, name="editar_producto"),
    path("admin-eliminar/<int:id>/", views.eliminar_producto, name="eliminar_producto"),

    # Catálogo
    path("catalogo/", views.catalogo, name="catalogo_productos"),

    # Carrito
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/eliminar/<int:id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/vaciar/", views.vaciar_carrito, name="vaciar_carrito"),
    path("carrito/finalizar/", views.finalizar_compra, name="finalizar_compra"),

]
