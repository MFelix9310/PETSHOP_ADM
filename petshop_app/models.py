from django.db import models
from django.utils import timezone

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True, help_text="Código único del producto", null=True, blank=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"[{self.codigo}] {self.nombre}"

class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_estimada = models.PositiveIntegerField(help_text="Duración estimada en minutos")
    fecha_ingreso = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nombre

class VentaProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(default=timezone.now)
    
    def total(self):
        return self.precio_unitario * self.cantidad
    
    def __str__(self):
        return f"Venta de {self.cantidad} {self.producto.nombre}"

class ServicioRealizado(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    fecha_realizado = models.DateTimeField(default=timezone.now)
    precio_cobrado = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Servicio {self.servicio.nombre} realizado"
