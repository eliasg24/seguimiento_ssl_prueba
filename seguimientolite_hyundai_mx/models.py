from tabnanny import verbose

from django.db import models

# Historial


class HistorialEvidencias(models.Model):
    archivo = models.ImageField()
    hora_subida = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "historial_evidencias"


# Informacion general


class Informacion(models.Model):
    no_orden = models.CharField(max_length=30, primary_key=True)
    vin = models.CharField(max_length=30, blank=True, null=True)
    kilometraje = models.CharField(max_length=20, blank=True, null=True)
    asesor = models.CharField(max_length=100, blank=True, null=True)
    cliente = models.CharField(max_length=500, blank=True, null=True)
    telefono = models.CharField(max_length=25, blank=True, null=True)
    email = models.CharField(max_length=150, blank=True, null=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    vehiculo = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=120, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora_ingreso = models.DateTimeField(blank=True, null=True)
    tecnico = models.CharField(max_length=250, blank=True, null=True)
    id_hd = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "informacion"


class VInformacion(models.Model):
    no_orden = models.CharField(max_length=100, primary_key=True)
    vin = models.CharField(max_length=100, blank=True, null=True)
    kilometraje = models.CharField(max_length=100, blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    cliente = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    placas = models.CharField(max_length=100, blank=True, null=True)
    vehiculo = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora_ingreso = models.DateTimeField(blank=True, null=True)
    tecnico = models.CharField(max_length=250, blank=True, null=True)
    id_hd = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_informacion"


class VTecnicos(models.Model):
    id_empleado = models.CharField(
        db_column="ID_EMPLEADO", max_length=10, primary_key=True
    )  # Field name made lowercase.
    id_tipo_empleado = models.CharField(
        db_column="ID_TIPO_EMPLEADO", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    nombre_empleado = models.CharField(
        db_column="NOMBRE_EMPLEADO", max_length=60, blank=True, null=True
    )  # Field name made lowercase.
    nivel = models.CharField(db_column="NIVEL", max_length=1, blank=True, null=True)  # Field name made lowercase.
    bahia = models.IntegerField(db_column="BAHIA", blank=True, null=True)  # Field name made lowercase.
    express = models.BooleanField(db_column="EXPRESS", blank=True, null=True)  # Field name made lowercase.
    color_tecnico = models.CharField(
        db_column="COLOR_TECNICO", max_length=25, blank=True, null=True
    )  # Field name made lowercase.
    hora_ent_lv = models.CharField(
        db_column="HORA_ENT_LV", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_sal_lv = models.CharField(
        db_column="HORA_SAL_LV", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_comer = models.CharField(
        db_column="HORA_COMER", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_ent_s = models.CharField(
        db_column="HORA_ENT_S", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_sal_s = models.CharField(
        db_column="HORA_SAL_S", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    id_asesor = models.CharField(
        db_column="ID_ASESOR", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    nombre_asesor = models.CharField(
        db_column="NOMBRE_ASESOR", max_length=50, blank=True, null=True
    )  # Field name made lowercase.
    no_emp_asesor = models.IntegerField(db_column="NO_EMP_ASESOR", blank=True, null=True)  # Field name made lowercase.
    jefe_taller = models.BooleanField(db_column="JEFE_TALLER", blank=True, null=True)  # Field name made lowercase.
    hora_ent_d = models.CharField(
        db_column="HORA_ENT_D", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_sal_d = models.CharField(
        db_column="HORA_SAL_D", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_comer_s = models.CharField(
        db_column="HORA_COMER_S", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    hora_comer_d = models.CharField(
        db_column="HORA_COMER_D", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    id_empleado_bi = models.CharField(
        db_column="ID_EMPLEADO_BI", max_length=10, blank=True, null=True
    )  # Field name made lowercase.
    min_comer_lv = models.IntegerField(db_column="MIN_COMER_LV", blank=True, null=True)  # Field name made lowercase.
    min_comer_s = models.IntegerField(db_column="MIN_COMER_S", blank=True, null=True)  # Field name made lowercase.
    min_comer_d = models.IntegerField(db_column="MIN_COMER_D", blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = "v_tecnicos"


class VUsuarios(models.Model):
    cvegrupo = models.IntegerField(db_column="cveGrupo")  # Field name made lowercase.
    cveperfil = models.IntegerField(db_column="cvePerfil")  # Field name made lowercase.
    cveusuario = models.CharField(db_column="cveUsuario", max_length=15)  # Field name made lowercase.
    pass_field = models.CharField(
        db_column="Pass", max_length=100
    )  # Field name made lowercase. Field renamed because it was a Python reserved word.
    nombre = models.CharField(db_column="Nombre", max_length=150, blank=True, null=True)  # Field name made lowercase.
    correoe = models.CharField(db_column="correoE", max_length=100, blank=True, null=True)  # Field name made lowercase.
    color = models.CharField(db_column="Color", max_length=50, blank=True, null=True)  # Field name made lowercase.
    cveasesor = models.CharField(
        db_column="cveAsesor", max_length=20, blank=True, null=True
    )  # Field name made lowercase.

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_usuarios"


class Revisiones(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=150, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    guia_mantenimiento = models.FileField(upload_to="guias_mantenimiento", blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_revisiones"
        verbose_name_plural = "Revisiones"
        verbose_name = "Revisión"

    def __str__(self):
        return self.nombre


# Tecnico
class ListaItemsFamilias(models.Model):
    id = models.BigAutoField(primary_key=True)
    orden = models.IntegerField(blank=True, null=True)
    revision = models.ForeignKey(Revisiones, models.SET_NULL, blank=True, null=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=300, blank=True, null=True)
    descripcion_adicional = models.CharField(max_length=1000, blank=True, null=True)
    imagen = models.FileField(upload_to="lista_items_familias", blank=True, null=True)
    video = models.FileField(upload_to="lista_items_familias", blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_familias"
        verbose_name_plural = "Familias de Items"
        verbose_name = "Familia de Items"

    def __str__(self):
        return self.nombre + " - " + self.revision.nombre


class ListaItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    orden = models.IntegerField(blank=True, null=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    familia = models.ForeignKey(ListaItemsFamilias, on_delete=models.CASCADE, blank=True, null=True)
    multipuntos = models.BooleanField(blank=True, null=True)
    pagina = models.IntegerField(blank=True, null=True)
    revision = models.ForeignKey(Revisiones, null=True, on_delete=models.SET_NULL)
    g_x = models.IntegerField(blank=True, null=True)
    g_y = models.IntegerField(blank=True, null=True)
    y_x = models.IntegerField(blank=True, null=True)
    y_y = models.IntegerField(blank=True, null=True)
    r_x = models.IntegerField(blank=True, null=True)
    r_y = models.IntegerField(blank=True, null=True)
    no_aplica_x = models.IntegerField(blank=True, null=True)
    no_aplica_y = models.IntegerField(blank=True, null=True)
    si_x = models.IntegerField(blank=True, null=True)
    si_y = models.IntegerField(blank=True, null=True)
    no_x = models.IntegerField(blank=True, null=True)
    no_y = models.IntegerField(blank=True, null=True)
    modificado_x = models.IntegerField(blank=True, null=True)
    modificado_y = models.IntegerField(blank=True, null=True)
    valor_x = models.IntegerField(blank=True, null=True)
    valor_y = models.IntegerField(blank=True, null=True)
    unidad = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_tecnico"
        verbose_name_plural = "Lista de Items"
        verbose_name = "Item"

    def __str__(self):
        return self.descripcion


class Items(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    item = models.ForeignKey(ListaItems, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=25, blank=True, null=True)
    comentarios = models.CharField(max_length=500, blank=True, null=True)
    valor = models.CharField(max_length=50, blank=True, null=True)
    bateria_estado = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=None)
    bateria_nivel = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, default=None)
    cambiado = models.BooleanField(default=0)
    tecnico = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora_fin = models.DateTimeField(auto_now_add=True)
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "actividades_tecnico"


class ActividadesTecnicoCaptura(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_orden = models.CharField(max_length=10, blank=True, null=True)
    item = models.CharField(max_length=100, blank=True, null=True)
    valor = models.CharField(max_length=300, blank=True, null=True)
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "actividades_tecnico_captura"


class Evidencias(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    item = models.ForeignKey(Items, null=True, on_delete=models.SET_NULL)
    evidencia = models.CharField(max_length=100, blank=True, null=True)
    fecha_hora_fin = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "actividades_tecnico_medios"


class ListaItemsTecnicoCaptura(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=400, blank=True, null=True)
    x = models.IntegerField(blank=True, null=True)
    y = models.IntegerField(blank=True, null=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    line_size = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_items_tecnico_captura"
        verbose_name_plural = "Lista de Items de Captura"
        verbose_name = "Item de Captura"

    def __str__(self):
        return self.nombre


class VOperacionesTecnico(models.Model):
    id = models.BigIntegerField(blank=True, null=False, primary_key=True)
    id_hd = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    tecnico = models.CharField(max_length=60, blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    fecha_llegada = models.DateField(blank=True, null=True)
    hora_promesa = models.DateTimeField(blank=True, null=True)
    cliente = models.CharField(max_length=200, blank=True, null=True)
    servicio_capturado = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_operaciones_tecnico"


# Refacciones
class TiposRefacciones(models.Model):
    id = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_tipos_refacciones"


class Refacciones(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=50, blank=True, null=True)
    item = models.ForeignKey(Items, null=True, on_delete=models.SET_NULL)
    nombre = models.CharField(max_length=250, blank=True, null=True)
    no_parte = models.CharField(max_length=50, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True)
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    porcentaje_iva = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    subtotal_iva = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    existencia = models.CharField(max_length=10, blank=True, null=True)
    localizacion = models.CharField(max_length=50, blank=True, null=True)
    tipo = models.ForeignKey(TiposRefacciones, null=True, on_delete=models.SET_NULL)
    fecha_hora_fin = models.DateTimeField(auto_now_add=True)
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "actividades_refacciones"


class VOperacionesRefacciones(models.Model):
    fecha_ingreso = models.DateField(blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, primary_key=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    tecnico = models.CharField(max_length=60, blank=True, null=True)
    fin_tecnico = models.DateTimeField(blank=True, null=True)
    modificacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_operaciones_refacciones"


# MANO DE OBRA
class TiposCargos(models.Model):
    id = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "lista_tipos_cargos"


class ManoDeObra(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=50, blank=True, null=True)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    item = models.ForeignKey(Items, null=True, on_delete=models.SET_NULL)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    cantidad_uts = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    precio_ut = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    porcentaje_iva = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    subtotal_iva = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    cargo = models.ForeignKey(TiposCargos, null=True, on_delete=models.SET_NULL)
    fecha_hora_fin = models.DateTimeField(auto_now_add=True)
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "actividades_mano_de_obra"


# Calidad


class ActividadesCalidad(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    item = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "actividades_calidad"


# Asesor


class ActividadesAsesorFirmas(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.CharField(max_length=50, blank=True, null=True)
    no_orden = models.CharField(max_length=50, blank=True, null=True)
    firma = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora_fin = models.DateTimeField(auto_now_add=True)
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "actividades_asesor_firmas"


class VOperacionesAsesorAlt(models.Model):
    no_orden = models.CharField(max_length=25, primary_key=True)
    placas = models.CharField(max_length=10, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    vehiculo = models.CharField(max_length=250, blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_operaciones_asesor_alt"


class TiposCotizacion(models.Model):
    id = models.BigAutoField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = "lista_tipos_cotizacion"


class CotizacionPdf(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    tipo = models.ForeignKey(TiposCotizacion, null=True, on_delete=models.SET_NULL)
    fecha_hora_fin = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "actividades_cotizacion_pdf"


# Cliente


class Autorizaciones(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    item = models.ForeignKey(Items, null=True, on_delete=models.SET_NULL)
    autorizacion = models.BooleanField(default=0)
    pagado = models.BooleanField(default=0)
    fecha_hora_fin = models.DateTimeField(auto_now_add=True)
    fecha_hora_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = "actividades_cliente"


class VSeguimientoEvidencia(models.Model):
    id = models.BigIntegerField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    tecnico = models.CharField(max_length=50, blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    id_item = models.CharField(max_length=50, blank=True, null=True)
    item = models.CharField(max_length=250, blank=True, null=True)
    estado = models.CharField(max_length=25, blank=True, null=True)
    comentarios = models.CharField(max_length=500, blank=True, null=True)
    fecha_hora_inicio = models.DateTimeField(blank=True, null=True)
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)
    fecha_hora_actualizacion = models.DateTimeField(blank=True, null=True)
    no_cotizacion = models.CharField(max_length=20, blank=True, null=True)
    valor = models.CharField(max_length=50, blank=True, null=True)
    cambiado = models.BooleanField(blank=True, null=True)
    evidencia = models.CharField(max_length=200)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_seguimiento_evidencia"


# Logs


class LogCliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    cliente = models.BinaryField(blank=True, null=True)
    fecha_hora_visita = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "log_cliente"


class LogEnvios(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    medio = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora_envio = models.DateTimeField(blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    correo = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = True
        db_table = "log_envios"


class LogGeneral(models.Model):
    id = models.BigAutoField(primary_key=True)
    no_orden = models.CharField(max_length=25, blank=True, null=True)
    inicio_tecnico = models.DateTimeField(blank=True, null=True)
    fin_tecnico = models.DateTimeField(blank=True, null=True)
    inicio_refacciones = models.DateTimeField(blank=True, null=True)
    fin_refacciones = models.DateTimeField(blank=True, null=True)
    inicio_mano_de_obra = models.DateTimeField(blank=True, null=True)
    fin_mano_de_obra = models.DateTimeField(blank=True, null=True)
    inicio_asesor = models.DateTimeField(blank=True, null=True)
    fin_asesor = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = "log_general"


# DMS


class VInterfazDms(models.Model):
    id = models.BigIntegerField(primary_key=True)
    numero = models.BigIntegerField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    bodega = models.IntegerField(blank=True, null=True)
    clase_operacion = models.CharField(max_length=10, blank=True, null=True)
    operacion = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    valor_unidad = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    tiempo = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    porcentaje_iva = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=18, decimal_places=0, blank=True, null=True)
    nit = models.CharField(max_length=50, blank=True, null=True)
    nombres = models.CharField(max_length=150, blank=True, null=True)
    direccion = models.CharField(max_length=250, blank=True, null=True)
    telefono_1 = models.CharField(max_length=50, blank=True, null=True)
    serie = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=20, blank=True, null=True)
    placa = models.CharField(max_length=50, blank=True, null=True)
    nombre_vendedor = models.CharField(max_length=100, blank=True, null=True)
    descripcion_mo = models.CharField(max_length=150, blank=True, null=True)
    descripcion_ref = models.CharField(max_length=150, blank=True, null=True)
    vehiculo = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "v_interfaz_dms"


class ListaItemsAdicionales(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_item = models.BigIntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    familia = models.IntegerField(blank=True, null=True)
    orden = models.IntegerField(blank=True, null=True)
    costo_repuestos = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    costo_mo = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    descuento = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "lista_items_adicionales"


class ActividadesAdicionales(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_hd = models.BigIntegerField(blank=True, null=True)
    no_orden = models.CharField(max_length=50, blank=True, null=True)
    item = models.CharField(max_length=250, blank=True, null=True)
    id_item = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    cantidad = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    nombre = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.CharField(max_length=50, blank=True, null=True)
    no_parte = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    total_iva = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    porcentaje_descuento = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    existencia = models.CharField(max_length=10, blank=True, null=True)
    localizacion = models.CharField(max_length=50, blank=True, null=True)
    fecha_hora_fin = models.DateTimeField(blank=True, null=True)
    fecha_hora_actualizacion = models.DateTimeField(blank=True, null=True)
    uts = models.IntegerField(blank=True, null=True)
    monto_refaccion = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    monto_mo = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "actividades_adicionales"


# ARCHIVOS FIRMAS


class ArchivoFirmasTecnico(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_tecnico = models.CharField(null=True, blank=True, max_length=50)
    imagen_firma = models.FileField(upload_to="firmas_tecnico", blank=True, null=True)


class ArchivosFirmasAsesor(models.Model):
    id = models.BigAutoField(primary_key=True)
    id_asesor = models.CharField(null=True, blank=True, max_length=50)
    imagen_firma = models.FileField(upload_to="firmas_asesor", blank=True, null=True)


## Models para agregar inspección a pdf multipuntos


class VRevisionCalidadRi(models.Model):
    id_calidad = models.IntegerField()
    id_sector = models.IntegerField()
    id_item = models.IntegerField()
    id_opcion = models.IntegerField()
    opcion = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200, blank=True, null=True)
    no_orden = models.CharField(max_length=20)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_revision_calidad_ri"


class VPantallaRecepcion(models.Model):
    id = models.BigIntegerField(primary_key=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    hora_asesor = models.CharField(max_length=5, blank=True, null=True)
    hora_recepcion = models.CharField(max_length=5, blank=True, null=True)
    tipo_llegada = models.CharField(max_length=5)
    placas = models.CharField(max_length=10, blank=True, null=True)
    cliente = models.CharField(max_length=25, blank=True, null=True)
    servicio_capturado = models.CharField(max_length=25, blank=True, null=True)
    vehiculo = models.CharField(max_length=20, blank=True, null=True)
    estatus_orden = models.CharField(max_length=30)
    tipo_cliente = models.CharField(max_length=25, blank=True, null=True)
    numcita = models.CharField(db_column="NUMCITA", max_length=25)  # Field name made lowercase.
    cita = models.IntegerField()

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "v_pantalla_recepcion"


class KpisGeneral(models.Model):
    no_orden = models.CharField(primary_key=True, max_length=25)
    no_placas = models.CharField(max_length=10, blank=True, null=True)
    fecha_hora_entrada = models.DateTimeField(blank=True, null=True)
    fecha_hora_salida = models.DateTimeField(blank=True, null=True)
    kilometraje = models.IntegerField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    asesor = models.CharField(max_length=150, blank=True, null=True)
    vin = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=250, blank=True, null=True)
    year_vehiculo = models.IntegerField(blank=True, null=True)
    cliente = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    multipuntos = models.IntegerField()
    tecnico = models.CharField(max_length=60, blank=True, null=True)
    inmediato = models.IntegerField(blank=True, null=True)
    buen_estado = models.IntegerField(blank=True, null=True)
    recomendado = models.IntegerField(blank=True, null=True)
    videos = models.IntegerField(blank=True, null=True)
    fotos = models.IntegerField(blank=True, null=True)
    cotizacion = models.IntegerField()
    envio_cotizacion = models.IntegerField()
    envio_email = models.IntegerField(blank=True, null=True)
    envio_whatsapp = models.IntegerField(blank=True, null=True)
    vista_cliente = models.IntegerField()
    autorizados = models.IntegerField(blank=True, null=True)
    detalle_items_autorizados = models.TextField(blank=True, null=True)
    # detalle_refacciones_autorizadas = models.TextField(blank=True, null=True)
    # detalle_items_no_autorizados = models.TextField(blank=True, null=True)
    # detalle_refacciones_no_autorizadas = models.TextField(blank=True, null=True)
    # total_cotizado_mo = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    # total_cotizado_repuestos = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    # total_cotizado = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    monto_autorizado = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    # monto_autorizado_refacciones = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    # monto_autorizado_mo = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    # no_autorizados = models.IntegerField(blank=True, null=True)
    monto_no_autorizado = models.DecimalField(max_digits=38, decimal_places=2, blank=True, null=True)
    porcentaje_autorizado = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    porcentaje_no_autorizado = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False  # Created from a view. Don't remove.
        db_table = "kpis_general"
