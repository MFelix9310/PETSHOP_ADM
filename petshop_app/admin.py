from django.contrib import admin
from .models import Producto, Servicio, VentaProducto, ServicioRealizado

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'fecha_ingreso')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_ingreso',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'fecha_ingreso')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('fecha_ingreso',)

@admin.register(VentaProducto)
class VentaProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'precio_unitario', 'total', 'fecha_venta')
    search_fields = ('producto__nombre',)
    list_filter = ('fecha_venta',)

@admin.register(ServicioRealizado)
class ServicioRealizadoAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'precio_cobrado', 'fecha_realizado')
    search_fields = ('servicio__nombre', 'observaciones')
    list_filter = ('fecha_realizado',)
