from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Añade una clase CSS al widget de un campo de formulario
    """
    return value.as_widget(attrs={'class': arg}) 