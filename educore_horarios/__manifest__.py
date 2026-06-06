{
    'name': 'aula_jornada_mock.py',
    'version': '16.0.1.0.0',
    'summary': 'Gestión de horarios académicos y asignación docente',
    'description': "Horarios de Docentes y estudiantes",
    'author': 'Grupo6',
    'category': 'Education',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/educore_horario_views.xml',
    ],
    'installable': True,
    'application': True,
}