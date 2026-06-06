from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ArteVenta(models.Model):
    _name = 'arte.ventas'
    _description = 'Venta de obras de arte'
    _rec_name = 'arte_id'

    # --- Relación con la obra ---
    arte_id = fields.Many2one(
        'galeria.arte',
        string='Obra',
        required=True,
        ondelete='restrict',
        domain=[('disponible', '=', True)],
    )

    nombre_autor = fields.Char(
        related='arte_id.name',
        string='Autor',
        store=True,
    )

    tecnica_arte = fields.Selection(
        related='arte_id.tecnica',
        string='Técnica',
        store=True,
    )

    precio_arte = fields.Float(
        compute='_compute_precio',
        string='Precio base ($)',
        store=True,
    )

    precio_minimo = fields.Float(
        related='arte_id.precio_minimo',
        string='Precio mínimo ($)',
        store=True,
    )

    # --- Negociación ---
    descuento = fields.Float(string='Descuento (%)', default=0.0)

    precio_con_descuento = fields.Float(
        string='Precio con descuento ($)',
        compute='_compute_precio_descuento',
        store=True,
    )

    # --- Impuestos y totales ---
    iva = fields.Float(
        string='IVA 15% ($)',
        compute='_compute_iva',
        store=True,
    )

    total = fields.Float(
        string='Total a pagar ($)',
        compute='_compute_total',
        store=True,
    )

    comision_galeria = fields.Float(
        string='Comisión galería 10% ($)',
        compute='_compute_comision',
        store=True,
    )

    ganancia_neta = fields.Float(
        string='Ganancia neta ($)',
        compute='_compute_ganancia',
        store=True,
    )

    # --- Datos del comprador ---
    cliente = fields.Char(string='Nombre del comprador', required=True)

    cedula_cliente = fields.Char(string='Cédula / RUC del comprador')

    telefono_cliente = fields.Char(string='Teléfono del comprador')

    email_cliente = fields.Char(string='Correo del comprador')

    # --- Datos de la transacción ---
    metodo_pago = fields.Selection(
        [
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia bancaria'),
            ('tarjeta', 'Tarjeta de crédito/débito'),
            ('cheque', 'Cheque'),
        ],
        string='Método de pago',
        required=True,
        default='efectivo',
    )

    fecha_venta = fields.Datetime(
        string='Fecha de la compra',
        default=fields.Datetime.today,
        required=True,
    )

    fecha_entrega = fields.Date(string='Fecha de entrega de la obra')

    vendedor = fields.Char(string='Vendedor responsable')

    estado = fields.Selection(
        [
            ('d', 'Disponible'),
            ('r', 'Reservada'),
            ('v', 'Vendida'),
            ('c', 'Cancelada'),
        ],
        string='Estado',
        default='d',
        required=True,
    )

    notas = fields.Text(string='Notas de la venta')

    # --- Cálculos ---
    @api.depends('arte_id.precio')
    def _compute_precio(self):
        for rec in self:
            rec.precio_arte = rec.arte_id.precio if rec.arte_id else 0.0

    @api.depends('precio_arte', 'descuento')
    def _compute_precio_descuento(self):
        for rec in self:
            if rec.descuento:
                rec.precio_con_descuento = rec.precio_arte * (1 - rec.descuento / 100)
            else:
                rec.precio_con_descuento = rec.precio_arte

    @api.depends('precio_con_descuento')
    def _compute_iva(self):
        for rec in self:
            rec.iva = rec.precio_con_descuento * 0.15

    @api.depends('precio_con_descuento', 'iva')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.precio_con_descuento + rec.iva

    @api.depends('precio_con_descuento')
    def _compute_comision(self):
        for rec in self:
            rec.comision_galeria = rec.precio_con_descuento * 0.10

    @api.depends('precio_con_descuento', 'comision_galeria')
    def _compute_ganancia(self):
        for rec in self:
            rec.ganancia_neta = rec.precio_con_descuento - rec.comision_galeria

    # --- Validaciones ---
    @api.constrains('descuento')
    def _check_descuento(self):
        for rec in self:
            if rec.descuento < 0 or rec.descuento > 100:
                raise ValidationError(
                    "El descuento debe estar entre 0% y 100%."
                )

    @api.constrains('precio_con_descuento', 'precio_minimo')
    def _check_precio_minimo(self):
        for rec in self:
            if rec.precio_minimo and rec.precio_con_descuento < rec.precio_minimo:
                raise ValidationError(
                    f"El precio con descuento (${rec.precio_con_descuento:.2f}) "
                    f"no puede ser menor al precio mínimo (${rec.precio_minimo:.2f})."
                )

    @api.constrains('fecha_venta', 'fecha_entrega')
    def _check_fechas(self):
        for rec in self:
            if rec.fecha_entrega and rec.fecha_venta:
                from datetime import datetime
                fecha_v = rec.fecha_venta.date() if isinstance(rec.fecha_venta, datetime) else rec.fecha_venta
                if rec.fecha_entrega < fecha_v:
                    raise ValidationError(
                        "La fecha de entrega no puede ser anterior a la fecha de venta."
                    )
