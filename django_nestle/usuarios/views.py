from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import RegistroForm, LoginForm
from odoo_connector.conexion import obtener_uid, ejecutar


def registro(request):
    formulario = RegistroForm()

    if request.method == 'POST':
        formulario = RegistroForm(request.POST)

        if formulario.is_valid():
            datos = formulario.cleaned_data

            # Para la autentificacio con la cuenta técnica (admin) para asi crear el usuario nuevo
            uid_admin = obtener_uid(settings.ODOO_ADMIN_LOGIN, settings.ODOO_ADMIN_PASSWORD)

            # Para reviar si el  ya existe un usuario con ese correo en Odoo
            usuarios_existentes = ejecutar(
                uid_admin, settings.ODOO_ADMIN_PASSWORD,
                'res.users', 'search',
                [('login', '=', datos['correo'])]
            )

            if usuarios_existentes:
                formulario.add_error('correo', 'Ese correo ya está registrado')
            else:
                # para buscar el grupo "Cliente" para asignárselo al usuario nuevo
                grupo_cliente = ejecutar(
                    uid_admin, settings.ODOO_ADMIN_PASSWORD,
                    'res.groups', 'search',
                    [('name', '=', 'Cliente')]
                )

                #Para crear el usuario en Odoo
                ejecutar(
                    uid_admin, settings.ODOO_ADMIN_PASSWORD,
                    'res.users', 'create',
                    [{
                        'name': datos['nombre'],
                        'login': datos['correo'],
                        'email': datos['correo'],
                        'password': datos['contrasena'],
                        'groups_id': [(6, 0, grupo_cliente)] if grupo_cliente else [],
                    }]
                )

                messages.success(request, 'Cuenta creada con éxito, ya puedes iniciar sesión :3')
                return redirect('login')

    return render(request, 'usuarios/registro.html', {'formulario': formulario})


def iniciar_sesion(request):
    formulario = LoginForm()

    if request.method == 'POST':
        formulario = LoginForm(request.POST)

        if formulario.is_valid():
            datos = formulario.cleaned_data
            uid = obtener_uid(datos['correo'], datos['contrasena'])

            if uid:
                # Para guardar los datos de sesión para usarlos en futuras llamadas a Odoo
                request.session['odoo_uid'] = uid
                request.session['odoo_correo'] = datos['correo']
                request.session['odoo_contrasena'] = datos['contrasena']

                messages.success(request, 'Bienvenido/a')
                return redirect('inicio')
            else:
                formulario.add_error(None, 'Correo o contraseña incorrectos')

    return render(request, 'usuarios/login.html', {'formulario': formulario})


def cerrar_sesion(request):
    request.session.flush()
    return redirect('login')

def inicio(request):
    # Muestro una bienvenida temporal mientras construyo el catálogo real
    if not request.session.get('odoo_uid'):
        return redirect('login')

    return render(request, 'usuarios/inicio.html', {
        'correo': request.session.get('odoo_correo')
    })
