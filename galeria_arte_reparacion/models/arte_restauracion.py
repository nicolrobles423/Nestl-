from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ArteRestauracion(models.Model):
    _name = 'arte.restauracion'
    _description = 'Restauración de obras de arte'
    _rec_name = 'arte_id'

    # --- Relación con la obra ---
    arte_id = fields.Many2one(
        'galeria.arte',
        string='Obra',
        required=True,
        ondelete='restrict',
    )

    nombre_autor = fields.Char(
        related='arte_id.name',
        string='Autor',
        store=True,
    )

    precio_arte = fields.Float(
        related='arte_id.precio',
        string='Precio de la Obra ($)',
        store=True,
    )

    tecnica_arte = fields.Selection(
        related='arte_id.tecnica',
        string='Técnica',
        store=True,
    )

    estado_previo = fields.Selection(
        related='arte_id.estado_conservacion',
        string='Estado previo a restauración',
        store=True,
    )

    # --- Información del restaurador ---
    reparador = fields.Char(string='Nombre del restaurador', required=True)

    especialidad = fields.Selection(
        [
            ('pintura', 'Pintura'),
            ('escultura', 'Escultura'),
            ('papel', 'Papel y documentos'),
            ('textil', 'Textiles'),
            ('general', 'Restauración general'),
        ],
        string='Especialidad del restaurador',
        required=True,
        default='general',
    )

    empresa_restauracion = fields.Char(string='Empresa / Taller de restauración')

    # --- Detalle del daño ---
    estado = fields.Selection(
        [
            ('i', 'Irreparable'),
            ('m', 'Muy dañado'),
            ('p', 'Poco daños'),
            ('a', 'Arreglar una parte'),
        ],
        string='Estado de la Obra',
        required=True,
        default='m',
    )

    descripcion_dano = fields.Text(string='Descripción del daño')

    zona_afectada = fields.Char(string='Zona afectada de la obra')

    # --- Fechas ---
    fecha_entrega = fields.Datetime(
        string='Fecha de ingreso a restauración',
        required=True,
        default=fields.Datetime.today,
    )

    fecha_retiro = fields.Datetime(
        string='Fecha estimada de retiro',
        required=True,
    )

    fecha_real_entrega = fields.Datetime(string='Fecha real de entrega')

    # --- Costos ---
    costo = fields.Float(string='Costo base de restauración ($)', required=True)

    costo_materiales = fields.Float(string='Costo de materiales ($)')

    costo_total = fields.Float(
        string='Costo total ($)',
        compute='_compute_costo_total',
        store=True,
    )

    porcentaje_costo = fields.Float(
        string='Costo como % del valor de la obra (%)',
        compute='_compute_porcentaje_costo',
        store=True,
    )

    # --- Estado del proceso ---
    fase = fields.Selection(
        [
            ('evaluacion', 'En evaluación'),
            ('proceso', 'En proceso'),
            ('finalizado', 'Finalizado'),
            ('cancelado', 'Cancelado'),
        ],
        string='Fase de restauración',
        default='evaluacion',
        required=True,
    )

    observaciones = fields.Text(string='Observaciones finales')

    # --- Cálculos ---
    @api.depends('costo', 'costo_materiales')
    def _compute_costo_total(self):
        for rec in self:
            rec.costo_total = rec.costo + rec.costo_materiales

    @api.depends('costo_total', 'precio_arte')
    def _compute_porcentaje_costo(self):
        for rec in self:
            if rec.precio_arte and rec.precio_arte > 0:
                rec.porcentaje_costo = (rec.costo_total / rec.precio_arte) * 100
            else:
                rec.porcentaje_costo = 0.0

    # --- Validaciones ---
    @api.constrains('costo', 'costo_materiales')
    def _check_costos(self):
        for rec in self:
            if rec.costo < 0:
                raise ValidationError(
                    "El costo base de restauración no puede ser negativo."
                )
            if rec.costo_materiales < 0:
                raise ValidationError(
                    "El costo de materiales no puede ser negativo."
                )

    @api.constrains('fecha_entrega', 'fecha_retiro')
    def _check_fechas(self):
        for rec in self:
            if rec.fecha_retiro and rec.fecha_entrega:
                if rec.fecha_retiro <= rec.fecha_entrega:
                    raise ValidationError(
                        "La fecha de retiro debe ser posterior a la fecha de ingreso."
                    )

    @api.constrains('porcentaje_costo')
    def _check_porcentaje(self):
        for rec in self:
            if rec.porcentaje_costo > 80:
                raise ValidationError(
                    "El costo de restauración supera el 80% del valor de la obra. "
                    "Verifique si conviene restaurar."
                )
