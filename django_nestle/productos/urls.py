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

    # Historial de pedidos y facturas del cliente
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:id_pedido>/factura/', views.descargar_factura, name='descargar_factura'),

    # Cuenta de usuario
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # Panel administrativo: página de inicio con accesos a los demás paneles
    path('panel/', views.panel_inicio, name='panel_inicio'),

    # Panel administrativo de productos (rol administrador)
    path('panel/productos/', views.panel_productos, name='panel_productos'),
    path('panel/productos/nuevo/', views.panel_producto_form, name='panel_producto_nuevo'),
    path('panel/productos/<int:id_producto>/editar/', views.panel_producto_form, name='panel_producto_editar'),
    path('panel/productos/<int:id_producto>/eliminar/', views.panel_producto_eliminar, name='panel_producto_eliminar'),
    path('panel/productos/<int:id_producto>/archivar/', views.panel_producto_archivar, name='panel_producto_archivar'),

    # Panel de pedidos (rol administrador): ve todos los pedidos del sistema
    path('panel/pedidos/', views.panel_pedidos, name='panel_pedidos'),

    # Panel de usuarios (rol administrador): asigna roles
    path('panel/usuarios/', views.panel_usuarios, name='panel_usuarios'),
    path('panel/usuarios/<int:id_perfil>/rol/', views.panel_usuario_cambiar_rol, name='panel_usuario_cambiar_rol'),

    # Panel de stock (rol bodeguero): ve y ajusta el inventario
    path('panel/stock/', views.panel_stock, name='panel_stock'),
    path('panel/stock/<int:id_producto>/ajustar/', views.panel_stock_ajustar, name='panel_stock_ajustar'),
]
