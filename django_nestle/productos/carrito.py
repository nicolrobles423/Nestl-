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

    def eliminar_varios(self, ids_productos):
        """Quito del carrito solo los productos indicados (los demás quedan
        intactos), para cuando se paga solo una parte del carrito."""
        for id_producto in ids_productos:
            self.carrito.pop(str(id_producto), None)
        self._guardar()

    def vaciar(self):
        self.carrito = self.session[CLAVE_SESION_CARRITO] = {}
        self._guardar()

    def _guardar(self):
        self.session.modified = True

    def cantidad_total(self):
        return sum(self.carrito.values())

    def obtener_items(self, solo_ids=None):
        """
        Me traigo de Odoo los datos actuales de cada producto en el carrito
        y calculo el subtotal de cada línea con el precio vigente.

        Si 'solo_ids' viene dado, me limito a esos productos del carrito
        (para cuando el cliente elige pagar solo una parte de lo que tiene).
        """
        if not self.carrito:
            return []

        carrito = self.carrito
        if solo_ids is not None:
            ids_permitidos = {str(id_producto) for id_producto in solo_ids}
            carrito = {k: v for k, v in carrito.items() if k in ids_permitidos}
            if not carrito:
                return []

        ids_productos = [int(id_producto) for id_producto in carrito.keys()]
        conexion = OdooConexion()
        productos = conexion.obtener_productos(filtro=[('id', 'in', ids_productos)])
        productos_por_id = {producto['id']: producto for producto in productos}

        items = []
        for id_producto_str, cantidad in carrito.items():
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

    def total(self, solo_ids=None):
        return round(sum(item['subtotal'] for item in self.obtener_items(solo_ids=solo_ids)), 2)

    def totales_con_impuestos(self, solo_ids=None):
        """
        Retorno (subtotal, iva, total) calculados con los impuestos reales
        configurados en Odoo para cada producto, para que el total mostrado
        coincida con lo que Odoo termina cobrando en el pedido.
        """
        items = self.obtener_items(solo_ids=solo_ids)
        if not items:
            return 0.0, 0.0, 0.0
        conexion = OdooConexion()
        productos_con_cantidad = [(item['producto'], item['cantidad']) for item in items]
        return conexion.calcular_totales_con_impuestos(productos_con_cantidad)
