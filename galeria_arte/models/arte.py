from odoo import models, fields, api
from odoo.exceptions import ValidationError


class GaleriaArte(models.Model):
    _name = 'galeria.arte'
    _description = 'Modelo para una galeria de arte'
    _rec_name = 'obra'

    # --- Información del autor ---
    name = fields.Char(string='Nombre del autor', required=True)

    origen = fields.Char(string='País de origen', required=True)

    anio_nacimiento = fields.Integer(string='Año de nacimiento del autor')

    biografia = fields.Text(string='Biografía del autor')

    # --- Información de la obra ---
    obra = fields.Char(string='Nombre de la obra', required=True)

    anio_creacion = fields.Integer(string='Año de creación')

    descripcion = fields.Text(string='Descripción de la obra')

    dimensiones = fields.Char(string='Dimensiones (ej: 80x100 cm)')

    tecnica = fields.Selection(
        [
            ('r', 'Realismo'),
            ('i', 'Impresionismo'),
            ('e', 'Expresionismo'),
            ('s', 'Surrealismo'),
            ('a', 'Arte Abstracto'),
            ('b', 'Barroco'),
            ('m', 'Modernismo'),
            ('c', 'Contemporáneo'),
        ],
        string='Técnica de Arte',
        required=True,
    )

    soporte = fields.Selection(
        [
            ('lienzo', 'Lienzo'),
            ('madera', 'Madera'),
            ('papel', 'Papel'),
            ('metal', 'Metal'),
            ('ceramica', 'Cerámica'),
            ('otro', 'Otro'),
        ],
        string='Soporte / Material',
        required=True,
        default='lienzo',
    )

    # --- Valoración y estado ---
    precio = fields.Float(string='Precio de exhibición ($)', required=True)

    precio_minimo = fields.Float(string='Precio mínimo de venta ($)')

    estado_conservacion = fields.Selection(
        [
            ('excelente', 'Excelente'),
            ('bueno', 'Bueno'),
            ('regular', 'Regular'),
            ('malo', 'Malo'),
        ],
        string='Estado de conservación',
        required=True,
        default='bueno',
    )

    disponible = fields.Boolean(string='Disponible para venta', default=True)

    prioridad = fields.Selection(
        [
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
        ],
        string='Prioridad de venta',
        required=True,
        default='media',
    )

    fecha_ingreso = fields.Date(
        string='Fecha de ingreso a la galería',
        default=fields.Date.today,
    )

    # --- Campo calculado: antigüedad de la obra ---
    antiguedad = fields.Integer(
        string='Antigüedad (años)',
        compute='_compute_antiguedad',
        store=True,
    )

    @api.depends('anio_creacion')
    def _compute_antiguedad(self):
        from datetime import date
        anio_actual = date.today().year
        for rec in self:
            if rec.anio_creacion and rec.anio_creacion > 0:
                rec.antiguedad = anio_actual - rec.anio_creacion
            else:
                rec.antiguedad = 0

    # --- Validaciones ---
    @api.constrains('precio', 'precio_minimo')
    def _check_precios(self):
        for rec in self:
            if rec.precio <= 0:
                raise ValidationError(
                    "El precio de exhibición debe ser mayor a cero."
                )
            if rec.precio_minimo < 0:
                raise ValidationError(
                    "El precio mínimo no puede ser negativo."
                )
            if rec.precio_minimo > rec.precio:
                raise ValidationError(
                    "El precio mínimo no puede ser mayor al precio de exhibición."
                )

    @api.constrains('anio_creacion', 'anio_nacimiento')
    def _check_anios(self):
        from datetime import date
        anio_actual = date.today().year
        for rec in self:
            if rec.anio_creacion and rec.anio_creacion > anio_actual:
                raise ValidationError(
                    "El año de creación no puede ser mayor al año actual."
                )
            if rec.anio_nacimiento and rec.anio_nacimiento > anio_actual:
                raise ValidationError(
                    "El año de nacimiento del autor no puede ser mayor al año actual."
                )
