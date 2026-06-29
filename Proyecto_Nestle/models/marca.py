from odoo import models, fields

class ProyectoNestleMarca(models.Model):
    _name = 'nestle.marca'
    _description = 'Marcas en Nestlé'

    name = fields.Char(string='Nombre', required=True)
    descripcion = fields.Text(string='Descripción')
    logo = fields.Image(string='Logo')