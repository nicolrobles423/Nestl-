from odoo import models, fields


class Zapato(models.Model):
    _inherit = 'zapatos.zapato'

    proveedor_id = fields.Many2one(
        'zapatos.proveedor',
        string='Proveedor',
        required=True
    )

    categoria_id = fields.Many2one(
        'zapatos.categoria',
        string='Categoria',
        required=True
    )