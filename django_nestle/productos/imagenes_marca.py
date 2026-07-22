# Foto real por producto específico (con licencia libre, tomada de Wikimedia
# Commons). Solo cubro los productos para los que encontré una foto real y
# verificable; el resto queda sin imagen a propósito.
IMAGEN_POR_PRODUCTO = {
    'Milo Activ-Go en Polvo 1000g': 'productos/milo_polvo_tin.jpg',
    'Nestlé Crunch Pack 4x20g': 'productos/nestle_crunch_barra.jpg',
    'Kit Kat Chocolate con Leche 41.5g': 'productos/kitkat_barra.jpg',
}


def imagen_para_producto(producto):
    """Le asigno la foto real del producto si existe una específica.

    Si no hay una foto verificada para ese producto exacto, devuelvo None
    (no invento ni relleno con una foto genérica de la marca).
    """
    return IMAGEN_POR_PRODUCTO.get(producto.get('name'))
