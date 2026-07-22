import os
from pathlib import Path

# Me establezco la ruta base del proyecto
RUTA_BASE = Path(__file__).resolve().parent.parent

# Clave secreta para desarrollo (cambiar en producción)
SECRET_KEY = 'django-insecure-key-para-desarrollo-nestlesolo'

# Modo de depuración (desactivar en producción)
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = ['*']

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'productos',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL raíz de configuración
ROOT_URLCONF = 'proyecto_nestle.urls'

# Configuración de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(RUTA_BASE, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'productos.context_processors.carrito_contexto',
            ],
        },
    },
]

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(RUTA_BASE, 'db.sqlite3'),
    }
}

# Validación de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(RUTA_BASE, 'staticfiles')
STATICFILES_DIRS = [os.path.join(RUTA_BASE, 'static')]

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(RUTA_BASE, 'media')

# Tipo de campo de clave primaria por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CONFIGURACIÓN DE CONEXIÓN A ODOO
# ============================================

# Me establezco los parámetros de conexión a Odoo vía XML-RPC
ODOO_CONFIG = {
    'host': 'localhost',
    'puerto': 8069,
    'base_datos': 'odoo_test',
    'usuario_admin': 'admin',
    'contrasena_admin': 'admin',
}

# URL base de Odoo para XML-RPC
ODOO_URL_XMLRPC = f"http://{ODOO_CONFIG['host']}:{ODOO_CONFIG['puerto']}"