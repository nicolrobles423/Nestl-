from .conexion_odoo import OdooConexion

CLAVE_SESION_CARRITO = 'carrito'
CANTIDAD_MAXIMA_POR_PRODUCTO = 99


class Carrito:
    """
    Carrito de compras guardado en la sesión del navegador.
    Solo guarda {id_producto: cantidad}; los datos del producto
    (nombre, precio, marca...) se consultan a Odoo al mostrar el carrito.
    """

    def __init__(self, solicitud):
        self.session = solicitud.session
        carrito = self.session.get(CLAVE_SESION_CARRITO)
        if carrito is None:
            carrito = self.session[CLAVE_SESION_CARRITO] = {}
        self.carrito = carrito

    def agregar(self, id_producto, cantidad=1):
        id_producto = str(id_producto)
        cantidad_actual = self.carrito.get(id_producto, 0)
        nueva_cantidad = max(1, min(cantidad_actual + cantidad, CANTIDAD_MAXIMA_POR_PRODUCTO))
        self.carrito[id_producto] = nueva_cantidad
        self._guardar()

    def actualizar_cantidad(self, id_producto, cantidad):
        id_producto = str(id_producto)
        if cantidad <= 0:
            self.eliminar(id_producto)
            return
        if id_producto in self.carrito:
            self.carrito[id_producto] = min(cantidad, CANTIDAD_MAXIMA_POR_PRODUCTO)
            self._guardar()

    def eliminar(self, id_producto):
        id_producto = str(id_producto)
        if id_producto in self.carrito:
            del self.carrito[id_producto]
            self._guardar()

    def vaciar(self):
        self.carrito = self.session[CLAVE_SESION_CARRITO] = {}
        self._guardar()

    def _guardar(self):
        self.session.modified = True

    def cantidad_total(self):
        return sum(self.carrito.values())

    def obtener_items(self):
        """
        Me traigo de Odoo los datos actuales de cada producto en el carrito
        y calculo el subtotal de cada línea con el precio vigente.
        """
        if not self.carrito:
            return []

        ids_productos = [int(id_producto) for id_producto in self.carrito.keys()]
        conexion = OdooConexion()
        productos = conexion.obtener_productos(filtro=[('id', 'in', ids_productos)])
        productos_por_id = {producto['id']: producto for producto in productos}

        items = []
        for id_producto_str, cantidad in self.carrito.items():
            producto = productos_por_id.get(int(id_producto_str))
            if not producto:
                # El producto ya no existe o fue desactivado en Odoo
                continue
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': round(producto['list_price'] * cantidad, 2),
            })
        return items

    def total(self):
        return round(sum(item['subtotal'] for item in self.obtener_items()), 2)
