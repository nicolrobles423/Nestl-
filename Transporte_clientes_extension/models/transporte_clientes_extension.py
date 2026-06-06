from odoo import models, fields, api


class TransporteClienteExtension(models.Model):
    _inherit = "transporte.publico"

    ruta_id = fields.Many2one(
        'transporte.ruta',
        string='Ruta de Transporte',
        required=True
    )


    total_de_descuento = fields.Float(
        string="Descuento (%)",
        compute="_compute_descuento",
        store=True
    )

    precio_final = fields.Float(
        string="Precio Final",
        compute="_compute_tarifa_final",
        readonly=True,
        store=True
    )

    origen = fields.Char(string="Origen",readonly=True)
    destino = fields.Char(string="Destino",readonly=True)
    pasaje = fields.Float(string="Pasaje",readonly=True)
    imagen_de_referencia = fields.Image(
    related="ruta_id.imagen_de_referencia",
    string="Imagen de referencia del Autobus",
    readonly=True,
    store=True
)


    @api.depends('pasaje','total_de_descuento','discapacidad','estudiante','edad')
    def _compute_descuento(self):
        for registro in self:
            if registro.discapacidad:
                registro.total_de_descuento = 75

            elif registro.estudiante:
                registro.total_de_descuento = 50

            elif registro.edad <= 17:
                registro.total_de_descuento = 50

            elif registro.edad >= 65:
                registro.total_de_descuento = 40

            else:
                registro.total_de_descuento = 0

    @api.depends('pasaje', 'total_de_descuento')
    def _compute_tarifa_final(self):
        for registro in self:
            registro.precio_final = (
                registro.pasaje
                - (registro.pasaje * registro.total_de_descuento / 100)
            )

    @api.onchange('ruta_id')
    def _onchange_ruta_id(self):
        if self.ruta_id:
            self.origen = self.ruta_id.origen
            self.destino = self.ruta_id.destino
            self.pasaje = self.ruta_id.pasaje


    
    

    
