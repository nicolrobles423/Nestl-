from django.shortcuts import render, get_object_or_404
from .conexion_odoo import OdooConexion

# Me instancio la conexión a Odoo una sola vez
conexion_odoo = OdooConexion()

def catalogo_productos(solicitud):
    """
    Me muestro el catálogo completo de productos.
    Aquí el usuario puede filtrar por marca y categoría.
    """
    # Me traigo todos los parámetros de filtrado de la URL
    id_marca = solicitud.GET.get('marca', None)
    id_categoria = solicitud.GET.get('categoria', None)
    busqueda = solicitud.GET.get('buscar', '')
    
    # Me traigo los productos según los filtros
    if id_marca and id_categoria:
        # Me filtro por marca Y categoría
        productos = conexion_odoo.obtener_productos_por_marca_y_categoria(
            int(id_marca), 
            int(id_categoria)
        )
    elif id_marca:
        # Me filtro solo por marca
        productos = conexion_odoo.obtener_productos_por_marca(int(id_marca))
    elif id_categoria:
        # Me filtro solo por categoría
        productos = conexion_odoo.obtener_productos_por_categoria(int(id_categoria))
    else:
        # Me traigo todos los productos
        productos = conexion_odoo.obtener_productos()
    
    # Me filtro por búsqueda si lo requiere
    if busqueda:
        productos = [
            p for p in productos 
            if busqueda.lower() in p['name'].lower()
        ]
    
    # Me traigo las marcas y categorías para los filtros
    marcas = conexion_odoo.obtener_marcas()
    categorias = conexion_odoo.obtener_categorias()
    
    # Me preparo el contexto para el template
    contexto = {
        'productos': productos,
        'marcas': marcas,
        'categorias': categorias,
        'marca_seleccionada': id_marca,
        'categoria_seleccionada': id_categoria,
        'busqueda': busqueda,
    }
    
    return render(solicitud, 'productos/catalogo.html', contexto)


def detalle_producto(solicitud, id_producto):
    """
    Me muestro el detalle completo de un producto específico.
    Aquí el usuario ve toda la información y puede agregar al carrito.
    """
    # Me traigo el producto por su ID
    producto = conexion_odoo.obtener_producto_por_id(id_producto)
    
    if not producto:
        return render(solicitud, 'error.html', {'mensaje': 'Producto no encontrado'})
    
    # Me preparo el contexto
    contexto = {
        'producto': producto,
    }
    
    return render(solicitud, 'productos/detalle.html', contexto)


def productos_por_marca(solicitud, id_marca):
    """
    Me muestro los productos de una marca específica.
    Este es un atajo para filtrar por marca directamente.
    """
    productos = conexion_odoo.obtener_productos_por_marca(id_marca)
    
    # Me traigo las marcas para los filtros
    marcas = conexion_odoo.obtener_marcas()
    categorias = conexion_odoo.obtener_categorias()
    
    # Me obtengoel nombre de la marca
    nombre_marca = next(
        (m['name'] for m in marcas if m['id'] == id_marca),
        'Marca desconocida'
    )
    
    contexto = {
        'productos': productos,
        'marcas': marcas,
        'categorias': categorias,
        'marca_seleccionada': id_marca,
        'nombre_marca': nombre_marca,
    }
    
    return render(solicitud, 'productos/catalogo.html', contexto)


def productos_por_categoria(solicitud, id_categoria):
    """
    Me muestro los productos de una categoría específica.
    Este es un atajo para filtrar por categoría directamente.
    """
    productos = conexion_odoo.obtener_productos_por_categoria(id_categoria)
    
    # Me traigo las marcas y categorías para los filtros
    marcas = conexion_odoo.obtener_marcas()
    categorias = conexion_odoo.obtener_categorias()
    
    # Me obtengo el nombre de la categoría
    nombre_categoria = next(
        (c['name'] for c in categorias if c['id'] == id_categoria),
        'Categoría desconocida'
    )
    
    contexto = {
        'productos': productos,
        'marcas': marcas,
        'categorias': categorias,
        'categoria_seleccionada': id_categoria,
        'nombre_categoria': nombre_categoria,
    }
    
    return render(solicitud, 'productos/catalogo.html', contexto)