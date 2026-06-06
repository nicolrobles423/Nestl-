{
    'name': 'Galeria de Arte',
    'version': '1.1',
    'summary': 'Gestión de obras de arte y autores',
    'author': 'Wil',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/arte_views.xml',
    ],
    'installable': True,
    'application': True,
}
