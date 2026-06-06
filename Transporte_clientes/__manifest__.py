{
    'name': 'Transporte publico - clientes',
    'version': '1.0',
    'summary': 'Servicio de transporte - clientes',
    'description': 'Transporte publico - clientes',
    'author': 'Grupo',
    'category': 'Sales',
    'license': 'LGPL-3',
    'depends': ['bus'],
    'data': {
        'security/ir.model.access.csv',
        'views/transporte_publico_views.xml',
    },
    'installable': True,
    'application': True,

}