{
    'name': 'Galeria de Restauracion',
    'version': '1.1',
    'summary': 'Gestión de restauración de obras de arte',
    'author': 'Wil',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['galeria_arte'],
    'data': [
        'security/ir.model.access.csv',
        'views/arte_restauracion.xml',
    ],
    'installable': True,
    'application': True,
}
