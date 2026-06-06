from odoo import models, fields

class TransportePublico(models.Model):
    _name = 'transporte.publico'
    _description = 'Modelo para el transporte publico'
    
    name = fields.Char(string='Nombre',required=True)
    edad = fields.Integer(string='Edad',required=True)
    estudiante = fields.Boolean(string='Estudiante')
    discapacidad = fields.Boolean(string='Discapacidad')
    reservacion = fields.Boolean(string='Reservación en linea')
    


    
