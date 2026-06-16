{
    'name': 'zapatos',
    'version': '1.0',
    'summary': 'Es una zapateria',
    'description': 'Primer modulo para una zapateria.',
    'author': 'Alejo',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/zapato_views.xml',
    ],
    'installable': True,
    'application': True,
}

