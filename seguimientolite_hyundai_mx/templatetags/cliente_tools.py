from django import template

register = template.Library()


@register.filter
def tiene_evidencia(item, evidencias):
    tiene_evidencias = False
    for evidencia in evidencias:
        if evidencia.item == item:
            tiene_evidencias = True
    return tiene_evidencias
