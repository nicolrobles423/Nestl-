from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Datos adicionales del usuario que no vienen en el User de Django.

    id_cliente_odoo guarda el ID del res.partner creado en Odoo al
    registrarse, para no tener que volver a buscarlo/crearlo en cada compra.
    """
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    id_cliente_odoo = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.usuario.get_full_name() or self.usuario.username}'
