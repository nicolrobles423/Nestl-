{
    'name': 'Galeria de Ventas',
    'version': '1.1',
    'summary': 'Gestión de ventas de obras de arte',
    'author': 'Wil',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['galeria_arte'],
    'data': [
        'security/ir.model.access.csv',
        'views/arte_ventas_views.xml',
    ],
    'installable': True,
    'application': True,
}
