
from odoo import models, fields


class Gorra(models.Model):
    _name = 'gorras.gorra'
    _description = 'Gorreria'

    nombre = fields.Char(
        string='Nombre de la gorra',required=True
    )

    color = fields.Char(
        string='Color',
        required=True
    )

    precio = fields.Float(
        string='Precio',
        required=True
    
    )
    #Veamos que hace 
    zapato_recomendado_id =fields.Many2one(
        'zapatos.zapato',
        string ='Zapato Recomendado'
    )
            

