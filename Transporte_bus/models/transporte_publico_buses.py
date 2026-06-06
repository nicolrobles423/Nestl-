from odoo import models, fields

class TransportePublico(models.Model):
    _name = 'transporte.ruta'
    _description = 'Modelo para el transporte publico'
    
    name = fields.Char(string='Nombre de bus', required=True)
    origen = fields.Char(string='Origen', required=True)
    destino = fields.Char(string='Destino', required=True)
    activo = fields.Boolean(string='Activo', default=True)
    pasaje= fields.Float(string='Pasaje',default=0.35)
    imagen_de_referencia= fields.Image(string='Imagen de referencia')

    chofer_nombre = fields.Char(string='Nombre del encargado del bus', required=True)
    acompanante_nombre = fields.Char(string='Acompañante (opcional)')
    bus_identificacion = fields.Char(string='ID único del bus', required=True)

    numero_paradas = fields.Integer(string='Número de paradas', default=0)

    tamano_bus = fields.Selection([
        ('minibus', 'Minibús'),
        ('estandar', 'Estándar'),
        ('dos_pisos', 'Bus de dos pisos')
    ], string='Tamaño del bus', required=True)
