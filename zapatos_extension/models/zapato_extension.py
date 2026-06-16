from odoo import models, fields, api
from odoo.exceptions import ValidationError

 
 
class ZapatosZapato(models.Model):
    _inherit = 'zapatos.zapato'

    codigo = fields.Char(string='Còdigo')
    marca = fields.Char(string='Marca')
    color = fields.Char(string='Color')
    material = fields.Char (string='Material')
    descripcion = fields.Text(string = 'Descripciòn')
    stock_minimo = fields.Integer(string = 'Stock Minimo', default = 5)
    descuento = fields.Float(string='Descuento (%)', default=0.0)
 
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('available', 'Disponible'),
        ('out_stock', 'Agotado'),
        ('discontinued', 'Descontinuado'),
    ], string='Estado', default='draft', required=True)
 
    valor_inventario = fields.Float(
        string='Valor_inventario',
        compute='_compute_valor_inventario',
        store=True
    )
 
    @api.depends('precio', 'stock')
    def _compute_valor_inventario(self):
        for record in self:
            record.valor_inventario = record.precio * record.stock

    @api.constrains('stock_minimo')
    def _check_stock_minimo(self):
        for record in self:
            if record.stock_minimo < 0:
                raise ValidationError('El stock mínimo del zapato no puede ser negativo.')
 
    def action_disponible(self):
        for record in self:
            record.state = 'available'
 
    def action_agotado(self):
        for record in self:
            record.state = 'out_stock'
 
    def action_descontinuar(self):
        for record in self:
            record.state = 'discontinued'
 
    def action_borrador(self):
        for record in self:
            record.state = 'draft'
 
