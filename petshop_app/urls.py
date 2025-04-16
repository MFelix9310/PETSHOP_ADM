from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # URLs para Productos
    path('productos/', views.ProductoListView.as_view(), name='producto-list'),
    path('productos/nuevo/', views.ProductoCreateView.as_view(), name='producto-create'),
    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto-update'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto-delete'),
    path('productos/<int:pk>/vender/', views.venta_rapida, name='venta-rapida'),
    path('productos/buscar-por-codigo/', views.buscar_producto_por_codigo, name='buscar-producto-codigo'),
    
    # URLs para Servicios
    path('servicios/', views.ServicioListView.as_view(), name='servicio-list'),
    path('servicios/nuevo/', views.ServicioCreateView.as_view(), name='servicio-create'),
    path('servicios/<int:pk>/editar/', views.ServicioUpdateView.as_view(), name='servicio-update'),
    path('servicios/<int:pk>/eliminar/', views.ServicioDeleteView.as_view(), name='servicio-delete'),
    
    # URLs para Ventas de Productos
    path('ventas/productos/', views.VentaProductoListView.as_view(), name='venta-producto-list'),
    path('ventas/productos/nueva/', views.VentaProductoCreateView.as_view(), name='venta-producto-create'),
    
    # URLs para Servicios Realizados
    path('servicios/realizados/', views.ServicioRealizadoListView.as_view(), name='servicio-realizado-list'),
    path('servicios/realizados/nuevo/', views.ServicioRealizadoCreateView.as_view(), name='servicio-realizado-create'),
    
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
] 