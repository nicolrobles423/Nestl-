import os

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

CARPETA_FACTURAS = os.path.join(settings.MEDIA_ROOT, 'facturas')


def ruta_factura(id_pedido):
    return os.path.join(CARPETA_FACTURAS, f'factura_{id_pedido}.pdf')


def factura_existe(id_pedido):
    return os.path.isfile(ruta_factura(id_pedido))


def lineas_desde_items_carrito(items):
    """Convierto los items del carrito (con datos de Odoo ya embebidos) al
    formato (nombre, cantidad, precio_unitario, subtotal) que usa la factura."""
    return [
        (item['producto']['name'], item['cantidad'], item['producto']['list_price'], item['subtotal'])
        for item in items
    ]


def lineas_desde_pedido_odoo(pedido):
    """Convierto las líneas de un sale.order leído de Odoo (obtener_pedido_con_lineas)
    al mismo formato (nombre, cantidad, precio_unitario, subtotal)."""
    return [
        (linea['product_id'][1], linea['product_uom_qty'], linea['price_unit'], linea['price_subtotal'])
        for linea in pedido['lineas']
    ]


def generar_factura_pdf(pedido, datos_cliente, lineas):
    """
    Genero la factura en PDF y la guardo en MEDIA_ROOT/facturas/.

    pedido: dict con al menos 'id', 'name', 'amount_total' (y opcionalmente 'date_order').
    datos_cliente: dict con 'nombre', 'email', 'telefono'.
    lineas: lista de tuplas (nombre_producto, cantidad, precio_unitario, subtotal).

    Retorno la ruta absoluta del PDF generado.
    """
    os.makedirs(CARPETA_FACTURAS, exist_ok=True)
    ruta = ruta_factura(pedido['id'])

    estilos = getSampleStyleSheet()
    documento = SimpleDocTemplate(ruta, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    elementos = []

    elementos.append(Paragraph('Nestlé Ecuador', estilos['Title']))
    elementos.append(Paragraph(f"Factura — Pedido {pedido['name']}", estilos['Heading2']))
    if pedido.get('date_order'):
        elementos.append(Paragraph(f"Fecha: {pedido['date_order']}", estilos['Normal']))
    elementos.append(Spacer(1, 14))

    elementos.append(Paragraph('Datos del cliente', estilos['Heading3']))
    elementos.append(Paragraph(f"Nombre: {datos_cliente.get('nombre') or '-'}", estilos['Normal']))
    elementos.append(Paragraph(f"Correo: {datos_cliente.get('email') or '-'}", estilos['Normal']))
    elementos.append(Paragraph(f"Teléfono: {datos_cliente.get('telefono') or '-'}", estilos['Normal']))
    elementos.append(Spacer(1, 20))

    datos_tabla = [['Producto', 'Cantidad', 'Precio unitario', 'Subtotal']]
    for nombre, cantidad, precio_unitario, subtotal in lineas:
        datos_tabla.append([nombre, str(cantidad), f"${precio_unitario:.2f}", f"${subtotal:.2f}"])
    datos_tabla.append(['', '', 'Total', f"${pedido['amount_total']:.2f}"])

    tabla = Table(datos_tabla, colWidths=[8 * cm, 2.3 * cm, 3.3 * cm, 3.3 * cm])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B2E2E')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)

    documento.build(elementos)
    return ruta
