import xmlrpc.client
from django.conf import settings

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
            return producto[0] if producto else None
        
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