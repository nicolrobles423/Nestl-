import xmlrpc.client
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
                                  'description_sale', 'default_code']
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
                              'description_sale', 'default_code']
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
                {'fields': ['id', 'name', 'amount_total']}
            )
            return pedido[0] if pedido else None

        except Exception as excepcion:
            print(f"Error al crear pedido: {excepcion}")
            return None