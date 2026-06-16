from odoo import models, fields, api

class ZapatosZapato(models.Model):
    _inherit = 'zapatos.zapato'

    codigo = fields.Char(string='Còdigo')
    marca = fields.Char(string='Marca')
    color = fields.Char(string='Color')
    material = fields.Char (string='Material')
    descripcion = fields.Text(string = 'Descripciòn')
    stock_minimo = fields.Integer(string = 'Stock Minimo', default = 5)
    descuento = fields.Float(string='Descuento (%)', default=0.0)
    
    
    valor_inventario = fields.Float(
        string ='Valor_inventario',
        compute = '_compute_valor_inventario',
        store = True
    )

    @api.depends('precio','stock')
    def _compute_valor_inventario(self):
        for record in self:
            record.valor_inventario = record.precio * record.stock 

            
