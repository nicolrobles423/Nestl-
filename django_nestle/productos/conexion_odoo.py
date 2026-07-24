import xmlrpc.client
from decimal import ROUND_HALF_UP, Decimal
from django.conf import settings
from .imagenes_marca import imagen_para_producto

# Me conecto a Odoo usando XML-RPC para traer datos de productos, marcas y categorías
class OdooConexion:
    """
    Me creo una clase para manejar la conexión a Odoo vía XML-RPC.
    Esta clase facilita traer datos de productos, marcas y categorías.
    """
    
    def __init__(self):
        # Me obtengo la configuración de Odoo desde settings.py
        self.host = settings.ODOO_CONFIG['host']
        self.puerto = settings.ODOO_CONFIG['puerto']
        self.base_datos = settings.ODOO_CONFIG['base_datos']
        self.usuario_admin = settings.ODOO_CONFIG['usuario_admin']
        self.contrasena_admin = settings.ODOO_CONFIG['contrasena_admin']
        
        # Me construyo la URL base de Odoo
        self.url_base = f"http://{self.host}:{self.puerto}"
        
        # Me inicializo los proxies de XML-RPC
        self.proxy_comun = xmlrpc.client.ServerProxy(f'{self.url_base}/xmlrpc/2/common')
        self.proxy_objetos = xmlrpc.client.ServerProxy(f'{self.url_base}/xmlrpc/2/object')
        
        # Me obtengo el UID del usuario admin autenticándome
        self.uid = self._autenticarme()
    
    def _autenticarme(self):
        """
        Me autentico en Odoo usando las credenciales de admin.
        Retorno el UID si la autenticación es exitosa.
        """
        try:
            uid = self.proxy_comun.authenticate(
                self.base_datos,
                self.usuario_admin,
                self.contrasena_admin,
                {}
            )
            return uid
        except Exception as excepcion:
            print(f"Error al autenticarme en Odoo: {excepcion}")
            return None
    
    def obtener_productos(self, filtro=None, limite=False):
        """
        Me traigo todos los productos de Odoo.
        Retorno una lista con nombre, precio, marca, categoría y stock.
        """
        try:
            # Me establezco el filtro por defecto (solo productos activos)
            if filtro is None:
                filtro = [('active', '=', True), ('marca_id', '!=', False)]
            
            # Me traigo los IDs de los productos que cumplen el filtro
            ids_productos = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.template',
                'search',
                [filtro],
                {'limit': limite} if limite else {}
            )
            
            # Me traigo los datos de cada producto
            if ids_productos:
                productos = self.proxy_objetos.execute_kw(
                    self.base_datos,
                    self.uid,
                    self.contrasena_admin,
                    'product.template',
                    'read',
                    [ids_productos],
                    {
                        'fields': ['id', 'name', 'list_price', 'standard_price',
                                  'marca_id', 'categ_id', 'qty_available',
                                  'description_sale', 'default_code', 'active', 'taxes_id']
                    }
                )
                for producto in productos:
                    producto['imagen'] = imagen_para_producto(producto)
                return productos
            else:
                return []
        
        except Exception as excepcion:
            print(f"Error al traer productos: {excepcion}")
            return []
    
    def obtener_producto_por_id(self, id_producto):
        """
        Me traigo un producto específico por su ID.
        Retorno todos sus datos.
        """
        try:
            producto = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.template',
                'read',
                [[id_producto]],
                {
                    'fields': ['id', 'name', 'list_price', 'standard_price',
                              'marca_id', 'categ_id', 'qty_available',
                              'description_sale', 'default_code', 'active']
                }
            )
            producto = producto[0] if producto else None
            if producto:
                producto['imagen'] = imagen_para_producto(producto)
            return producto
        
        except Exception as excepcion:
            print(f"Error al traer producto: {excepcion}")
            return None
    
    def obtener_marcas(self):
        """
        Me traigo todas las marcas de Odoo.
        Retorno una lista con ID y nombre.
        """
        try:
            ids_marcas = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'nestle.marca',
                'search',
                [[]]
            )
            
            if ids_marcas:
                marcas = self.proxy_objetos.execute_kw(
                    self.base_datos,
                    self.uid,
                    self.contrasena_admin,
                    'nestle.marca',
                    'read',
                    [ids_marcas],
                    {'fields': ['id', 'name']}
                )
                return marcas
            else:
                return []
        
        except Exception as excepcion:
            print(f"Error al traer marcas: {excepcion}")
            return []
    
    def obtener_categorias(self):
        """
        Me traigo todas las categorías de Odoo.
        Retorno una lista con ID y nombre.
        """
        try:
            # Me traigo solo las categorías hijo (no la raíz)
            ids_categorias = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.category',
                'search',
                [[('parent_id', '!=', False)]]
            )
            
            if ids_categorias:
                categorias = self.proxy_objetos.execute_kw(
                    self.base_datos,
                    self.uid,
                    self.contrasena_admin,
                    'product.category',
                    'read',
                    [ids_categorias],
                    {'fields': ['id', 'name', 'parent_id']}
                )
                return categorias
            else:
                return []
        
        except Exception as excepcion:
            print(f"Error al traer categorías: {excepcion}")
            return []
    
    def obtener_productos_por_marca(self, id_marca):
        """
        Me traigo los productos de una marca específica.
        Retorno una lista filtrada por marca.
        """
        filtro = [('marca_id', '=', id_marca), ('active', '=', True)]
        return self.obtener_productos(filtro=filtro)
    
    def obtener_productos_por_categoria(self, id_categoria):
        """
        Me traigo los productos de una categoría específica.
        Retorno una lista filtrada por categoría.
        """
        filtro = [('categ_id', '=', id_categoria), ('active', '=', True)]
        return self.obtener_productos(filtro=filtro)
    
    def obtener_productos_por_marca_y_categoria(self, id_marca, id_categoria):
        """
        Me traigo los productos filtrados por marca Y categoría.
        Retorno una lista con ambos filtros aplicados.
        """
        filtro = [
            ('marca_id', '=', id_marca),
            ('categ_id', '=', id_categoria),
            ('active', '=', True)
        ]
        return self.obtener_productos(filtro=filtro)

    def buscar_o_crear_cliente(self, nombre, email, telefono=''):
        """
        Me busco un cliente (res.partner) por su correo; si no existe, lo creo.
        Retorno el ID del partner, o None si algo falla.
        """
        try:
            ids_partner = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'res.partner',
                'search',
                [[('email', '=', email)]],
                {'limit': 1}
            )

            if ids_partner:
                return ids_partner[0]

            return self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'res.partner',
                'create',
                [{'name': nombre, 'email': email, 'phone': telefono}]
            )

        except Exception as excepcion:
            print(f"Error al buscar/crear cliente: {excepcion}")
            return None

    def obtener_variantes_por_plantillas(self, ids_plantillas):
        """
        Me traigo el ID de la variante (product.product) de cada plantilla
        (product.template). Lo necesito porque sale.order.line usa
        product.product, no product.template.
        Retorno un diccionario {id_plantilla: id_variante}.
        """
        try:
            ids_variantes = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.product',
                'search',
                [[('product_tmpl_id', 'in', ids_plantillas)]]
            )

            if not ids_variantes:
                return {}

            variantes = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.product',
                'read',
                [ids_variantes],
                {'fields': ['id', 'product_tmpl_id']}
            )
            return {variante['product_tmpl_id'][0]: variante['id'] for variante in variantes}

        except Exception as excepcion:
            print(f"Error al traer variantes de producto: {excepcion}")
            return {}

    def crear_producto(self, datos):
        """
        Me creo un producto nuevo (product.template) en Odoo.
        'datos' es un dict con los campos a guardar (name, list_price, etc.).
        Retorno el ID del producto creado, o None si falla.
        """
        try:
            datos = dict(datos)
            datos.setdefault('type', 'consu')
            datos.setdefault('is_storable', True)
            return self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.template',
                'create',
                [datos]
            )
        except Exception as excepcion:
            print(f"Error al crear producto: {excepcion}")
            raise

    def actualizar_producto(self, id_producto, datos):
        """
        Me actualizo los campos de un producto existente.
        Retorno True si se guardó correctamente.
        """
        try:
            return self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'product.template',
                'write',
                [[id_producto], datos]
            )
        except Exception as excepcion:
            print(f"Error al actualizar producto: {excepcion}")
            raise

    def eliminar_producto(self, id_producto):
        """
        Me elimino un producto de Odoo. Si el producto ya tiene movimientos
        (ventas, stock, etc.) Odoo no lo deja borrar; en ese caso propago el
        error para que la vista le explique al administrador que debe
        desactivarlo en lugar de eliminarlo.
        """
        return self.proxy_objetos.execute_kw(
            self.base_datos,
            self.uid,
            self.contrasena_admin,
            'product.template',
            'unlink',
            [[id_producto]]
        )

    def _ubicacion_stock_principal(self):
        """Ubicación interna del almacén principal (normalmente 'WH/Stock'),
        donde guardo los ajustes de inventario que hace el bodeguero."""
        ids_almacen = self.proxy_objetos.execute_kw(
            self.base_datos, self.uid, self.contrasena_admin,
            'stock.warehouse', 'search', [[]], {'limit': 1}
        )
        if not ids_almacen:
            return None
        almacenes = self.proxy_objetos.execute_kw(
            self.base_datos, self.uid, self.contrasena_admin,
            'stock.warehouse', 'read', [ids_almacen], {'fields': ['lot_stock_id']}
        )
        lot_stock_id = almacenes[0].get('lot_stock_id') if almacenes else None
        return lot_stock_id[0] if lot_stock_id else None

    def ajustar_stock(self, id_producto_template, nueva_cantidad):
        """
        Ajusto la cantidad disponible ('qty_available') de un producto a
        'nueva_cantidad', usando el mecanismo real de ajuste de inventario de
        Odoo (stock.quant + action_apply_inventory) sobre la ubicación
        principal del almacén. Si el producto todavía no rastrea inventario
        (is_storable=False, el caso de los productos creados antes de esta
        función), lo activo primero.
        """
        ids_variante = self.proxy_objetos.execute_kw(
            self.base_datos, self.uid, self.contrasena_admin,
            'product.product', 'search',
            [[('product_tmpl_id', '=', id_producto_template)]], {'limit': 1}
        )
        if not ids_variante:
            raise ValueError('El producto no tiene una variante para ajustar stock.')
        id_variante = ids_variante[0]

        self.proxy_objetos.execute_kw(
            self.base_datos, self.uid, self.contrasena_admin,
            'product.template', 'write', [[id_producto_template], {'is_storable': True}]
        )

        id_ubicacion = self._ubicacion_stock_principal()
        if not id_ubicacion:
            raise ValueError('No se encontró una ubicación de almacén para ajustar el stock.')

        ids_quant = self.proxy_objetos.execute_kw(
            self.base_datos, self.uid, self.contrasena_admin,
            'stock.quant', 'search',
            [[('product_id', '=', id_variante), ('location_id', '=', id_ubicacion)]], {'limit': 1}
        )

        if ids_quant:
            id_quant = ids_quant[0]
            self.proxy_objetos.execute_kw(
                self.base_datos, self.uid, self.contrasena_admin,
                'stock.quant', 'write',
                [[id_quant], {'inventory_quantity': nueva_cantidad, 'inventory_quantity_set': True}]
            )
        else:
            id_quant = self.proxy_objetos.execute_kw(
                self.base_datos, self.uid, self.contrasena_admin,
                'stock.quant', 'create',
                [{
                    'product_id': id_variante,
                    'location_id': id_ubicacion,
                    'inventory_quantity': nueva_cantidad,
                    'inventory_quantity_set': True,
                }]
            )

        try:
            self.proxy_objetos.execute_kw(
                self.base_datos, self.uid, self.contrasena_admin,
                'stock.quant', 'action_apply_inventory', [[id_quant]]
            )
        except xmlrpc.client.Fault as excepcion:
            # action_apply_inventory no retorna nada; Odoo falla al serializar
            # ese None por XML-RPC, pero el ajuste ya quedó aplicado en el
            # servidor (verificado: qty_available se actualiza igual).
            if 'cannot marshal None' not in str(excepcion):
                raise

        return True

    def obtener_impuestos(self, ids_impuestos):
        """Me traigo los impuestos (account.tax) indicados, para poder calcular
        cuánto IVA le corresponde a cada línea del carrito."""
        if not ids_impuestos:
            return []
        try:
            return self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'account.tax',
                'read',
                [list(ids_impuestos)],
                {'fields': ['id', 'amount', 'amount_type', 'price_include_override']}
            )
        except Exception as excepcion:
            print(f"Error al traer impuestos: {excepcion}")
            return []

    def calcular_totales_con_impuestos(self, productos_con_cantidad):
        """
        Calculo el subtotal, el IVA y el total (subtotal + IVA) de una lista
        de líneas [(producto, cantidad), ...], usando los impuestos
        ('taxes_id') configurados en cada producto en Odoo. Así el total que
        se ve en el carrito coincide con el que Odoo cobra de verdad.
        Retorno (subtotal, impuestos, total), los tres redondeados a 2 decimales.
        """
        ids_impuestos = set()
        for producto, _ in productos_con_cantidad:
            ids_impuestos.update(producto.get('taxes_id') or [])

        impuestos_por_id = {impuesto['id']: impuesto for impuesto in self.obtener_impuestos(ids_impuestos)}

        # Uso Decimal en toda la cuenta (no float) para no arrastrar errores de
        # precisión (p. ej. 28.5 * 0.15 en float da 4.2749999999999995 en vez
        # de 4.275), y redondeo el impuesto de cada línea antes de sumar,
        # igual que hace Odoo internamente.
        dos_decimales = Decimal('0.01')
        subtotal = Decimal('0')
        total_impuestos = Decimal('0')
        for producto, cantidad in productos_con_cantidad:
            precio_linea = Decimal(str(producto['list_price'])) * Decimal(cantidad)
            subtotal += precio_linea
            for id_impuesto in (producto.get('taxes_id') or []):
                impuesto = impuestos_por_id.get(id_impuesto)
                # Solo sé calcular impuestos de tipo "porcentaje" que no vengan
                # ya incluidos en el precio (el caso configurado en este proyecto).
                if impuesto and impuesto['amount_type'] == 'percent' and impuesto.get('price_include_override') != 'always':
                    porcentaje = Decimal(str(impuesto['amount'])) / Decimal('100')
                    total_impuestos += (precio_linea * porcentaje).quantize(dos_decimales, rounding=ROUND_HALF_UP)

        subtotal = subtotal.quantize(dos_decimales, rounding=ROUND_HALF_UP)
        total_impuestos = total_impuestos.quantize(dos_decimales, rounding=ROUND_HALF_UP)
        total = (subtotal + total_impuestos).quantize(dos_decimales, rounding=ROUND_HALF_UP)
        return float(subtotal), float(total_impuestos), float(total)

    def obtener_pedidos_por_cliente(self, id_partner):
        """
        Me traigo el historial de pedidos (sale.order) de un cliente,
        del más reciente al más antiguo. Lo uso para "Mis pedidos".
        """
        try:
            ids_pedidos = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'search',
                [[('partner_id', '=', id_partner)]],
                {'order': 'date_order desc'}
            )

            if not ids_pedidos:
                return []

            return self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'read',
                [ids_pedidos],
                {'fields': ['id', 'name', 'date_order', 'amount_total', 'state']}
            )

        except Exception as excepcion:
            print(f"Error al traer pedidos del cliente: {excepcion}")
            return []

    def obtener_todos_los_pedidos(self):
        """
        Me traigo TODOS los pedidos (sale.order) del sistema, sin filtrar por
        cliente, del más reciente al más antiguo. Lo usa el administrador en
        el panel de pedidos.
        """
        try:
            ids_pedidos = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'search',
                [[]],
                {'order': 'date_order desc'}
            )

            if not ids_pedidos:
                return []

            return self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'read',
                [ids_pedidos],
                {'fields': ['id', 'name', 'partner_id', 'date_order', 'amount_total', 'state']}
            )

        except Exception as excepcion:
            print(f"Error al traer todos los pedidos: {excepcion}")
            return []

    def obtener_pedido_con_lineas(self, id_pedido):
        """
        Me traigo un pedido (sale.order) completo: sus datos, los del
        cliente (res.partner) y el detalle de líneas (producto, cantidad,
        precio). Lo uso para regenerar una factura si el PDF ya no existe
        en disco.
        Retorno None si el pedido no existe.
        """
        try:
            pedidos = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'read',
                [[id_pedido]],
                {'fields': ['id', 'name', 'date_order', 'amount_total', 'partner_id', 'order_line']}
            )
            if not pedidos:
                return None
            pedido = pedidos[0]

            cliente = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'res.partner',
                'read',
                [[pedido['partner_id'][0]]],
                {'fields': ['id', 'name', 'email', 'phone']}
            )
            pedido['cliente'] = cliente[0] if cliente else None

            ids_lineas = pedido.get('order_line') or []
            lineas = []
            if ids_lineas:
                lineas = self.proxy_objetos.execute_kw(
                    self.base_datos,
                    self.uid,
                    self.contrasena_admin,
                    'sale.order.line',
                    'read',
                    [ids_lineas],
                    {'fields': ['product_id', 'product_uom_qty', 'price_unit', 'price_subtotal', 'display_type']}
                )
                # Descarto líneas de sección/nota (display_type no vacío), que no son productos reales
                lineas = [linea for linea in lineas if not linea.get('display_type')]
            pedido['lineas'] = lineas

            return pedido

        except Exception as excepcion:
            print(f"Error al traer el pedido con líneas: {excepcion}")
            return None

    def crear_pedido(self, id_partner, items_carrito):
        """
        Me creo un pedido de venta (sale.order) en Odoo con las líneas del carrito.
        items_carrito: lista de dicts con 'producto' (dict con 'id') y 'cantidad'.
        Retorno un dict con id/name/amount_total del pedido, o None si falla.
        """
        try:
            ids_plantillas = [item['producto']['id'] for item in items_carrito]
            mapa_variantes = self.obtener_variantes_por_plantillas(ids_plantillas)

            lineas_pedido = []
            for item in items_carrito:
                id_variante = mapa_variantes.get(item['producto']['id'])
                if not id_variante:
                    continue
                lineas_pedido.append((0, 0, {
                    'product_id': id_variante,
                    'product_uom_qty': item['cantidad'],
                }))

            if not lineas_pedido:
                return None

            id_pedido = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'create',
                [{'partner_id': id_partner, 'order_line': lineas_pedido}]
            )

            pedido = self.proxy_objetos.execute_kw(
                self.base_datos,
                self.uid,
                self.contrasena_admin,
                'sale.order',
                'read',
                [[id_pedido]],
                {'fields': ['id', 'name', 'amount_total', 'date_order']}
            )
            return pedido[0] if pedido else None

        except Exception as excepcion:
            print(f"Error al crear pedido: {excepcion}")
            return None