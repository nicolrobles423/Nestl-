from .carrito import Carrito


def carrito_contexto(solicitud):
    """Me expone la cantidad total de items del carrito en todos los templates."""
    return {'carrito_cantidad_total': Carrito(solicitud).cantidad_total()}
