from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .conexion_odoo import OdooConexion
from .carrito import Carrito
from .models import Perfil

# Me instancio la conexión a Odoo una sola vez
conexion_odoo = OdooConexion()


def _redirigir_seguro(solicitud, url_destino, nombre_alterno='productos:carrito'):
    """Me redirijo a 'url_destino' solo si es una ruta propia del sitio (evito open redirect)."""
    if url_destino and url_has_allowed_host_and_scheme(url_destino, allowed_hosts={solicitud.get_host()}):
        return redirect(url_destino)
    return redirect(nombre_alterno)


def _cantidad_desde_formulario(solicitud, por_defecto=1):
    """Me traigo la cantidad del formulario, protegiéndome de valores no numéricos."""
    try:
        return int(solicitud.POST.get('cantidad', por_defecto))
    except (TypeError, ValueError):
        return por_defecto

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


def ver_carrito(solicitud):
    """
    Me muestro el contenido del carrito con los datos vigentes de cada
    producto (nombre, precio, marca) traídos de Odoo, y el total a pagar.
    """
    carrito = Carrito(solicitud)

    contexto = {
        'items': carrito.obtener_items(),
        'total': carrito.total(),
    }

    return render(solicitud, 'productos/carrito.html', contexto)


@require_POST
def agregar_al_carrito(solicitud, id_producto):
    """Me agrego un producto al carrito (o le sumo cantidad si ya estaba)."""
    cantidad = _cantidad_desde_formulario(solicitud)
    Carrito(solicitud).agregar(id_producto, cantidad)
    return _redirigir_seguro(solicitud, solicitud.POST.get('siguiente'))


@require_POST
def actualizar_carrito(solicitud, id_producto):
    """Me actualizo la cantidad de un producto ya presente en el carrito."""
    cantidad = _cantidad_desde_formulario(solicitud)
    Carrito(solicitud).actualizar_cantidad(id_producto, cantidad)
    return redirect('productos:carrito')


@require_POST
def eliminar_del_carrito(solicitud, id_producto):
    """Me elimino un producto del carrito."""
    Carrito(solicitud).eliminar(id_producto)
    return redirect('productos:carrito')


@require_POST
def vaciar_carrito(solicitud):
    """Me vacío el carrito por completo."""
    Carrito(solicitud).vaciar()
    return redirect('productos:carrito')


def finalizar_compra(solicitud):
    """
    Me muestro el formulario de datos del cliente y, al confirmarlo,
    creo el cliente (si no existe) y el pedido de venta en Odoo.
    """
    carrito = Carrito(solicitud)
    items = carrito.obtener_items()

    if not items:
        return redirect('productos:carrito')

    perfil_usuario = getattr(solicitud.user, 'perfil', None) if solicitud.user.is_authenticated else None
    if solicitud.user.is_authenticated:
        datos_formulario = {
            'nombre': solicitud.user.first_name or solicitud.user.email,
            'email': solicitud.user.email,
            'telefono': perfil_usuario.telefono if perfil_usuario else '',
        }
    else:
        datos_formulario = {
            'nombre': '',
            'email': '',
            'telefono': '',
        }

    if solicitud.method == 'POST':
        datos_formulario['nombre'] = solicitud.POST.get('nombre', '').strip()
        datos_formulario['email'] = solicitud.POST.get('email', '').strip()
        datos_formulario['telefono'] = solicitud.POST.get('telefono', '').strip()

        error = None
        if not datos_formulario['nombre'] or not datos_formulario['email']:
            error = 'Por favor completa tu nombre y correo electrónico.'
        else:
            # Si ya inició sesión y no cambió sus datos, uso el cliente que
            # ya tengo guardado en su perfil en vez de volver a buscarlo/crearlo.
            if (
                perfil_usuario and perfil_usuario.id_cliente_odoo
                and datos_formulario['email'] == solicitud.user.email
                and datos_formulario['nombre'] == (solicitud.user.first_name or solicitud.user.email)
                and datos_formulario['telefono'] == perfil_usuario.telefono
            ):
                id_partner = perfil_usuario.id_cliente_odoo
            else:
                id_partner = conexion_odoo.buscar_o_crear_cliente(
                    datos_formulario['nombre'],
                    datos_formulario['email'],
                    datos_formulario['telefono'],
                )
            if not id_partner:
                error = 'No pudimos registrar tus datos en Odoo. Intenta de nuevo.'
            else:
                pedido = conexion_odoo.crear_pedido(id_partner, items)
                if not pedido:
                    error = 'No pudimos crear tu pedido en Odoo. Intenta de nuevo.'
                else:
                    carrito.vaciar()
                    return render(solicitud, 'productos/pedido_confirmado.html', {'pedido': pedido})

        contexto = {
            'items': items,
            'total': carrito.total(),
            'error': error,
            **datos_formulario,
        }
        return render(solicitud, 'productos/checkout.html', contexto)

    contexto = {
        'items': items,
        'total': carrito.total(),
        **datos_formulario,
    }
    return render(solicitud, 'productos/checkout.html', contexto)


def registro(solicitud):
    """
    Me registro como cliente nuevo: creo mi usuario de Django (para poder
    iniciar sesión) y, al mismo tiempo, me creo o actualizo como res.partner
    en Odoo, para que mis datos queden guardados ahí como cliente.
    """
    if solicitud.user.is_authenticated:
        return redirect('productos:catalogo')

    datos_formulario = {
        'nombre': '',
        'email': '',
        'telefono': '',
    }

    if solicitud.method == 'POST':
        datos_formulario['nombre'] = solicitud.POST.get('nombre', '').strip()
        datos_formulario['email'] = solicitud.POST.get('email', '').strip().lower()
        datos_formulario['telefono'] = solicitud.POST.get('telefono', '').strip()
        contrasena = solicitud.POST.get('contrasena', '')
        contrasena2 = solicitud.POST.get('contrasena2', '')

        error = None
        if not datos_formulario['nombre'] or not datos_formulario['email']:
            error = 'Por favor completa tu nombre y correo electrónico.'
        elif len(contrasena) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres.'
        elif contrasena != contrasena2:
            error = 'Las contraseñas no coinciden.'
        elif User.objects.filter(username=datos_formulario['email']).exists():
            error = 'Ya existe una cuenta registrada con ese correo.'

        if not error:
            usuario_nuevo = User.objects.create_user(
                username=datos_formulario['email'],
                email=datos_formulario['email'],
                password=contrasena,
                first_name=datos_formulario['nombre'],
            )

            # Me creo o actualizo el cliente correspondiente en Odoo
            id_cliente_odoo = conexion_odoo.buscar_o_crear_cliente(
                datos_formulario['nombre'],
                datos_formulario['email'],
                datos_formulario['telefono'],
            )

            Perfil.objects.create(
                usuario=usuario_nuevo,
                telefono=datos_formulario['telefono'],
                id_cliente_odoo=id_cliente_odoo,
            )

            login(solicitud, usuario_nuevo)
            messages.success(solicitud, f'¡Bienvenido/a, {datos_formulario["nombre"]}! Tu cuenta fue creada.')
            return redirect('productos:catalogo')

        contexto = {'error': error, **datos_formulario}
        return render(solicitud, 'productos/registro.html', contexto)

    return render(solicitud, 'productos/registro.html', datos_formulario)


def iniciar_sesion(solicitud):
    """Me autentico con mi correo y contraseña."""
    if solicitud.user.is_authenticated:
        return redirect('productos:catalogo')

    error = None
    email = ''

    if solicitud.method == 'POST':
        email = solicitud.POST.get('email', '').strip().lower()
        contrasena = solicitud.POST.get('contrasena', '')

        usuario = authenticate(solicitud, username=email, password=contrasena)
        if usuario is not None:
            login(solicitud, usuario)
            return _redirigir_seguro(solicitud, solicitud.POST.get('siguiente'), 'productos:catalogo')

        error = 'Correo o contraseña incorrectos.'

    return render(solicitud, 'productos/login.html', {'error': error, 'email': email})


def cerrar_sesion(solicitud):
    """Me cierro la sesión y regreso al catálogo."""
    logout(solicitud)
    return redirect('productos:catalogo')