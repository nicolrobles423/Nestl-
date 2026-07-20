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
]
