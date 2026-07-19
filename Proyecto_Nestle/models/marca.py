from odoo import models, fields

# Defino el modelo de marcas 
class ProyectoNestleMarca(models.Model):
    _name = 'nestle.marca'
    _description = 'Marcas en Nestlé'

    name = fields.Char(string='Nombre', required=True)
    description = fields.Text(string='Descripción')
    logo = fields.Image(string='Logo')


# Heredo el modelo de productos de Odoo para agregarle el campo de marca
class ProductoNestle(models.Model):
    _inherit = 'product.template'

    # Relacion de cada producto con una marca
    marca_id = fields.Many2one(
        'nestle.marca',
        string='Marca Nestlé',
        ondelete='set null'
    )