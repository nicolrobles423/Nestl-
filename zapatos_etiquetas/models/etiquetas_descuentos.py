from odoo import models, fields, api

class EtiquetasDescuentos(models.Model):
    _name = 'etiquetas.descuentos'
    _description = 'Modelo para gestionar los descuentos'

    name = fields.Selection([
        ('descuento_navideño', 'Descuento Navideño'),
        ('descuento_madres', 'Descuento Madres'),
        ('descuento_verano', 'Descuento Verano'),
        ('descuento_black_friday', 'Descuento Black Friday'),
        ('descuento_fin_de_año', 'Descuento Fin de Año'),
        ('descuento_escolar', 'Descuento Escolar'),
        ('descuento_deportivo', 'Descuento Deportivo'),
    ],  string='Nombre del Descuento', 
        required=True)
    
    cantidad_descuento = fields.Float(
        string='Porcentaje de Descuento', 
        compute='_compute_cantidad_descuento',
        store=True
    )
    
    zapato_id = fields.Many2one('zapatos.zapato', string='Zapato Relacionado')

    DESCUENTOS = {
        'descuento_navideño': 20.0,
        'descuento_madres': 15.0,
        'descuento_verano': 25.0,
        'descuento_black_friday': 50.0,
        'descuento_fin_de_año': 30.0,
        'descuento_escolar': 10.0,
        'descuento_deportivo': 18.0,
    }

    @api.depends('name')
    def _compute_cantidad_descuento(self):
        for record in self:
            record.cantidad_descuento = self.DESCUENTOS.get(record.name, 0.0)

# esta clase es para las etiquetas   
         
class Etiquetas(models.Model):
    _name = 'etiquetas.etiquetas'
    _description = 'Modelo para gestionar etiquetas'

    name = fields.Selection([
        ('oferta', 'Oferta'),
        ('nuevo', 'Nuevo'),
        ('liquidacion', 'Liquidación'),
    ], string='Etiqueta', required=True)
    color = fields.Char(string='Color de la Etiqueta', default='#000000')
    zapato_ids = fields.Many2many('zapatos.zapato', string='Zapatos Relacionados')
    
    
# Herencia del modelo zapato para agregar descuento, precio final y etiquetas
class ZapatoExtension(models.Model):
    _inherit = 'zapatos.zapato'

    descuento = fields.Float(string='Descuento (%)')
    precio_final = fields.Float(
        string='Precio Final',
        compute='_compute_precio_final',
        store=True
    )
    etiqueta_ids = fields.Many2many('etiquetas.etiquetas', string='Etiquetas')

    @api.depends('precio', 'descuento')
    def _compute_precio_final(self):
        for record in self:
            record.precio_final = record.precio - (record.precio * record.descuento / 100)