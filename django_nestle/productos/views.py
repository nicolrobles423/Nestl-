from functools import partial, wraps
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from . import facturas
from .conexion_odoo import OdooConexion
from .carrito import Carrito
from .models import Perfil

# El resto del sitio (login.html, iniciar_sesion) usa 'siguiente' como nombre
# del parámetro de retorno, no el 'next' por defecto de Django.
login_required = partial(login_required, redirect_field_name='siguiente')


def rol_requerido(*roles):
    """
    Exijo que el usuario haya iniciado sesión Y que su Perfil tenga uno de
    los roles indicados (p. ej. 'administrador'). Reemplaza el uso de
    @staff_member_required en los paneles, que solo miraba is_staff y no
    distinguía administrador de bodeguero.
    """
    def decorador(vista):
        @wraps(vista)
        @login_required
        def _vista(solicitud, *args, **kwargs):
            perfil = getattr(solicitud.user, 'perfil', None)
            if not perfil or perfil.rol not in roles:
                raise PermissionDenied
            return vista(solicitud, *args, **kwargs)
        return _vista
    return decorador

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


def _productos_variados(productos, cantidad=10):
    """
    Me armo una selección variada de productos alternando entre marcas
    (ronda por marca), en vez de traer los primeros N que devuelva Odoo
    (que suelen venir agrupados por marca y muestran solo una de ellas).
    """
    por_marca = {}
    for producto in productos:
        id_marca = producto['marca_id'][0] if producto.get('marca_id') else None
        por_marca.setdefault(id_marca, []).append(producto)

    seleccion = []
    while len(seleccion) < cantidad and any(por_marca.values()):
        for id_marca in list(por_marca.keys()):
            if por_marca[id_marca]:
                seleccion.append(por_marca[id_marca].pop(0))
                if len(seleccion) >= cantidad:
                    break
    return seleccion

def catalogo_productos(solicitud):
    """
    Me muestro el catálogo completo de productos, pero solo si ya inicié
    sesión. Si no, me muestro una pantalla de bienvenida con un carrusel
    de productos destacados, invitando a iniciar sesión o registrarse.
    """
    if not solicitud.user.is_authenticated:
        productos_carrusel = _productos_variados(conexion_odoo.obtener_productos(), cantidad=10)
        return render(solicitud, 'productos/landing.html', {'productos_carrusel': productos_carrusel})

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

    # Me pagino los resultados (12 productos por página)
    paginador = Paginator(productos, 12)
    numero_pagina = solicitud.GET.get('pagina', 1)
    pagina_productos = paginador.get_page(numero_pagina)

    # Me traigo las marcas y categorías para los filtros
    marcas = conexion_odoo.obtener_marcas()
    categorias = conexion_odoo.obtener_categorias()

    # Me preparo el contexto para el template
    contexto = {
        'productos': pagina_productos,
        'total_productos': paginador.count,
        'marcas': marcas,
        'categorias': categorias,
        'marca_seleccionada': id_marca,
        'categoria_seleccionada': id_categoria,
        'busqueda': busqueda,
    }

    # Si la pido por AJAX (buscador/filtros sin recargar), devuelvo solo el
    # fragmento con la grilla y la paginación, no la página completa.
    if solicitud.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(solicitud, 'productos/_grid_productos.html', contexto)

    return render(solicitud, 'productos/catalogo.html', contexto)


@login_required
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


@login_required
def ver_carrito(solicitud):
    """
    Me muestro el contenido del carrito con los datos vigentes de cada
    producto (nombre, precio, marca) traídos de Odoo, y el total a pagar
    (con el IVA que Odoo le calcula a cada producto, para que coincida con
    lo que realmente se cobra al confirmar el pedido).
    """
    carrito = Carrito(solicitud)
    subtotal, iva, total = carrito.totales_con_impuestos()

    contexto = {
        'items': carrito.obtener_items(),
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
    }

    return render(solicitud, 'productos/carrito.html', contexto)


@login_required
@require_POST
def agregar_al_carrito(solicitud, id_producto):
    """Me agrego un producto al carrito (o le sumo cantidad si ya estaba)."""
    cantidad = _cantidad_desde_formulario(solicitud)
    Carrito(solicitud).agregar(id_producto, cantidad)
    messages.success(solicitud, 'Producto añadido al carrito.')
    return _redirigir_seguro(solicitud, solicitud.POST.get('siguiente'))


@login_required
@require_POST
def actualizar_carrito(solicitud, id_producto):
    """Me actualizo la cantidad de un producto ya presente en el carrito."""
    cantidad = _cantidad_desde_formulario(solicitud)
    Carrito(solicitud).actualizar_cantidad(id_producto, cantidad)
    return redirect('productos:carrito')


@login_required
@require_POST
def eliminar_del_carrito(solicitud, id_producto):
    """Me elimino un producto del carrito."""
    Carrito(solicitud).eliminar(id_producto)
    return redirect('productos:carrito')


@login_required
@require_POST
def vaciar_carrito(solicitud):
    """Me vacío el carrito por completo."""
    Carrito(solicitud).vaciar()
    return redirect('productos:carrito')


@login_required
def finalizar_compra(solicitud):
    """
    Me muestro el formulario de datos del cliente y, al confirmarlo,
    creo el cliente (si no existe) y el pedido de venta en Odoo, además de
    generar la factura en PDF. Solo pago los productos seleccionados en el
    carrito ('items'); los que no seleccioné quedan guardados para después.
    """
    carrito = Carrito(solicitud)

    if solicitud.method == 'POST':
        # Las casillas seleccionadas viajan como campos ocultos desde carrito.html/checkout.html
        ids_seleccionados = solicitud.POST.getlist('items') or None
    elif solicitud.GET.get('modo') == 'seleccion':
        ids_seleccionados = solicitud.GET.getlist('items')
        if not ids_seleccionados:
            messages.error(solicitud, 'Selecciona al menos un producto para pagar.')
            return redirect('productos:carrito')
    else:
        # Se entró sin elegir nada específico (p. ej. enlace directo): pago todo el carrito
        ids_seleccionados = None

    items = carrito.obtener_items(solo_ids=ids_seleccionados)

    if not items:
        return redirect('productos:carrito')

    ids_a_pagar = [str(item['producto']['id']) for item in items]
    subtotal_a_pagar, iva_a_pagar, total_a_pagar = carrito.totales_con_impuestos(solo_ids=ids_a_pagar)

    perfil_usuario = getattr(solicitud.user, 'perfil', None)
    datos_formulario = {
        'nombre': solicitud.user.first_name or solicitud.user.email,
        'email': solicitud.user.email,
        'telefono': perfil_usuario.telefono if perfil_usuario else '',
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
                    lineas_factura = facturas.lineas_desde_items_carrito(items)
                    facturas.generar_factura_pdf(pedido, datos_formulario, lineas_factura)
                    carrito.eliminar_varios(ids_a_pagar)
                    return render(solicitud, 'productos/pedido_confirmado.html', {'pedido': pedido})

        contexto = {
            'items': items,
            'subtotal': subtotal_a_pagar,
            'iva': iva_a_pagar,
            'total': total_a_pagar,
            'ids_a_pagar': ids_a_pagar,
            'error': error,
            **datos_formulario,
        }
        return render(solicitud, 'productos/checkout.html', contexto)

    contexto = {
        'items': items,
        'subtotal': subtotal_a_pagar,
        'iva': iva_a_pagar,
        'total': total_a_pagar,
        'ids_a_pagar': ids_a_pagar,
        **datos_formulario,
    }
    return render(solicitud, 'productos/checkout.html', contexto)


@login_required
def mis_pedidos(solicitud):
    """Historial de pedidos del cliente logueado, con enlace para descargar
    (o regenerar, si ya no existe en disco) la factura de cada uno."""
    perfil_usuario = getattr(solicitud.user, 'perfil', None)
    pedidos = []
    if perfil_usuario and perfil_usuario.id_cliente_odoo:
        pedidos = conexion_odoo.obtener_pedidos_por_cliente(perfil_usuario.id_cliente_odoo)
    return render(solicitud, 'productos/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def descargar_factura(solicitud, id_pedido):
    """
    Descargo el PDF de la factura de un pedido. Un cliente solo puede
    descargar la suya; el administrador puede descargar la de cualquiera
    (la usa desde el panel de pedidos). Si el PDF ya no existe en disco (se
    borró, o el pedido es de antes de tener esta función), lo regenero desde
    los datos que Odoo todavía tiene guardados.
    """
    perfil_usuario = getattr(solicitud.user, 'perfil', None)
    if not perfil_usuario:
        raise Http404

    pedido = conexion_odoo.obtener_pedido_con_lineas(id_pedido)
    if not pedido or not pedido.get('partner_id'):
        raise Http404

    es_propio = perfil_usuario.id_cliente_odoo == pedido['partner_id'][0]
    es_administrador = perfil_usuario.rol == Perfil.ROL_ADMINISTRADOR
    if not es_propio and not es_administrador:
        # No es su pedido y no es administrador: no se lo dejo descargar.
        raise Http404

    if not facturas.factura_existe(id_pedido):
        cliente = pedido.get('cliente') or {}
        datos_cliente = {
            'nombre': cliente.get('name'),
            'email': cliente.get('email'),
            'telefono': cliente.get('phone'),
        }
        facturas.generar_factura_pdf(pedido, datos_cliente, facturas.lineas_desde_pedido_odoo(pedido))

    return FileResponse(
        open(facturas.ruta_factura(id_pedido), 'rb'),
        as_attachment=True,
        filename=f"factura_{pedido['name']}.pdf",
    )


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
                rol=Perfil.ROL_CLIENTE,
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

            siguiente = solicitud.POST.get('siguiente')
            # Si soy administrador y no venía de una página específica, entro
            # directo a mi panel (no al admin de Django) en vez del catálogo.
            perfil_usuario = getattr(usuario, 'perfil', None)
            if not siguiente and perfil_usuario and perfil_usuario.rol == Perfil.ROL_ADMINISTRADOR:
                return redirect('productos:panel_inicio')

            return _redirigir_seguro(solicitud, siguiente, 'productos:catalogo')

        error = 'Correo o contraseña incorrectos.'

    return render(solicitud, 'productos/login.html', {'error': error, 'email': email})


def cerrar_sesion(solicitud):
    """Me cierro la sesión y regreso al catálogo."""
    logout(solicitud)
    return redirect('productos:catalogo')


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
def panel_inicio(solicitud):
    """Página de inicio del administrador: estadísticas rápidas y accesos
    directos a los paneles de productos, stock, pedidos y usuarios
    (reemplaza al admin de Django)."""
    total_productos = len(conexion_odoo.obtener_productos())
    total_usuarios = Perfil.objects.count()
    pedidos = conexion_odoo.obtener_todos_los_pedidos()
    total_pedidos = len(pedidos)
    ventas_totales = sum(pedido.get('amount_total', 0) for pedido in pedidos)

    contexto = {
        'total_productos': total_productos,
        'total_usuarios': total_usuarios,
        'total_pedidos': total_pedidos,
        'ventas_totales': ventas_totales,
    }
    return render(solicitud, 'productos/panel_inicio.html', contexto)


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
def panel_productos(solicitud):
    """
    Panel para que el administrador vea y gestione todos los productos
    (incluidos los inactivos), respaldado por los permisos que el grupo
    'Administrador Nestlé' tiene sobre product.template en Odoo.
    """
    productos = conexion_odoo.obtener_productos(
        filtro=[('marca_id', '!=', False), ('active', 'in', [True, False])]
    )
    productos.sort(key=lambda p: p['name'])
    return render(solicitud, 'productos/panel_productos.html', {'productos': productos})


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
def panel_producto_form(solicitud, id_producto=None):
    """
    Formulario para crear un producto nuevo (id_producto=None) o editar uno
    existente. Al guardar, escribo directamente en Odoo por XML-RPC.
    """
    producto = conexion_odoo.obtener_producto_por_id(id_producto) if id_producto else None
    if id_producto and not producto:
        return render(solicitud, 'error.html', {'mensaje': 'Producto no encontrado'})

    marcas = conexion_odoo.obtener_marcas()
    categorias = conexion_odoo.obtener_categorias()

    datos_formulario = {
        'name': producto['name'] if producto else '',
        'default_code': (producto.get('default_code') or '') if producto else '',
        'marca_id': str(producto['marca_id'][0]) if producto and producto.get('marca_id') else '',
        'categ_id': str(producto['categ_id'][0]) if producto and producto.get('categ_id') else '',
        'list_price': producto['list_price'] if producto else '',
        'standard_price': producto['standard_price'] if producto else '',
        'description_sale': (producto.get('description_sale') or '') if producto else '',
    }

    error = None

    if solicitud.method == 'POST':
        datos_formulario['name'] = solicitud.POST.get('name', '').strip()
        datos_formulario['default_code'] = solicitud.POST.get('default_code', '').strip()
        datos_formulario['marca_id'] = solicitud.POST.get('marca_id', '')
        datos_formulario['categ_id'] = solicitud.POST.get('categ_id', '')
        datos_formulario['list_price'] = solicitud.POST.get('list_price', '')
        datos_formulario['standard_price'] = solicitud.POST.get('standard_price', '')
        datos_formulario['description_sale'] = solicitud.POST.get('description_sale', '').strip()

        datos_odoo = None
        if not datos_formulario['name'] or not datos_formulario['marca_id'] or not datos_formulario['categ_id']:
            error = 'Completa al menos el nombre, la marca y la categoría.'
        else:
            try:
                datos_odoo = {
                    'name': datos_formulario['name'],
                    'default_code': datos_formulario['default_code'] or False,
                    'marca_id': int(datos_formulario['marca_id']),
                    'categ_id': int(datos_formulario['categ_id']),
                    'list_price': float(datos_formulario['list_price'] or 0),
                    'standard_price': float(datos_formulario['standard_price'] or 0),
                    'description_sale': datos_formulario['description_sale'] or False,
                }
            except ValueError:
                error = 'Los precios deben ser números válidos.'

        if not error and datos_odoo is not None:
            try:
                if producto:
                    conexion_odoo.actualizar_producto(producto['id'], datos_odoo)
                    messages.success(solicitud, f'Producto "{datos_formulario["name"]}" actualizado.')
                else:
                    conexion_odoo.crear_producto(datos_odoo)
                    messages.success(solicitud, f'Producto "{datos_formulario["name"]}" creado.')
                return redirect('productos:panel_productos')
            except Exception:
                error = 'No se pudo guardar el producto en Odoo. Intenta de nuevo.'

    contexto = {
        'producto': producto,
        'marcas': marcas,
        'categorias': categorias,
        'error': error,
        **datos_formulario,
    }
    return render(solicitud, 'productos/panel_producto_form.html', contexto)


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
@require_POST
def panel_producto_eliminar(solicitud, id_producto):
    """Elimino un producto de Odoo. Si tiene movimientos asociados (ventas,
    stock, etc.), Odoo lo bloquea; en ese caso sugiero desactivarlo."""
    try:
        conexion_odoo.eliminar_producto(id_producto)
        messages.success(solicitud, 'Producto eliminado correctamente.')
    except Exception:
        messages.error(
            solicitud,
            'No se pudo eliminar: el producto ya tiene movimientos asociados '
            '(ventas, stock, etc.). Puedes desactivarlo en su lugar.'
        )
    return redirect('productos:panel_productos')


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
@require_POST
def panel_producto_archivar(solicitud, id_producto):
    """Activo o desactivo un producto (alternativa segura a eliminarlo)."""
    activar = solicitud.POST.get('accion') == 'activar'
    conexion_odoo.actualizar_producto(id_producto, {'active': activar})
    messages.success(solicitud, 'Producto activado.' if activar else 'Producto desactivado.')
    return redirect('productos:panel_productos')


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
def panel_pedidos(solicitud):
    """Panel para que el administrador vea TODOS los pedidos del sistema
    (no solo los suyos), con enlace para descargar cada factura."""
    pedidos = conexion_odoo.obtener_todos_los_pedidos()
    return render(solicitud, 'productos/panel_pedidos.html', {'pedidos': pedidos})


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
def panel_usuarios(solicitud):
    """Panel para que el administrador vea todos los usuarios registrados
    y les asigne un rol (cliente / administrador / bodeguero)."""
    perfiles = Perfil.objects.select_related('usuario').order_by('usuario__username')
    return render(solicitud, 'productos/panel_usuarios.html', {
        'perfiles': perfiles,
        'roles_disponibles': Perfil.ROL_CHOICES,
    })


@rol_requerido(Perfil.ROL_ADMINISTRADOR)
@require_POST
def panel_usuario_cambiar_rol(solicitud, id_perfil):
    """Cambio el rol de un usuario registrado."""
    perfil = get_object_or_404(Perfil, id=id_perfil)
    nuevo_rol = solicitud.POST.get('rol')
    if nuevo_rol not in dict(Perfil.ROL_CHOICES):
        messages.error(solicitud, 'Rol no válido.')
    else:
        perfil.rol = nuevo_rol
        perfil.save()
        messages.success(solicitud, f'Rol de {perfil.usuario.username} actualizado a "{perfil.get_rol_display()}".')
    return redirect('productos:panel_usuarios')


@rol_requerido(Perfil.ROL_BODEGUERO, Perfil.ROL_ADMINISTRADOR)
def panel_stock(solicitud):
    """Panel para que el bodeguero vea el stock de cada producto y lo ajuste."""
    productos = conexion_odoo.obtener_productos(
        filtro=[('marca_id', '!=', False), ('active', 'in', [True, False])]
    )
    productos.sort(key=lambda p: p['name'])
    return render(solicitud, 'productos/panel_stock.html', {'productos': productos})


@rol_requerido(Perfil.ROL_BODEGUERO, Perfil.ROL_ADMINISTRADOR)
@require_POST
def panel_stock_ajustar(solicitud, id_producto):
    """Ajusto el stock de un producto a la cantidad que indique el bodeguero."""
    try:
        nueva_cantidad = float(solicitud.POST.get('cantidad', ''))
    except (TypeError, ValueError):
        messages.error(solicitud, 'La cantidad debe ser un número.')
        return redirect('productos:panel_stock')

    if nueva_cantidad < 0:
        messages.error(solicitud, 'La cantidad no puede ser negativa.')
        return redirect('productos:panel_stock')

    try:
        conexion_odoo.ajustar_stock(id_producto, nueva_cantidad)
        messages.success(solicitud, 'Stock actualizado correctamente.')
    except Exception:
        messages.error(solicitud, 'No se pudo ajustar el stock. Intenta de nuevo.')

    return redirect('productos:panel_stock')