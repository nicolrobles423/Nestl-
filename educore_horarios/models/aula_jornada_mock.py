from odoo import models, fields


class EduCoreAulaMock(models.Model):
    _name = 'educore.aula.mock'
    _description = 'Aula'

    name = fields.Char(
        string='Nombre del Aula',
        required=True,
    )

    capacidad = fields.Integer(
        string='Capacidad',
        default=30,
    )

    ubicacion = fields.Char(
        string='Ubicación',
    )

    tipo = fields.Selection(
        selection=[
            ('aula', 'Aula Regular'),
            ('laboratorio', 'Laboratorio'),
            ('auditorio', 'Auditorio'),
        ],
        string='Tipo',
        default='aula',
    )

    activo = fields.Boolean(
        string='Activo',
        default=True,
    )

    horario_ids = fields.One2many(
        comodel_name='educore.horario',
        inverse_name='aula_id',
        string='Horarios asignados',
    )

class EduCoreJornadaMock(models.Model):
    _name = 'educore.jornada.mock'
    _description = 'Jornada'

    name = fields.Char(
        string='Nombre de la Jornada',
        required=True,
    )

    hora_inicio = fields.Float(
        string='Hora de entrada',
        help='Formato 24h. Ej: 7.5 = 07:30',
    )

    hora_fin = fields.Float(
        string='Hora de Salira',
    )

    activo = fields.Boolean(
        string='Activo',
        default=True,
    )

    horario_ids = fields.One2many(
        comodel_name='educore.horario',
        inverse_name='jornada_id',
        string='Horarios de esta jornada',
    )