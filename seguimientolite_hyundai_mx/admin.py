from django.contrib import admin
from .models import *


@admin.register(ListaItems)
class ListaItemsAdmin(admin.ModelAdmin):
    pass


@admin.register(ListaItemsFamilias)
class ListaItemsFamiliasAdmin(admin.ModelAdmin):
    pass


@admin.register(Revisiones)
class RevisionesAdmin(admin.ModelAdmin):
    pass


@admin.register(ListaItemsTecnicoCaptura)
class ListaItemsTecnicoCapturaAdmin(admin.ModelAdmin):
    pass

@admin.register(ArchivoFirmasTecnico)
class ArchivoFirmasTecnicoAdmin(admin.ModelAdmin):
    pass

@admin.register(ArchivosFirmasAsesor)
class ArchivoFirmasAsesorAdmin(admin.ModelAdmin):
    pass