from decimal import Decimal

def descuento_por_cantidad_empresa(cantidad: int) -> Decimal:
    """
    Retorna el porcentaje de descuento para clientes empresa
    según la cantidad total de un producto.
    """
    if cantidad >= 1000:
        return Decimal("0.12")  # 12 %
    elif cantidad >= 500:
        return Decimal("0.07")  # 7 %
    return Decimal("0.00")      # sin descuento
