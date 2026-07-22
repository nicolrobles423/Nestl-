from django.urls import path
from . import views

# Me establezco el namespace de la app
app_name = 'productos'

# Me defino las rutas disponibles
urlpatterns = [
    # Catálogo principal con filtros
    path('', views.catalogo_productos, name='catalogo'),
    
    # Detalle de un producto específico
    path('producto/<int:id_producto>/', views.detalle_producto, name='detalle'),
    
    # Filtro por marca
    path('marca/<int:id_marca>/', views.productos_por_marca, name='por_marca'),
    
    # Filtro por categoría
    path('categoria/<int:id_categoria>/', views.productos_por_categoria, name='por_categoria'),

    # Carrito de compras
    path('carrito/', views.ver_carrito, name='carrito'),
    path('carrito/agregar/<int:id_producto>/', views.agregar_al_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:id_producto>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:id_producto>/', views.eliminar_del_carrito, name='eliminar_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),

    # Checkout: crea el pedido en Odoo
    path('checkout/', views.finalizar_compra, name='checkout'),

    # Cuenta de usuario
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
]
