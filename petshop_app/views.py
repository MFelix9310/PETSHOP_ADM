from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.db.models import Sum, Count
from django.contrib import messages
from .models import Producto, Servicio, VentaProducto, ServicioRealizado
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, FormView
from .db_sqlalchemy import agregar_producto, obtener_productos, obtener_producto_por_codigo, actualizar_stock as actualizar_stock_sqlalchemy, eliminar_producto as eliminar_producto_sqlalchemy
from decimal import Decimal
from django.http import JsonResponse
from django import forms

def home(request):
    return render(request, 'petshop_app/home.html')

# Vistas para Productos
class ProductoListView(ListView):
    model = Producto
    template_name = 'petshop_app/producto_list.html'
    context_object_name = 'productos'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadimos los productos de SQLAlchemy
        context['productos_sqlalchemy'] = obtener_productos()
        return context

class ProductoCreateView(CreateView):
    model = Producto
    template_name = 'petshop_app/producto_form.html'
    fields = ['nombre', 'codigo', 'descripcion', 'precio', 'stock']
    
    def form_valid(self, form):
        # Guardar en la base de datos de Django
        response = super().form_valid(form)
        
        # También guardamos en SQLAlchemy
        try:
            producto = form.instance
            agregar_producto(
                nombre=producto.nombre,
                codigo=producto.codigo,
                descripcion=producto.descripcion,
                precio=float(producto.precio),
                stock=producto.stock
            )
            messages.success(self.request, f"Producto '{producto.nombre}' guardado en ambas bases de datos.")
        except Exception as e:
            messages.error(self.request, f"Error al guardar en SQLAlchemy: {str(e)}")
        
        return response
    
    def get_success_url(self):
        return reverse('producto-list')

class ProductoUpdateView(UpdateView):
    model = Producto
    template_name = 'petshop_app/producto_form.html'
    fields = ['nombre', 'codigo', 'descripcion', 'precio', 'stock']
    
    def form_valid(self, form):
        response = super().form_valid(form)
        producto = form.instance
        
        # También actualizamos en SQLAlchemy
        try:
            # Primero eliminamos el registro viejo
            eliminar_producto_sqlalchemy(producto.codigo)
            # Luego lo creamos de nuevo
            agregar_producto(
                nombre=producto.nombre,
                codigo=producto.codigo,
                descripcion=producto.descripcion,
                precio=float(producto.precio),
                stock=producto.stock
            )
            messages.success(self.request, f"Producto '{producto.nombre}' actualizado en ambas bases de datos.")
        except Exception as e:
            messages.error(self.request, f"Error al actualizar en SQLAlchemy: {str(e)}")
        
        return response
    
    def get_success_url(self):
        return reverse('producto-list')

class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'petshop_app/producto_confirm_delete.html'
    success_url = reverse_lazy('producto-list')
    
    def delete(self, request, *args, **kwargs):
        producto = self.get_object()
        codigo = producto.codigo
        
        # Eliminar en base de datos de Django
        response = super().delete(request, *args, **kwargs)
        
        # También eliminar en SQLAlchemy
        try:
            eliminar_producto_sqlalchemy(codigo)
            messages.success(request, f"Producto '{producto.nombre}' eliminado de ambas bases de datos.")
        except Exception as e:
            messages.error(request, f"Error al eliminar en SQLAlchemy: {str(e)}")
        
        return response

# Vistas para Servicios
class ServicioListView(ListView):
    model = Servicio
    template_name = 'petshop_app/servicio_list.html'
    context_object_name = 'servicios'

class ServicioCreateView(CreateView):
    model = Servicio
    template_name = 'petshop_app/servicio_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'duracion_estimada']
    
    def get_success_url(self):
        return reverse('servicio-list')

class ServicioUpdateView(UpdateView):
    model = Servicio
    template_name = 'petshop_app/servicio_form.html'
    fields = ['nombre', 'descripcion', 'precio', 'duracion_estimada']
    
    def get_success_url(self):
        return reverse('servicio-list')

class ServicioDeleteView(DeleteView):
    model = Servicio
    template_name = 'petshop_app/servicio_confirm_delete.html'
    success_url = reverse_lazy('servicio-list')
    
    def delete(self, request, *args, **kwargs):
        servicio = self.get_object()
        
        # Eliminar en base de datos de Django
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Servicio '{servicio.nombre}' eliminado correctamente.")
        
        return response

# Vistas para Ventas de Productos
class VentaProductoListView(ListView):
    model = VentaProducto
    template_name = 'petshop_app/venta_producto_list.html'
    context_object_name = 'ventas'

# Formulario personalizado para buscar productos por código
class BuscarProductoForm(forms.Form):
    codigo = forms.CharField(max_length=50, required=False, label="Código del Producto")

# Formulario personalizado para venta rápida
class VentaRapidaForm(forms.Form):
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad")

class VentaProductoCreateView(CreateView):
    model = VentaProducto
    template_name = 'petshop_app/venta_producto_form.html'
    fields = ['producto', 'cantidad', 'precio_unitario']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buscar_form'] = BuscarProductoForm()
        return context
    
    def form_valid(self, form):
        venta = form.save(commit=False)
        producto = venta.producto
        
        # Actualizar stock
        if producto.stock >= venta.cantidad:
            producto.stock -= venta.cantidad
            producto.save()
            
            # También actualizar en SQLAlchemy
            try:
                actualizar_stock_sqlalchemy(producto.codigo, producto.stock)
            except Exception as e:
                messages.warning(self.request, f"Venta registrada pero hubo un error al actualizar en SQLAlchemy: {str(e)}")
            
            return super().form_valid(form)
        else:
            messages.error(self.request, "No hay suficiente stock disponible.")
            return self.form_invalid(form)
    
    def get_success_url(self):
        return reverse('venta-producto-list')

def venta_rapida(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = VentaRapidaForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            
            if producto.stock >= cantidad:
                # Actualizar stock
                producto.stock -= cantidad
                producto.save()
                
                # Registrar venta
                venta = VentaProducto.objects.create(
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )
                
                # Actualizar en SQLAlchemy
                try:
                    actualizar_stock_sqlalchemy(producto.codigo, producto.stock)
                    messages.success(request, f"Venta de {cantidad} unidades de '{producto.nombre}' registrada correctamente.")
                except Exception as e:
                    messages.error(request, f"Error al actualizar en SQLAlchemy: {str(e)}")
                
                return redirect('producto-list')
            else:
                messages.error(request, f"No hay suficiente stock. Disponible: {producto.stock}")
                return redirect('venta-rapida', pk=producto.pk)
    else:
        form = VentaRapidaForm()
    
    return render(request, 'petshop_app/venta_rapida_form.html', {
        'form': form,
        'producto': producto
    })

def buscar_producto_por_codigo(request):
    if request.method == 'GET' and 'codigo' in request.GET:
        codigo = request.GET.get('codigo')
        try:
            producto = Producto.objects.get(codigo=codigo)
            return JsonResponse({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': float(producto.precio),
                'stock': producto.stock
            })
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    return JsonResponse({'error': 'Solicitud inválida'}, status=400)

# Vistas para Servicios Realizados
class ServicioRealizadoListView(ListView):
    model = ServicioRealizado
    template_name = 'petshop_app/servicio_realizado_list.html'
    context_object_name = 'servicios_realizados'

class ServicioRealizadoCreateView(CreateView):
    model = ServicioRealizado
    template_name = 'petshop_app/servicio_realizado_form.html'
    fields = ['servicio', 'precio_cobrado', 'observaciones']
    
    def get_success_url(self):
        return reverse('servicio-realizado-list')

# Dashboard
class DashboardView(TemplateView):
    template_name = 'petshop_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Ventas de productos
        ventas_productos = VentaProducto.objects.filter(
            fecha_venta__month=timezone.now().month,
            fecha_venta__year=timezone.now().year
        )
        
        # Servicios realizados
        servicios_realizados = ServicioRealizado.objects.filter(
            fecha_realizado__month=timezone.now().month,
            fecha_realizado__year=timezone.now().year
        )
        
        # Total de ventas
        total_ventas = sum(venta.total() for venta in ventas_productos)
        
        # Total de servicios
        total_servicios = servicios_realizados.aggregate(Sum('precio_cobrado'))['precio_cobrado__sum'] or 0
        
        context['total_ventas'] = total_ventas
        context['total_servicios'] = total_servicios
        context['total_ingresos'] = total_ventas + total_servicios
        context['productos_mas_vendidos'] = VentaProducto.objects.values('producto__nombre').annotate(
            total=Sum('cantidad')).order_by('-total')[:5]
        context['servicios_mas_realizados'] = ServicioRealizado.objects.values('servicio__nombre').annotate(
            total=Count('id')).order_by('-total')[:5]
        
        return context
