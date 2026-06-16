# zapateria 
# nombre , talla , precio, stock, 

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ZapatosZapato(models.Model):
    _name = 'zapatos.zapato'
    _description = 'Zapato'

    name = fields.Char(string='Nombre', required=True)
    talla = fields.Integer(string='Talla', required=True)
    precio = fields.Float(string='Precio', required=True)
    stock = fields.Integer(string='Stock', required=True)
    activo = fields.Boolean(string='Activo', default=True)

    stock_bajo = fields.Boolean(
        string='Stock Bajo',
        compute='_compute_stock_bajo',
        store=True,
        )
    
    @api.depends('stock')
    def _compute_stock_bajo(self):
        for record in self:
            record.stock_bajo = record.stock < 5

    @api.constrains('precio')
    def _check_precio(self):
        for record in self:
            if record.precio <= 0:
                raise ValidationError(
                    'El precio del zapato debe ser mayor que cero.')
            
    @api.constrains('stock')
    def _check_stock(self):
        for record in self:
            if record.stock < 0:
                raise ValidationError(
                    'El stock del zapato no puede ser negativo.')
            
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError(
                    'El nombre del zapato es obligatorio y no puede estar vacío.')