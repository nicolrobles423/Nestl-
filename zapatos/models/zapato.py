# zapateria 
# nombre , talla , precio, stock, 

from odoo import models, fields


class ZapatosZapato(models.Model):
    _name = 'zapatos.zapato'
    _description = 'Zapato'

    name = fields.Char(string='Nombre', required=True)
    talla = fields.Integer(string='Talla')
    precio = fields.Float(string='Precio')
    stock = fields.Integer(string='Stock')
    activo = fields.Boolean(string='Activo', default=True)
    fecha = fields.Date(string='Fecha')