from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def svg_familia(familia):
    dispatch = {
        "Pito": "pito.svg",
        "Luces": "luces.svg",
        "Llantas Delanteras": "llantas.svg",
        "Llantas Traseras": "llantas.svg",
    }
    return dispatch.get(familia)


@register.filter
@stringfilter
def svg_item(item):
    dispatch = {
        "Aceite Motor": "aceite_motor.svg",
        "Batería": "bateria.svg",
        "Derecha-Estado": "llantas.svg",
        "Derecha-Presión": "llantas.svg",
        "Derecha-Labrado": "llantas.svg",
        "Estado": "pito.svg",
        "Izquierda-Estado": "llantas.svg",
        "Izquierda-Presion": "llantas.svg",
        "Izquierda-Labrado": "llantas.svg",
        "Filtro Aire Motor": "filtro_aire_motor.svg",
        "Frenos": "frenos.svg",
        "Frontales-Principal": "luces.svg",
        "Frontales-Direccionales": "luces.svg",
        "Frontales-Exploradoras": "luces.svg",
        "Traseras-Principal": "luces.svg",
        "Traseras-Direccionales": "luces.svg",
        "Traseras-Exploradoras": "luces.svg",
        "Internas-Principal": "luces.svg",
        "Limpiaparabrisas": "limpiaparabrisas.svg",
        "Pastillas Freno Delanteras": "pastilla_frenos.svg",
        "Pastillas Freno Traseras": "pastilla_frenos.svg",
        "Plumillas": "plumillas.svg",
        "Refrigerante Motor": "refrigerante_motor.svg",
    }
    return dispatch.get(item)
