import xmlrpc.client

# Configuración de conexión a Odoo
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo_test"


def obtener_uid(login, password):
    """
    Autentica un usuario contra Odoo.
    Devuelve el uid (numero) si las credenciales son correctas,
    o False si son incorrectas.
    """
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, login, password, {})
    return uid


def ejecutar(uid, password, modelo, metodo, *args, **kwargs):
    """
    Ejecuta cualquier metodo de cualquier modelo de Odoo (create, search,
    read, write, etc.), como si estuvieras usando el ORM de Odoo pero
    desde Django.

    Ejemplo de uso:
        ejecutar(uid, password, 'res.partner', 'create', [{'name': 'Juan'}])
    """
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return models.execute_kw(ODOO_DB, uid, password, modelo, metodo, list(args), kwargs)
