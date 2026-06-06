{
    'name': 'Venta de Gorras',
    'version': '1.0',
    'summary': 'Es una tienda de Gorras',
    'description': 'Gorreria',
    'author': 'Alejo',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['base', 'zapatos'],
    'data': [
        'security/ir.model.access.csv',
        'views/gorra_views.xml',
    ],
    'installable': True,
    'application': True,
}

