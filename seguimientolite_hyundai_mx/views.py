import base64
import calendar
import hashlib
import json
import logging
import mimetypes
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import numpy as np
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMessage
from django.db.models import Avg, ExpressionWrapper, F, Sum, fields
from django.http import FileResponse, HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseRedirect
from Crypto.Cipher import AES
from base64 import urlsafe_b64encode, urlsafe_b64decode
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from excel_response.response import ExcelResponse
from PIL import Image
from webpush import send_user_notification

from django.views import View
from .models import *
from .pdf_calidad import get_pdf_calidad
from .pdf_cotizacion import cotizacion_pdf
from .pdf_cotizacion_simplificado import CotizacionSimplificada
from .utils import *

BASE_DIR = settings.BASE_DIR
HEADERS = {"Content-Type": "application/json"}


FOLDER_GUIAS_MANTENIMIENTO = Path(settings.MEDIA_ROOT / "guias_mantenimiento")
FOLDER_GUIAS_MANTENIMIENTO.mkdir(exist_ok=True, parents=True)

logger = logging.getLogger(__name__)


SECRET_KEY = b'4W2tHksBO1fWSJlq'  # Debes cambiar esto por una clave segura

def encrypt_number(number):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    padded_number = number + ' ' * (16 - len(number) % 16)  # Asegura que la longitud sea un múltiplo de 16 (para AES)
    encrypted_number = cipher.encrypt(padded_number.encode())
    return urlsafe_b64encode(encrypted_number).decode()

def decrypt_number(encrypted_number):
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    decrypted_number = cipher.decrypt(urlsafe_b64decode(encrypted_number.encode())).decode().strip()
    return decrypted_number

class Error404View(View):
    def get(self, request):
        return HttpResponseNotFound(render(request, 'seguimientolite_hyundai_mx/error_404.html'))

class Error500View(TemplateView):
    template_name = 'seguimientolite_hyundai_mx/error_404.html'

def handler404(request, exception):
    return render(request, 'seguimientolite_hyundai_mx/error_404.html', status=404)

def handler500(request):
    return render(request, 'seguimientolite_hyundai_mx/error_404.html', status=500)
# Login
def staff_login(request):
    context = {}
    form = AuthenticationForm()
    context["form"] = form
    context["titulo"] = "Seguimiento en Línea"
    context["settings"] = settings

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        # if form.is_valid():
        username = request.POST["username"]
        password = request.POST["password"]
        password_view = hashlib.sha1(bytes(password, encoding="utf-8"))
        user_in_local = authenticate(username=username, password=password)
        try:
            user_in_view = VUsuarios.objects.get(cveusuario=username, pass_field=str(password_view.hexdigest()).upper())
        except Exception:
            user_in_view = False

        if user_in_view and user_in_local:
            if user_in_view.cveperfil == 1:
                group = Group.objects.get_or_create(name="administradores")[0]
                user_in_local.groups.add(group)
                login(request, user_in_local)
                return redirect("ordenes")
            elif user_in_view.cveperfil == 2:
                group = Group.objects.get_or_create(name="asesores")[0]
                user_in_local.groups.add(group)
                login(request, user_in_local)
                return redirect("ordenes")
            elif user_in_view.cveperfil == 3:
                group = Group.objects.get_or_create(name="jefe de taller")[0]
                user_in_local.groups.add(group)
                login(request, user_in_local)
                return redirect("ordenes")
            elif user_in_view.cveperfil == 5:
                group = Group.objects.get_or_create(name="administradores")[0]
                user_in_local.groups.add(group)
                login(request, user_in_local)
                return redirect("ordenes")
            elif user_in_view.cveperfil == 7:
                group = Group.objects.get_or_create(name="refacciones")[0]
                user_in_local.groups.add(group)
                login(request, user_in_local)
                return redirect("refacciones")
            elif user_in_view.cveperfil == 13:
                group = Group.objects.get_or_create(name="asesores")[0]
                user_in_local.groups.add(group)
                login(request, user_in_local)
                return redirect("ordenes")
        elif user_in_view and not user_in_local:
            logger.info("Creando usuario")
            new_local_user = User.objects.create_user(
                username=username, password=password, first_name=user_in_view.nombre
            )
            login(request, new_local_user)
            return redirect("ordenes")
        else:
            if username == "admin":
                try:
                    new_local_user = User.objects.create_user(
                        username=username, password=password, first_name="Administrador", last_login=datetime.now()
                    )
                    group = Group.objects.get_or_create(name="administradores")[0]
                    new_local_user.groups.add(group)
                    login(request, new_local_user)
                    logger.info("Usuario admin creado")
                except Exception:
                    logger.info("Login de usuario local")
                    login(request, user_in_local)
                return redirect("ordenes")
            logger.info("Usuario no valido")
    return render(request, "seguimientolite_hyundai_mx/login.html", context)


# Técnico
def tecnico(request, id_tecnico, no_orden):
    """
    Pantalla de técnico
    """
    context = {}
    if request.method == "GET":
        # Logs
        try:
            log = LogGeneral.objects.get(no_orden=no_orden)
            if not log.fin_tecnico:
                log.inicio_tecnico = datetime.now()
                log.save()
        except Exception:
            LogGeneral.objects.create(no_orden=no_orden, inicio_tecnico=datetime.now())

        # Titulo de la pagina
        context["titulo"] = "Tecnico"
        context["settings"] = settings

        # Informacion de orden
        try:
            info = VInformacion.objects.filter(no_orden=no_orden).first()
            context["info"] = info
        except Exception as error:
            logger.warning(error)

        # Evidencias
        get_evidencias(context, no_orden)

        # Historial
        context["filas"] = Items.objects.filter(no_orden=no_orden).order_by("id")
        context["revisiones"] = Revisiones.objects.all()

        # Listado de items
        query_lista_items_tecnico = ListaItems.objects.exclude(familia=9)
        context["lista_items"] = query_lista_items_tecnico
        context["familias_items"] = ListaItemsFamilias.objects.exclude(id=9)
        context["items_extra_forms"] = (
            query_lista_items_tecnico.filter(valor_x__isnull=False).values_list("descripcion", flat=True).distinct()
        )

        # Recuperacion de estado para cada item
        context["items_guardados"] = Items.objects.filter(no_orden=no_orden)
        context["lista_items_guardados"] = Items.objects.filter(no_orden=no_orden).values_list("item", flat=True)

        # Comentarios hoja multipuntos
        try:
            context["comentario_inferior_guardado"] = ActividadesTecnicoCaptura.objects.get(
                no_orden=no_orden, item="comentario_inferior"
            ).valor
        except Exception:
            pass
        try:
            context["sintoma_guardado"] = ActividadesTecnicoCaptura.objects.get(no_orden=no_orden, item="sintoma").valor
        except Exception:
            pass
        try:
            context["raiz_guardado"] = ActividadesTecnicoCaptura.objects.get(no_orden=no_orden, item="raiz").valor
        except Exception:
            pass
        try:
            context["componente_guardado"] = ActividadesTecnicoCaptura.objects.get(
                no_orden=no_orden, item="componente"
            ).valor
        except Exception:
            pass

        # Crear o actalizar la informacion de la orden
        crear_actualizar_info(no_orden)

    if request.method == "POST":
        r = request.POST

        # Obtención de la informacion
        try:
            info = Informacion.objects.get(no_orden=no_orden)
        except Exception:
            pass

        notif = r.get("notif", None)

        # ACTUALIZAR ESTADO
        if r.get("update", None):
            try:
                update = Items.objects.get(no_orden=no_orden, item=r["item"])
                update.estado = str(r["estado"]).strip()
                update.fecha_hora_actualizacion = datetime.now()
                update.cambiado = True
                update.save()
                return HttpResponse(status=200)
            except Exception:
                pass

        # REMOVER REGISTRO
        if r.get("remove", None):
            try:
                Items.objects.get(no_orden=no_orden, item=r["item"]).delete()
                return HttpResponse(status=200)
            except Exception as error:
                logger.warning(error)

        # GUARDAR INSPECCION
        if r.get("inspeccion", None):
            # ITEMS
            logger.info("Guardado de item")
            item = ListaItems.objects.get(id=r["id_item"])
            item_defaults = {
                "estado": str(r["estado"]).strip(),
                "comentarios": str(r["comentario"]).strip(),
                "valor": str(r.get("valor")),
                "tecnico": id_tecnico,
                "bateria_estado": r.get("bateria_estado"),
                "bateria_nivel": r.get("bateria_nivel"),
            }
            item_tecnico, created = Items.objects.update_or_create(no_orden=no_orden, item=item, defaults=item_defaults)

            # EVIDENCIAS
            if r.get("evidencias[]", False):
                logger.info("Se encuentran evidencias")
                for filename in r.getlist("evidencias[]"):
                    try:
                        Evidencias.objects.create(
                            no_orden=no_orden,
                            item=item_tecnico,
                            evidencia=filename,
                        )
                        logger.info("Evidencia guardada")
                    except Exception as error:
                        logger.warning(error)
            if r.get("fp_id[]", False):
                save_filepond(r.getlist("fp_id[]"))

            # LOG
            log = LogGeneral.objects.get(no_orden=no_orden)
            if not log.fin_tecnico:
                log.fin_tecnico = datetime.now()
                log.save()

            # NOTIFICATIONS
            if notif:
                # Correo al contact center
                correos = settings.SEGUIMIENTOLITE_CORREOS_REFACCIONES + settings.SEGUIMIENTOLITE_CORREOS_GERENCIA
                nuevo_correo = NotificacionCorreo(
                    direccion_email=correos,
                    asunto=f"{settings.AGENCIA} - SSL - Llenado de Multipuntos {no_orden}",
                    titulo="Inspección multipuntos terminada",
                    mensaje=f"La inspección multipuntos de la orden {no_orden} ha finalizado.\nHaga click aquí para ver los detalles.\n<a href='https://{settings.DOMINIO}:{settings.PUERTO}{reverse_lazy('tecnico', kwargs={'id_tecnico': id_tecnico, 'no_orden': no_orden})}'>Ver detalles</a>",
                    preview="",
                )
                nuevo_correo.enviar()

                # Notificacion push al personal de refacciones
                push_groups(no_orden=no_orden, groups="repuestos")

            return HttpResponse(status=200)

        # GUARDAR COMENTARIOS DE DIAGNOSTICO
        if r.get("observaciones", None):
            try:
                update = ActividadesTecnicoCaptura.objects.get(no_orden=no_orden, item="comentario_inferior")
                update.valor = r["comentario_inferior"]
                update.save()
            except Exception:
                ActividadesTecnicoCaptura.objects.create(
                    no_orden=no_orden,
                    item="comentario_inferior",
                    valor=r["comentario_inferior"],
                )

            return HttpResponse(status=200)

        # Guardar items adicionales nuevos
        if r.get("items_adicionales_nuevos"):
            logger.info("Items adicionales nuevos")
            nuevos_items_adicionales = json.loads(r["items"])

            for item in nuevos_items_adicionales:
                # Se obtiene la familia otros
                familia_otros, creado = ListaItemsFamilias.objects.get_or_create(nombre="OTROS")
                if creado:
                    logger.info("Familia otros creado en lista items familias")
                else:
                    logger.info("Familia otros ya existe en lista items familias")

                # Se crea nuevo registro en la tabla de lista items
                nuevo_item, creado = ListaItems.objects.get_or_create(descripcion=item["nombre"], familia=familia_otros)
                if creado:
                    logger.info("Item creado en lista items")
                else:
                    logger.info("Item ya existe en lista items")

                # Se crea nuevo registro en la tabla de items tecnico
                item_tecnico_defaults = {
                    "estado": item["estado"],
                    "comentarios": item["comentarios"],
                    "tecnico": id_tecnico,
                }
                nuevo_item_tecnico, creado = Items.objects.update_or_create(
                    no_orden=no_orden, item=nuevo_item, defaults=item_tecnico_defaults
                )
                if creado:
                    logger.info("Item creado en actividades tecnico")
                else:
                    logger.info("Item ya existe en actividades tecnico")

                # Evidencias
                if item.get("evidencias"):
                    logger.info("Se encuentran evidencias")
                    for filename in item["evidencias"]:
                        try:
                            Evidencias.objects.create(
                                no_orden=no_orden,
                                item=nuevo_item_tecnico,
                                evidencia=filename,
                            )
                            logger.info("Evidencia guardada")
                        except Exception as error:
                            logger.warning(error)
                if item.get("fp_id"):
                    save_filepond(item["fp_id"])

            return HttpResponse(status=200)

    return render(request, "seguimientolite_hyundai_mx/tecnico.html", context)


# Listado de refacciones
def refacciones(request):
    context = {}

    context["filas"] = []
    context["titulo"] = "Repuestos"
    context["settings"] = settings

    # Verificación de login
    grupos = request.user.groups.values_list("name", flat=True)
    if not request.user.is_authenticated or "cliente" in grupos:
        return redirect("login")
    notificaciones_push(request, context)

    query_refacciones = VOperacionesRefacciones.objects.order_by("-fecha_ingreso")

    # Creación de tabla
    no_ordenes = query_refacciones.values_list("no_orden", flat=True).distinct()

    # Queries generales
    query_tecnico = Items.objects.filter(no_orden__in=no_ordenes)

    for no_orden in no_ordenes.iterator():
        info = query_refacciones.filter(no_orden=no_orden).first()
        if info:
            inmediatos = query_tecnico.filter(no_orden=no_orden, estado="Inmediato").count()
            recomendados = query_tecnico.filter(no_orden=no_orden, estado="Recomendado").count()

            context["filas"].append(
                {
                    "no_orden": no_orden,
                    "vin": info.vin,
                    "placas": info.placas,
                    "vehiculo": info.vehiculo,
                    "asesor": info.asesor,
                    "tecnico": info.tecnico,
                    "fecha_ingreso": info.fecha_ingreso,
                    "fin_tecnico": info.fin_tecnico,
                    "modificacion": info.modificacion,
                    "inmediatos": inmediatos,
                    "recomendados": recomendados,
                }
            )
    return render(request, "seguimientolite_hyundai_mx/refacciones.html", context)


# Detalle de refacciones
def refacciones_detalle(request, no_orden):

    if request.method == "GET":
        context = {}
        context["titulo"] = "Repuestos"
        context["settings"] = settings

        grupos = request.user.groups.values_list("name", flat=True)
        if not request.user.is_authenticated or "cliente" in grupos:
            return redirect("staff_login")
        notificaciones_push(request, context)
        crear_actualizar_info(no_orden)
        get_evidencias(context, no_orden)

        # Log
        try:
            log = LogGeneral.objects.get(no_orden=no_orden)
            if not log.inicio_refacciones and not log.fin_refacciones:
                log.inicio_refacciones = datetime.now()
                log.save()
        except Exception:
            pass

        # Informacion de orden
        try:
            context["orden"] = Informacion.objects.get(no_orden=no_orden)
            context["tecnicos"] = VTecnicos.objects.all()
        except Exception as error:
            logger.warning(error)

        queryset_tecnico = Items.objects.filter(no_orden=no_orden)
        queryset_refacciones = Refacciones.objects.filter(no_orden=no_orden)

        context["items_tecnico"] = (
            queryset_tecnico.exclude(estado="Buen Estado").exclude(estado="Corregido").exclude(estado="No Aplica")
        )
        context["fin_tecnico"] = queryset_tecnico.first().fecha_hora_fin
        context["refacciones"] = queryset_refacciones
        context["iva"] = settings.SEGUIMIENTOLITE_IVA

        context["ubicaciones"] = settings.SEGUIMIENTOLITE_REFACCIONES_UBICACIONES

        return render(request, "seguimientolite_hyundai_mx/refacciones_detalle.html", context)

    if request.method == "POST":
        r = request.POST
        logger.debug(r)

        # Guardado de inspección
        if r.get("guardar_inspeccion"):
            refacciones = json.loads(r["refacciones"])
            logger.info("Guardado de inspeccion de refacciones")
            for refaccion in refacciones:
                # Log
                try:
                    log = LogGeneral.objects.get(no_orden=no_orden)
                    if not log.fin_refacciones:
                        log.fin_refacciones = datetime.now()
                        log.save()
                except Exception:
                    pass

                item = Items.objects.get(no_orden=no_orden, id=refaccion["item_id"])

                subtotal_no_descuento_iva = Decimal(refaccion["cantidad"]) * Decimal(refaccion["precio_unitario"])
                porcentaje_descuento = Decimal(refaccion["porcentaje_descuento"])

                defaults_refacciones = {
                    "nombre": refaccion["nombre"],
                    "cantidad": refaccion["cantidad"],
                    "precio_unitario": refaccion["precio_unitario"],
                    "porcentaje_descuento": porcentaje_descuento,
                    "subtotal": round(
                        subtotal_no_descuento_iva - ((subtotal_no_descuento_iva / 100) * porcentaje_descuento), 2
                    ),
                    "porcentaje_iva": settings.SEGUIMIENTOLITE_IVA,
                    "subtotal_iva": Decimal(refaccion["subtotal"]),
                    "existencia": refaccion["existencia"],
                    "localizacion": refaccion["localizacion"],
                }

                Refacciones.objects.update_or_create(
                    no_orden=no_orden, item=item, no_parte=refaccion["no_parte"], defaults=defaults_refacciones
                )

            # Correo al contact center para notificar el fin de la inspeccion
            correos = settings.SEGUIMIENTOLITE_CORREOS_MANO_DE_OBRA + settings.SEGUIMIENTOLITE_CORREOS_GERENCIA
            nuevo_correo = NotificacionCorreo(
                direccion_email=correos,
                asunto=f"{settings.AGENCIA} - SSL - Llenado de Refacciones {no_orden}",
                titulo="Inspección de refacciones terminada",
                mensaje=f"La inspección de refacciones de la orden {no_orden} ha finalizado.\nHaga click aquí para ver los detalles.\n<a href='https://{settings.DOMINIO}:{settings.PUERTO}{reverse_lazy('refacciones_detalle', kwargs={'no_orden': no_orden})}'>Ver detalles</a>",
                preview="",
            )
            nuevo_correo.enviar()

            # Notificacion push al personal de mano de obra
            push_groups(no_orden=no_orden, groups="jefedetaller")

        # Borrado individual de refacciones
        if r.get("borrado_refaccion"):
            Refacciones.objects.get(no_orden=no_orden, id=r["refaccion_id"]).delete()

        return HttpResponse(status=200)


# Listado mano de obra
def mano_de_obra(request):
    context = {}

    context["filas"] = []
    context["titulo"] = "Mano de obra"
    context["settings"] = settings

    # Verificación de login
    grupos = request.user.groups.values_list("name", flat=True)
    if not request.user.is_authenticated or "cliente" in grupos:
        return redirect("staff_login")
    notificaciones_push(request, context)

    query_refacciones = VOperacionesRefacciones.objects.all().order_by("-fecha_ingreso")

    # Creación de tabla
    no_ordenes = query_refacciones.values_list("no_orden", flat=True).distinct()

    # Queries generales
    query_tecnico = Items.objects.filter(no_orden__in=no_ordenes)
    query_mo = ManoDeObra.objects.filter(no_orden__in=no_ordenes)

    for no_orden in no_ordenes:
        try:
            info = query_refacciones.filter(no_orden=no_orden).first()
            try:
                modificacion = query_mo.filter(no_orden=no_orden).order_by("-fecha_hora_fin").first().fecha_hora_fin
            except Exception:
                modificacion = ""
            inmediatos = query_tecnico.filter(no_orden=no_orden, estado="Inmediato").count()
            recomendados = query_tecnico.filter(no_orden=no_orden, estado="Recomendado").count()

            context["filas"].append(
                {
                    "no_orden": no_orden,
                    "vin": info.vin,
                    "placas": info.placas,
                    "vehiculo": info.vehiculo,
                    "asesor": info.asesor,
                    "tecnico": info.tecnico,
                    "fecha_ingreso": info.fecha_ingreso,
                    "fin_tecnico": info.fin_tecnico,
                    "modificacion": modificacion,
                    "inmediatos": inmediatos,
                    "recomendados": recomendados,
                }
            )
        except Exception as error:
            logger.warning(error)
    return render(request, "seguimientolite_hyundai_mx/refacciones.html", context)


# Detalle de mano de obra
def mano_de_obra_detalle(request, no_orden):

    if request.method == "GET":
        context = {}
        context["titulo"] = "Mano de obra"
        context["settings"] = settings

        grupos = request.user.groups.values_list("name", flat=True)
        if not request.user.is_authenticated or "cliente" in grupos:
            return redirect("staff_login")
        notificaciones_push(request, context)
        crear_actualizar_info(no_orden)
        get_evidencias(context, no_orden)

        # Log
        try:
            log = LogGeneral.objects.get(no_orden=no_orden)
            if not log.inicio_mano_de_obra and not log.fin_mano_de_obra:
                log.inicio_mano_de_obra = datetime.now()
                log.save()
        except Exception:
            pass

        # Informacion de la orden
        try:
            context["orden"] = Informacion.objects.get(no_orden=no_orden)
            context["tecnicos"] = VTecnicos.objects.all()
        except Exception:
            pass

        queryset_tecnico = Items.objects.filter(no_orden=no_orden)
        queryset_refacciones = Refacciones.objects.filter(no_orden=no_orden)
        queryset_mano_de_obra = ManoDeObra.objects.filter(no_orden=no_orden)

        context["items_tecnico"] = queryset_tecnico.exclude(estado="Buen Estado").exclude(estado="No Aplica")
        context["fin_tecnico"] = queryset_tecnico.first().fecha_hora_fin
        context["refacciones"] = queryset_refacciones
        context["mano_de_obra"] = queryset_mano_de_obra
        context["iva"] = settings.SEGUIMIENTOLITE_IVA
        context["precio_ut"] = settings.SEGUIMIENTOLITE_PRECIO_UT
        context["cargos"] = TiposCargos.objects.all()

        return render(request, "seguimientolite_hyundai_mx/mano_de_obra_detalle.html", context)

    if request.method == "POST":
        r = request.POST
        logger.debug(r)

        # Guardado de inspección
        if r.get("guardar_inspeccion"):
            mano_de_obra = json.loads(r["mano_de_obra"])
            logger.info("Guardado de inspeccion de mano de obra")
            for m_obra in mano_de_obra:

                # Log
                try:
                    log = LogGeneral.objects.get(no_orden=no_orden)
                    if not log.fin_mano_de_obra:
                        log.fin_mano_de_obra = datetime.now()
                        log.save()
                except Exception:
                    pass

                item = Items.objects.get(no_orden=no_orden, id=m_obra["item_id"])
                cargo = TiposCargos.objects.get(id=m_obra["cargo"])
                subtotal_no_descuento_iva = Decimal(m_obra["uts"]) * Decimal(m_obra["precio_ut"])
                porcentaje_descuento = Decimal(m_obra["porcentaje_descuento"])

                defaults_mo = {
                    "nombre": m_obra["nombre"],
                    "cantidad_uts": m_obra["uts"],
                    "precio_ut": m_obra["precio_ut"],
                    "porcentaje_descuento": porcentaje_descuento,
                    "subtotal": round(
                        subtotal_no_descuento_iva - ((subtotal_no_descuento_iva / 100) * porcentaje_descuento), 2
                    ),
                    "porcentaje_iva": settings.SEGUIMIENTOLITE_IVA,
                    "subtotal_iva": Decimal(m_obra["subtotal"]),
                    "cargo": cargo,
                }

                ManoDeObra.objects.update_or_create(
                    no_orden=no_orden, item=item, codigo=m_obra["codigo"], defaults=defaults_mo
                )

            # Correo al contact center para notificar el fin de la inspeccion
            correos = settings.SEGUIMIENTOLITE_CORREOS_GERENCIA
            nuevo_correo = NotificacionCorreo(
                asunto=f"{settings.AGENCIA} - SSL - Llenado de Mano de Obra {no_orden}",
                direccion_email=correos,
                titulo="Inspección de mano de obra terminada",
                mensaje=f"La inspección de mano de obra de la orden {no_orden} ha finalizado.\nHaga click aquí para ver los detalles.\n<a href='https://{settings.DOMINIO}:{settings.PUERTO}{reverse_lazy('mano_de_obra_detalle', kwargs={'no_orden': no_orden})}'>Ver detalles</a>",
                preview="",
            )
            nuevo_correo.enviar()

            # Notificacion push a los asesores
            push_groups(no_orden=no_orden, groups="asesores")

        # Borrado individual de refacciones
        if r.get("borrado_mano_de_obra"):
            ManoDeObra.objects.get(no_orden=no_orden, id=r["mano_de_obra_id"]).delete()

        return HttpResponse(status=200)


# Listado de asesor
def asesor(request):
    context = {}
    context["titulo"] = "Asesor"
    context["settings"] = settings

    grupos = request.user.groups.values_list("name", flat=True)
    if not request.user.is_authenticated or "cliente" in grupos:
        return redirect("staff_login")
    notificaciones_push(request, context)

    # Construcción de la tabla
    if str(request.user.groups.first()) == "administradores":
        filas_ordenes = VOperacionesAsesorAlt.objects.order_by("-no_orden").all()
        ordenes = filas_ordenes.values_list("no_orden", flat=True).distinct()
    else:
        asesor_name = VUsuarios.objects.get(cveusuario=request.user.username)
        filas_ordenes = VOperacionesAsesorAlt.objects.order_by("no_orden").filter(asesor=asesor_name.nombre).distinct()
        ordenes = filas_ordenes.values_list("no_orden", flat=True).distinct()

    context["filas"] = []

    query_tecnico = Items.objects.filter(no_orden__in=ordenes)
    for orden in ordenes.iterator():
        inmediatos = query_tecnico.filter(no_orden=orden, estado="Inmediato").count()
        recomendados = query_tecnico.filter(no_orden=orden, estado="Recomendado").count()

        try:
            log = LogGeneral.objects.get(no_orden=orden)
            if not log.fin_tecnico:
                state = "En Revisión"
            if log.fin_tecnico and not log.fin_refacciones:
                state = "Espera de Refacciones"
            if log.fin_refacciones and not log.fin_mano_de_obra:
                state = "Esperando Mano de Obra"
            if log.fin_mano_de_obra and not log.fin_asesor:
                state = "Esperando envio"
            if log.inicio_asesor and log.fin_asesor:
                state = "Enviado"

            order_info = filas_ordenes.filter(no_orden=orden)[0]
            visits = LogCliente.objects.filter(no_orden=orden).count()
            if visits > 0:
                state = "Visto por el Cliente"

            respuesta = Autorizaciones.objects.filter(no_orden=orden, autorizacion=True).count()
            if respuesta > 0:
                state = "Respondido"

            fin_tecnico = log.fin_tecnico
            fecha_hora_fin_refacciones = log.fin_refacciones

            try:
                tecnico = VOperacionesRefacciones.objects.filter(no_orden=orden).first().tecnico
                modificacion = LogGeneral.objects.get(no_orden=orden).fin_asesor
            except Exception as error:
                logger.warning(error)
                modificacion = ""

            context["filas"].append(
                {
                    "no_orden": order_info.no_orden,
                    "placas": order_info.placas,
                    "asesor": order_info.asesor,
                    "tecnico": tecnico,
                    "fecha_ingreso": fin_tecnico,
                    "fecha_hora_fin_refacciones": fecha_hora_fin_refacciones,
                    "modificacion": modificacion,
                    "vin": order_info.vin,
                    "vehiculo": order_info.vehiculo,
                    "estado": state,
                    "visitas": visits,
                    "respuesta": respuesta,
                    "inmediatos": inmediatos,
                    "recomendados": recomendados,
                }
            )
        except Exception as error:
            logger.warning(error)

    return render(request, "seguimientolite_hyundai_mx/asesor.html", context)


# Detalle de asesor
def asesor_detalle(request, no_orden):

    if request.method == "GET":
        context = {}
        context["titulo"] = "Asesor"
        context["no_orden"] = no_orden
        context["settings"] = settings

        grupos = request.user.groups.values_list("name", flat=True)
        if not request.user.is_authenticated or "cliente" in grupos:
            return redirect("staff_login")
        notificaciones_push(request, context)
        get_evidencias(context, no_orden)

        # Log
        try:
            log = LogGeneral.objects.get(no_orden=no_orden)
            if not log.inicio_asesor and not log.fin_asesor:
                log.inicio_asesor = datetime.now()
                log.save()
        except Exception as error:
            logger.warning(error)

        # Proseso normal
        try:
            context["orden"] = Informacion.objects.get(no_orden=no_orden)
            context["tecnicos"] = VTecnicos.objects.all()
        except Exception:
            pass

        # Informacion de refacciones y mano de obra
        query_tecnico = Items.objects.filter(no_orden=no_orden)
        query_refacciones = Refacciones.objects.filter(no_orden=no_orden)
        query_mano_de_obra = ManoDeObra.objects.filter(no_orden=no_orden)
        query_autorizaciones = Autorizaciones.objects.filter(no_orden=no_orden)

        context["items_tecnico"] = query_tecnico.exclude(estado="Buen Estado").exclude(estado="No Aplica")
        context["refacciones"] = query_refacciones
        context["mano_de_obra"] = query_mano_de_obra
        context["autorizaciones"] = query_autorizaciones
        context["fin_tecnico"] = query_tecnico.first().fecha_hora_fin
        context["guias_mantenimiento"] = query_tecnico.values("item__revision__id", "item__revision__nombre").distinct()

        # Totales
        total_refacciones = query_refacciones.aggregate(Sum("subtotal_iva"))["subtotal_iva__sum"]
        total_mano_de_obra = query_mano_de_obra.aggregate(Sum("subtotal_iva"))["subtotal_iva__sum"]
        if not total_refacciones:
            total_refacciones = 0
        if not total_mano_de_obra:
            total_mano_de_obra = 0
        total_cotizado = total_refacciones + total_mano_de_obra
        context["total_cotizado"] = total_cotizado
        context["total_refacciones"] = total_refacciones
        context["total_mano_de_obra"] = total_mano_de_obra

        items_autorizados = query_autorizaciones.filter(autorizacion=True).values_list("item", flat=True)
        total_refacciones_autorizadas = query_refacciones.filter(item__in=items_autorizados).aggregate(
            Sum("subtotal_iva")
        )["subtotal_iva__sum"]
        total_mano_de_obra_autorizada = query_mano_de_obra.filter(item__in=items_autorizados).aggregate(
            Sum("subtotal_iva")
        )["subtotal_iva__sum"]
        if not total_refacciones_autorizadas:
            total_refacciones_autorizadas = 0
        if not total_mano_de_obra_autorizada:
            total_mano_de_obra_autorizada = 0
        total_autorizado = total_refacciones_autorizadas + total_mano_de_obra_autorizada

        context["total_autorizado"] = total_autorizado
        context["total_no_autorizado"] = total_cotizado - total_autorizado
        context["total_refacciones_autorizadas"] = total_refacciones_autorizadas
        context["total_refacciones_no_autorizadas"] = total_refacciones - total_refacciones_autorizadas
        context["total_mano_de_obra_autorizada"] = total_mano_de_obra_autorizada
        context["total_mano_de_obra_no_autorizada"] = total_mano_de_obra - total_mano_de_obra_autorizada

        context["items_autorizados"] = query_autorizaciones.filter(autorizacion=True)
        context["items_no_autorizados"] = context["items_tecnico"].exclude(
            id__in=context["items_autorizados"].values_list("item_id")
        )

        context["nombre_agencia"] = settings.AGENCIA
        context["prefijo"] = settings.TELEFONO
        context["precio_ut"] = settings.SEGUIMIENTOLITE_PRECIO_UT
        context["iva"] = settings.SEGUIMIENTOLITE_IVA
        context["link"] = f"http://{settings.DOMINIO}:{settings.PUERTO}/{settings.PREFIJO}/seguimiento/cliente/{no_orden}/"
        context["encrypted_no_orden"] = encrypt_number(no_orden)

        return render(request, "seguimientolite_hyundai_mx/asesor_detalle.html", context)

    if request.method == "POST":
        context = {}
        context["no_orden"] = no_orden
        r = request.POST
        metodo = r.get("metodo", None)

        # ENVIO DE WHATSAPP
        if metodo == "WhatsApp":
            # LOG
            try:
                encrypted_no_orden = encrypt_number(no_orden)
                enviar_whatsapp(r["prefijo"], r["telefono"], r["mensaje"], encrypted_no_orden)

                log = LogGeneral.objects.get(no_orden=no_orden)
                if not log.fin_asesor:
                    log.fin_asesor = datetime.now()
                    log.save()

                LogEnvios.objects.create(
                    no_orden=no_orden,
                    medio=request.POST["metodo"],
                    fecha_hora_envio=datetime.now(),
                    telefono=request.POST["telefono"],
                )
                return HttpResponse(status=200)
            except Exception:
                return HttpResponse(status=500)

        # ENVIO DE CORREO
        if metodo == "E-Mail":
            # LOG
            template_context = {}
            template_context["cotizacion"] = True
            template_context["asunto"] = "Cotizacion"
            template_context["preview"] = settings.AGENCIA + " | Su vehículo ha sido revisado"
            template_context["nombre_agencia"] = settings.AGENCIA
            encrypted_no_orden = encrypt_number(no_orden)
            template_context["cotizacion_url"] = f"{settings.DOMINIO}/{settings.PREFIJO}/seguimiento/cliente/{encrypted_no_orden}"
            template_context["telefono_agencia"] = settings.TELEFONO
            template_context["privacy_url"] = settings.AVISO_PRIVACIDAD

            template_context[
                "logo"
            ] = "https://logos-world.net/wp-content/uploads/2021/03/Hyundai-Logo-2003-present.png"
            html_content = render_to_string("seguimientolite_hyundai_mx/mail-template.html", template_context)

            client_mail = request.POST.get("mail", None)

            email = EmailMessage(
                settings.AGENCIA,
                html_content,
                settings.EMAIL_HOST_USER,
                [client_mail],
            )

            email.content_subtype = "html"
            email.send()
            logger.info("Correo enviado")
            print(template_context["cotizacion_url"])
            print(template_context["cotizacion"])

            # LOG
            LogEnvios.objects.create(
                no_orden=no_orden,
                medio=request.POST["metodo"],
                fecha_hora_envio=datetime.now(),
                correo=request.POST["mail"],
            )
            try:
                log = LogGeneral.objects.get(no_orden=no_orden)
                if not log.fin_asesor:
                    log.fin_asesor = datetime.now()
                    log.save()
            except Exception:
                pass

        if metodo:
            # Correo al contact center para notificar el fin de la inspeccion
            correos = settings.SEGUIMIENTOLITE_CORREOS_ASESORES + settings.SEGUIMIENTOLITE_CORREOS_GERENCIA
            nuevo_correo = NotificacionCorreo(
                asunto=f"{settings.AGENCIA} - SSL - Envío de Cotización {no_orden}",
                direccion_email=correos,
                titulo="Orden enviada",
                mensaje=f"La orden {no_orden} ha sido enviada por medio de {metodo}.\nHaga click aquí para ver los detalles.\n<a href='https://{settings.DOMINIO}:{settings.PUERTO}/{settings.PREFIJO}{reverse_lazy('detalle_ordenes', kwargs={'no_orden': no_orden})}'>Ver detalles</a>",
                preview="",
            )
            nuevo_correo.enviar()

        # Log de whatsapp web
        if r.get("log_whatsapp_web"):
            log = LogGeneral.objects.get(no_orden=no_orden)
            if not log.fin_asesor:
                log.fin_asesor = datetime.now()
                log.save()
            LogEnvios.objects.create(
                no_orden=no_orden,
                medio="WhatsApp",
                fecha_hora_envio=datetime.now(),
                telefono=request.POST["telefono"],
            )
            # Correo al contact center para notificar el fin de la inspeccion
            correos = settings.SEGUIMIENTOLITE_CORREOS_ASESORES + settings.SEGUIMIENTOLITE_CORREOS_GERENCIA
            nuevo_correo = NotificacionCorreo(
                asunto=f"{settings.AGENCIA} - SSL - Envío de Cotización {no_orden}",
                direccion_email=correos,
                titulo="Orden enviada",
                mensaje=f"La orden {no_orden} ha sido enviada por medio de WhatsApp.\nHaga click aquí para ver los detalles.\n<a href='https://{settings.DOMINIO}:{settings.PUERTO}/{settings.PREFIJO}{reverse_lazy('detalle_ordenes', kwargs={'no_orden': no_orden})}'>Ver detalles</a>",
                preview="",
            )
            nuevo_correo.enviar()

        # GUARDADO DE FIRMA
        if r.get("firma"):
            sign = r.get("firma", None)
            data = sign[22:].encode()
            with open(os.path.join(BASE_DIR, "media", "tmp.png"), "wb") as fh:
                fh.write(base64.decodebytes(data))

            threshold = 100
            dist = 5
            img_buffer = Image.open(os.path.join(BASE_DIR, "media", "tmp.png")).convert("RGBA")
            arr = np.array(np.asarray(img_buffer))
            r, g, b, a = np.rollaxis(arr, axis=-1)
            mask = (
                (r > threshold)
                & (g > threshold)
                & (b > threshold)
                & (np.abs(r - g) < dist)
                & (np.abs(r - b) < dist)
                & (np.abs(g - b) < dist)
            )
            arr[mask, 3] = 0
            name = f"{datetime.now()}.png"
            img_buffer = Image.fromarray(arr, mode="RGBA")
            img_buffer.save(os.path.join(settings.MEDIA_ROOT, f"{no_orden}.png"))
            os.remove(os.path.join(BASE_DIR, "media", "tmp.png"))

            try:
                f = ActividadesAsesorFirmas.objects.get(no_orden=no_orden)
                f.firma = f"{no_orden}.png"
                f.save()
            except Exception:
                ActividadesAsesorFirmas.objects.create(no_orden=no_orden, firma=f"{no_orden}.png")

        r = request.POST
        if r.get("cotizacion_pdf"):
            refacciones_ids = json.loads(r["ids_ref"])
            mano_de_obra_ids = json.loads(r["ids_mo"])
            pdf = cotizacion_pdf(no_orden, refacciones_ids, mano_de_obra_ids)
            response = HttpResponse(pdf)
            response["Content-Disposition"] = 'attachment; filename="cotizacion.pdf"'
            response["Content-Type"] = "application/octet-stream"
            return response

        if r.get("cotizacion_pdf_simplificado"):
            cotizacion = CotizacionSimplificada(no_orden)
            pdf = cotizacion.pdf()
            response = HttpResponse(pdf)
            response["Content-Disposition"] = 'attachment; filename="cotizacion.pdf"'
            response["Content-Type"] = "application/octet-stream"
            return response

        return HttpResponse(status=200)


# Listado de historial
def historial(request):
    grupos = request.user.groups.values_list("name", flat=True)
    if not request.user.is_authenticated or "cliente" in grupos:
        return redirect("staff_login")

    try:
        context = {}
        context["settings"] = settings
        orders_to_exclude = VOperacionesTecnico.objects.values_list("no_orden", flat=True)
        orders = Informacion.objects.order_by("-fecha_hora_ingreso").exclude(no_orden__in=orders_to_exclude)
        context["filas"] = orders
        context["tecnicos"] = VTecnicos.objects.all()
        context["titulo"] = "Historial"
    except Exception as error:
        logger.warning(error)

    notificaciones_push(request, context)

    return render(request, "seguimientolite_hyundai_mx/historial.html", context)


# Detalle de historial
def historial_detalle(request, no_orden):
    # Login
    grupos = request.user.groups.values_list("name", flat=True)
    if not request.user.is_authenticated or "cliente" in grupos:
        return redirect("staff_login")

    context = {}
    context["titulo"] = "Historial"
    context["settings"] = settings

    notificaciones_push(request, context)

    try:
        if LogEnvios.objects.filter(no_orden=no_orden).exists():
            context["envios"] = True
        if ActividadesCalidad.objects.filter(no_orden=no_orden).exists():
            context["calidad"] = True
        context["log"] = LogGeneral.objects.get(no_orden=no_orden)
    except Exception as error:
        logger.warning(error)

    try:
        context["no_orden"] = no_orden
        context["tecnicos"] = VTecnicos.objects.all()
        try:
            context["fin_tecnico"] = (
                Items.objects.filter(no_orden=no_orden).order_by("fecha_hora_fin").first().fecha_hora_fin
            )
        except Exception as error:
            logger.warning(error)
            context["fin_tecnico"] = "Sin revision tecnica"
        context["precio_ut"] = settings.SEGUIMIENTOLITE_PRECIO_UT
        context["iva"] = settings.SEGUIMIENTOLITE_IVA
        # context['orden'] = VOperacionesRefacciones.objects.get(no_orden=no_orden)
        context["orden"] = Informacion.objects.get(no_orden=no_orden)
        # context['filas_media'] = Evidencias.objects.filter(no_orden=no_orden)
        context["filas_media"] = []
        context["filas_video"] = []
        media = Evidencias.objects.filter(no_orden=no_orden)
        for file in media:
            file_type = mimetypes.guess_type(file.evidencia)[0]
            try:
                if "video" in file_type:
                    context["filas_video"].append(file)
                else:
                    context["filas_media"].append(file)
            except Exception as error:
                logger.warning(error)

        context["items_mo"] = context["filas"].values_list("item", flat=True).distinct()
    except Exception as error:
        logger.warning(error)
    return render(request, "seguimientolite_hyundai_mx/historial_detalle.html", context)


# Login automatico para clientes
def client_autologin(request, encrypt_number_no_orden):
    no_orden = decrypt_number(encrypt_number_no_orden)
    print(encrypt_number_no_orden)
    print(no_orden)
    try:
        client = User.objects.get(username=no_orden)
        login(request, client)
        return redirect("cliente_cotizacion", encrypt_number_no_orden=encrypt_number_no_orden)
    except User.DoesNotExist:
        try:
            client = User.objects.create_user(username=no_orden, first_name=no_orden)
            group = Group.objects.get_or_create(name="cliente")[0]
            password = User.objects.make_random_password(length=12)
            client.set_password(password)
            client.groups.add(group)
            client.save()
            login(request, client)
            return redirect("cliente_cotizacion", encrypt_number_no_orden=encrypt_number_no_orden)
        except Exception as e:
            return render(request, 'seguimientolite_hyundai_mx/error_404.html', {'error': e})



# Detalle de cliente
def cliente_detalle(request, encrypt_number_no_orden):
    try:
        no_orden = decrypt_number(encrypt_number_no_orden)
    except ValueError as e:
        return render(request, 'seguimientolite_hyundai_mx/error_404.html', {'error_message': str(e)})
    
    print(encrypt_number_no_orden)
    print(no_orden)


    if request.method == "GET":
        # Login de cliente
        try:
            client = User.objects.get(username=no_orden)
            login(request, client)
        except Exception:
            client = User.objects.create_user(username=no_orden, first_name=no_orden)
            group = Group.objects.get_or_create(name="cliente")[0]
            password = User.objects.make_random_password(length=12)
            client.set_password(password)
            client.groups.add(group)
            client.save()
            login(request, client)

        context = {}
        context["titulo"] = "Cliente"
        context["settings"] = settings

        # Notificaciones push
        notificaciones_push(request, context)
        get_evidencias(context, no_orden)

        # Log
        try:
            LogCliente.objects.create(
                no_orden=no_orden,
                fecha_hora_visita=datetime.now(),
            )
        except Exception as error:
            logger.warning(error)

        context["no_orden"] = no_orden
        try:
            context["orden"] = Informacion.objects.get(no_orden=no_orden)
        except Exception:
            pass

        # Items
        queryset_tecnico = Items.objects.filter(no_orden=no_orden)
        items_recomendados = queryset_tecnico.filter(estado="Recomendado")
        items_urgentes = queryset_tecnico.filter(estado="Inmediato")

        context["items_tecnico"] = queryset_tecnico.exclude(estado="Buen Estado").exclude(estado="No Aplica")
        context["items_recomendados"] = items_recomendados.count()
        context["items_urgentes"] = items_urgentes.count()

        # Totales
        context["totales_items"] = []
        for item in context["items_tecnico"]:
            cotizaciones_ref = Refacciones.objects.filter(item=item)
            cotizaciones_mo = ManoDeObra.objects.filter(item=item)

            subtotal_ref = cotizaciones_ref.aggregate(Sum("subtotal_iva"))["subtotal_iva__sum"]
            subtotal_mo = cotizaciones_mo.aggregate(Sum("subtotal_iva"))["subtotal_iva__sum"]

            if not subtotal_ref:
                subtotal_ref = 0
            if not subtotal_mo:
                subtotal_mo = 0

            try:
                total = subtotal_ref + subtotal_mo
                context["totales_items"].append(
                    {
                        "item": item,
                        "total_ref": round(subtotal_ref, 2),
                        "total_mo": round(subtotal_mo, 2),
                        "total": round(total, 2),
                    }
                )
            except Exception as error:
                logger.error(error)
                context["totales_items"].append(
                    {
                        "item": item,
                        "total_ref": 0,
                        "total_mo": 0,
                        "total": 0,
                    }
                )

        context["total_orden"] = 0
        for item in context["totales_items"]:
            context["total_orden"] += item["total"]

        # Items autorizados
        query_autorizaciones = Autorizaciones.objects.filter(no_orden=no_orden)
        context["items_autorizados"] = query_autorizaciones

        # TABLAS EN FRONT-END
        query_refacciones = Refacciones.objects.filter(no_orden=no_orden)
        query_mano_de_obra = ManoDeObra.objects.filter(no_orden=no_orden)
        context["refacciones"] = query_refacciones
        context["mano_de_obra"] = query_mano_de_obra

        return render(request, "seguimientolite_hyundai_mx/cliente_detalle.html", context)

    if request.method == "POST":
        r = request.POST

        items_revisados = json.loads(r.get("items_revisados"))
        for item_revisado in items_revisados:
            Autorizaciones.objects.update_or_create(
                no_orden=no_orden, item_id=item_revisado["item_id"], defaults=item_revisado
            )

        # Correo de confirmacion para cliente
        client_mail = LogEnvios.objects.filter(no_orden=no_orden).order_by("-fecha_hora_envio").first().correo
        nuevo_correo = NotificacionCorreo(
            direccion_email=[client_mail],
            asunto=f"{settings.AGENCIA} - Su autorización ha sido procesada",
            titulo=f"En {settings.AGENCIA} trabajamos para ti",
            mensaje=f"Gracias por usar el servicio de Seguimiento en línea, su solicitud ha sido procesada con éxito \n<a href='https://{settings.DOMINIO}:{settings.PUERTO}/{settings.PREFIJO}{reverse_lazy('cliente_cotizacion', kwargs={'no_orden': no_orden})}'>Detalles de Cotización</a>",
            preview="",
        )
        nuevo_correo.enviar()

        # Correo de confirmacion para personal
        correos = settings.SEGUIMIENTOLITE_CORREOS_ASESORES + settings.SEGUIMIENTOLITE_CORREOS_GERENCIA
        nuevo_correo = NotificacionCorreo(
            direccion_email=correos,
            asunto=f"{settings.AGENCIA} - SSL - Autorización del presupuesto {no_orden}",
            titulo="Orden revisada por el cliente",
            mensaje=f"La orden {no_orden} ha sido revisada por el cliente, para conocer items autorizados y no autorizados haga click aquí para ver los detalles.\n<a href='https://{settings.DOMINIO}:{settings.PUERTO}/{settings.PREFIJO}{reverse_lazy('detalle_ordenes', kwargs={'no_orden': no_orden})}'>Ver detalles</a>",
            preview="",
        )
        nuevo_correo.enviar()

        # Notificacion push para personal
        try:
            payload = {
                "head": settings.AGENCIA,
                "body": f"{settings.AGENCIA} - SSL - Autorización del presupuesto {no_orden}",
                "icon": "https://logos-marcas.com/wp-content/uploads/2020/04/Toyota-Emblema-650x366.png",
                "url": f"https://{settings.DOMINIO}:{settings.PUERTO}/{settings.PREFIJO}{reverse_lazy('detalle_ordenes', kwargs={'no_orden': no_orden})}",
            }
            asesor = Informacion.objects.get(no_orden=no_orden).asesor
            receiver = User.objects.filter(first_name=asesor)

            send_user_notification(user=receiver, payload=payload, ttl=1000)
        except Exception as error:
            logger.warning(error)
        return HttpResponse(status=200)


# Hoja multipuntos
def hoja_multipuntos_pdf(request, no_orden):
    buffer = get_pdf_calidad(no_orden)
    return FileResponse(buffer, as_attachment=False, filename=f"multipuntos_{no_orden}.pdf")


# KPIS Resumen
def kpis_resumen(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect("staff_login")

        context = {}
        context["titulo"] = "KPIS"
        context["settings"] = settings
        context["años"] = Informacion.objects.datetimes("fecha_hora_ingreso", "year").distinct()
        notificaciones_push(request, context)

        return render(request, "kpis_hyundai_mx/resumen.html", context)

    if request.method == "POST":
        request_body = request.POST
        tipo = request_body.get("tipo")

        if tipo == "hoy":
            fecha = str(date.today())
            queryset_header = Informacion.objects.filter(
                fecha_hora_ingreso__isnull=False, fecha_hora_ingreso__date=fecha
            )
        if tipo == "mes":
            fecha = request_body.get("fecha")
            queryset_header = Informacion.objects.filter(
                fecha_hora_ingreso__isnull=False,
                fecha_hora_ingreso__date__year=fecha[0:4],
                fecha_hora_ingreso__date__month=fecha[5:7],
            )
        if tipo == "año":
            fecha = request_body.get("fecha")
            queryset_header = Informacion.objects.filter(
                fecha_hora_ingreso__isnull=False,
                fecha_hora_ingreso__date__year=fecha[0:4],
            )
        if tipo == "rango":
            queryset_header = Informacion.objects.filter(
                fecha_hora_ingreso__range=(request_body["inicio"], request_body["fin"])
            )

        no_ordenes_all = queryset_header.exclude(no_orden=0).values_list("no_orden").distinct()

        tarjetas_tecnico = Items.objects.filter(no_orden__in=no_ordenes_all)
        tarjetas_refacciones = Refacciones.objects.filter(no_orden__in=no_ordenes_all)
        tarjetas_asesor = ManoDeObra.objects.filter(no_orden__in=no_ordenes_all)
        tarjetas_visitas = LogCliente.objects.filter(no_orden__in=no_ordenes_all)
        queryset_tiempos = LogGeneral.objects.filter(no_orden__in=no_ordenes_all)
        queryset_envios = LogEnvios.objects.filter(no_orden__in=no_ordenes_all)
        queryset_autorizaciones = Autorizaciones.objects.filter(no_orden__in=no_ordenes_all)

        response = {}
        response["total_entradas"] = no_ordenes_all.count()
        response["finalizados_tecnico"] = tarjetas_tecnico.values("no_orden").distinct().count()
        response["finalizados_refacciones"] = tarjetas_refacciones.values("no_orden").distinct().count()
        response["finalizados_asesor"] = tarjetas_asesor.values("no_orden").distinct().count()
        response["tarjeta_ordenes_enviadas"] = queryset_envios.values("no_orden").distinct().count()
        response["tarjeta_vistas"] = tarjetas_visitas.values("no_orden").distinct().count()
        response["finalizados_cliente"] = queryset_autorizaciones.values("no_orden").distinct().count()

        # Tiempo promedio de tecnico
        duracion_tecnico_func = ExpressionWrapper(
            F("fin_tecnico") - F("inicio_tecnico"), output_field=fields.DurationField()
        )
        duracion_tecnico = queryset_tiempos.annotate(duracion_tecnico=duracion_tecnico_func)
        if tiempo_tecnico := duracion_tecnico.aggregate(promedio=Avg("duracion_tecnico"))["promedio"]:
            response["tiempo_tecnico"] = round(tiempo_tecnico.seconds / 60, 2)
        else:
            response["tiempo_tecnico"] = 0

        # Tiempo promedio de refacciones
        duracion_ref_func = ExpressionWrapper(
            F("fin_refacciones") - F("inicio_refacciones"), output_field=fields.DurationField()
        )
        duracion_ref = queryset_tiempos.annotate(duracion_ref=duracion_ref_func)
        if tiempo_cotizacion_refacciones := duracion_ref.aggregate(promedio=Avg("duracion_ref"))["promedio"]:
            response["tiempo_refacciones"] = round(tiempo_cotizacion_refacciones.seconds / 60, 2)
        else:
            response["tiempo_refacciones"] = 0

        # Tiempo promedio de mano de obra
        duracion_mo_func = ExpressionWrapper(
            F("fin_mano_de_obra") - F("inicio_mano_de_obra"), output_field=fields.DurationField()
        )
        duracion_mo = queryset_tiempos.annotate(duracion_mo=duracion_mo_func)
        if tiempo_mo := duracion_mo.aggregate(promedio=Avg("duracion_mo"))["promedio"]:
            response["tiempo_mo"] = round(tiempo_mo.seconds / 60, 2)
        else:
            response["tiempo_mo"] = 0

        # Tiempo promedio de asesor
        duracion_asesor_func = ExpressionWrapper(
            F("fin_asesor") - F("inicio_asesor"), output_field=fields.DurationField()
        )
        duracion_asesor = queryset_tiempos.annotate(duracion_asesor=duracion_asesor_func)
        if tiempo_asesor := duracion_asesor.aggregate(promedio=Avg("duracion_asesor"))["promedio"]:
            response["tiempo_asesor"] = round(tiempo_asesor.seconds / 60, 2)
        else:
            response["tiempo_asesor"] = 0

        if no_wa := queryset_envios.filter(medio="WhatsApp").count():
            response["no_wa"] = no_wa
        else:
            response["no_wa"] = 0

        if no_mail := queryset_envios.filter(medio="E-Mail").count():
            response["no_mail"] = no_mail
        else:
            response["no_mail"] = 0

        finalizados_envios = queryset_envios.values_list("no_orden").distinct().count()
        response["finalizados_envios"] = finalizados_envios

        return HttpResponse(json.dumps(response), content_type="application/json")


# KPIS Financiero
def kpis_financiero(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect("staff_login")
        context = {}
        context["titulo"] = "KPIS"
        context["settings"] = settings
        context["años"] = Informacion.objects.datetimes("fecha_hora_ingreso", "year").distinct()
        context["asesores"] = VUsuarios.objects.exclude(cveasesor__isnull=False).values_list("nombre", flat=True)
        notificaciones_push(request, context)
        return render(request, "kpis_hyundai_mx/financiero.html", context)

    if request.method == "POST":
        request_body = request.POST

        tipo = request_body.get("tipo")
        header_filtros = {}

        if request_body.get("asesor"):
            header_filtros["asesor"] = request_body["asesor"]
        if tipo == "hoy":
            fecha = date.today()
            header_filtros["fecha_hora_ingreso__isnull"] = False
            header_filtros["fecha_hora_ingreso__date"] = fecha
            no_dias = calendar.monthrange(fecha.year, fecha.month)[1]
            categorias = list(range(1, no_dias + 1))
        if tipo == "mes":
            fecha = request_body.get("fecha")
            header_filtros["fecha_hora_ingreso__isnull"] = False
            header_filtros["fecha_hora_ingreso__date__year"] = fecha[0:4]
            header_filtros["fecha_hora_ingreso__date__month"] = fecha[5:7]
            no_dias = calendar.monthrange(int(fecha[0:4]), int(fecha[5:7]))[1]
            categorias = list(range(1, no_dias + 1))
        if tipo == "año":
            fecha = request_body.get("fecha")
            header_filtros["fecha_hora_ingreso__isnull"] = False
            header_filtros["fecha_hora_ingreso__date__year"] = fecha[0:4]
            no_meses = 12
            categorias = list(range(1, no_meses + 1))
        if tipo == "rango":
            header_filtros["fecha_hora_ingreso__range"] = (request_body["inicio"], request_body["fin"])
            no_meses = 12
            categorias = list(range(1, no_meses + 1))

        queryset_header = Informacion.objects.filter(**header_filtros)
        no_ordenes_all = queryset_header.values_list("no_orden", flat=True)

        queryset_general = Autorizaciones.objects.filter(no_orden__in=no_ordenes_all)
        queryset_envios = LogEnvios.objects.filter(no_orden__in=no_ordenes_all)

        # Construccion de la respuesta
        # Tarjetas de cabecera
        response = {}
        response["categories"] = categorias
        response["no_ordenes_totales"] = queryset_header.exclude(no_orden=0).count()
        response["no_ordenes_enviadas"] = queryset_envios.values("no_orden").distinct().count()
        response["no_ordenes_autorizadas"] = queryset_general.exclude(autorizacion=False).values("no_orden").count()

        monto_ref = Refacciones.objects.filter(no_orden__in=no_ordenes_all).aggregate(sum=Sum("subtotal_iva"))["sum"]
        if not monto_ref:
            monto_ref = 0
        monto_mo = ManoDeObra.objects.filter(no_orden__in=no_ordenes_all).aggregate(sum=Sum("subtotal_iva"))["sum"]
        if not monto_mo:
            monto_mo = 0
        response["total_autorizado"] = str(monto_ref + monto_mo)

        promedio_ordenes = queryset_general.values("no_orden").annotate(promedio=Sum("autorizacion"))
        try:
            response["items_promedio"] = round(promedio_ordenes.aggregate(avg=Avg("promedio"))["avg"], 2)
        except Exception:
            response["items_promedio"] = 0

        # Graficas
        response["tarjetas_asesor"] = []
        series = []
        nombres_asesores = queryset_header.exclude(asesor__isnull=True).values_list("asesor", flat=True).distinct()
        for nombre_asesor in nombres_asesores:
            asesor_no_ordenes = (
                queryset_header.filter(asesor=nombre_asesor).values_list("no_orden", flat=True).distinct()
            )
            ordenes_enviadas = (
                queryset_envios.filter(no_orden__in=asesor_no_ordenes).values("no_orden").distinct().count()
            )
            ordenes_autorizadas = (
                queryset_general.filter(no_orden__in=asesor_no_ordenes)
                .exclude(autorizacion=False)
                .values("no_orden")
                .count()
            )

            # Monto de refacciones
            monto_asesor_ref = Refacciones.objects.filter(no_orden__in=asesor_no_ordenes).aggregate(
                sum=Sum("subtotal_iva")
            )["sum"]
            if not monto_asesor_ref:
                monto_asesor_ref = 0
            # Monto de mano de obra
            monto_asesor_mo = ManoDeObra.objects.filter(no_orden__in=asesor_no_ordenes).aggregate(
                sum=Sum("subtotal_iva")
            )["sum"]
            if not monto_asesor_mo:
                monto_asesor_mo = 0

            # Monto total
            monto_total = monto_asesor_mo + monto_asesor_ref
            if not monto_total:
                monto_total = 0
            monto_ssl = round(monto_total, 2)

            if not ordenes_enviadas:
                porcentaje_efectividad = 0
            else:
                porcentaje_efectividad = round((100 / ordenes_enviadas) * ordenes_autorizadas, 2)

            response["tarjetas_asesor"].append(
                {
                    "asesor_nombre": nombre_asesor,
                    "asesor_ordenes": queryset_header.filter(asesor=nombre_asesor).count(),
                    "asesor_ordenes_enviadas": ordenes_enviadas,
                    "asesor_ordenes_autorizadas": ordenes_autorizadas,
                    "asesor_porcentaje_efectividad": porcentaje_efectividad,
                    "asesor_monto_ssl": str(monto_ssl),
                    "asesor_monto_total": str(monto_total),
                }
            )

            data = []
            for categoria in categorias:
                if categoria < 10:
                    categoria = "0" + str(categoria)
                if tipo in ("hoy", "mes"):
                    categoria_filter = {"fecha_hora_fin__day": categoria}
                if tipo in ("año", "rango"):
                    categoria_filter = {"fecha_hora_fin__month": categoria}

                # Monto de refacciones
                monto_dia_asesor_ref = Refacciones.objects.filter(
                    no_orden__in=asesor_no_ordenes, **categoria_filter
                ).aggregate(sum=Sum("subtotal_iva"))["sum"]
                if not monto_dia_asesor_ref:
                    monto_dia_asesor_ref = 0

                # Monto de mano de obra
                monto_dia_asesor_mo = ManoDeObra.objects.filter(
                    no_orden__in=asesor_no_ordenes, **categoria_filter
                ).aggregate(sum=Sum("subtotal_iva"))["sum"]
                if not monto_dia_asesor_mo:
                    monto_dia_asesor_mo = 0

                monto_dia_asesor_total = monto_dia_asesor_mo + monto_dia_asesor_ref
                data.append(monto_dia_asesor_total)
            series.append({"name": nombre_asesor, "data": data})

        response["series"] = series
        return JsonResponse(response)


def kpis_general(request):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect("staff_login")

        queryset_general = KpisGeneral.objects.all().order_by("-fecha_hora_entrada")

        context = {
            "titulo": "KPIS",
            "asesores": queryset_general.order_by("asesor")
            .exclude(asesor=None)
            .values_list("asesor", flat=True)
            .distinct(),
            "ordenes": queryset_general,
        }
    return render(request, "kpis_hyundai_mx/general.html", context)


def kpis_general_pdf(request, fecha_inicio=None, fecha_fin=None, asesores=None):
    if not request.user.is_authenticated:
        return redirect("staff_login")

    fecha_inicio = None if fecha_inicio == "null" else datetime.strptime(fecha_inicio, "%d-%m-%Y").strftime("%Y-%m-%d")

    fecha_fin = None if fecha_inicio == "null" else datetime.strptime(fecha_fin, "%d-%m-%Y").strftime("%Y-%m-%d")

    asesores = None if asesores == "null" else asesores.split(",")

    if all((fecha_inicio, fecha_fin, asesores)):
        queryset_general = KpisGeneral.objects.filter(
            fecha_hora_entrada__date__range=[fecha_inicio, fecha_fin], asesor__in=asesores
        )
    elif fecha_inicio and fecha_fin:
        queryset_general = KpisGeneral.objects.filter(fecha_hora_entrada__date__range=[fecha_inicio, fecha_fin])
    elif fecha_inicio:
        queryset_general = KpisGeneral.objects.filter(fecha_hora_entrada__date__gte=fecha_inicio)
    elif fecha_fin:
        queryset_general = KpisGeneral.objects.filter(fecha_hora_entrada__date__lte=fecha_fin)
    elif asesores:
        queryset_general = KpisGeneral.objects.filter(asesor__in=asesores)
    else:
        queryset_general = KpisGeneral.objects.all()
    return ExcelResponse(queryset_general.order_by("-fecha_hora_entrada"))


def kpis_general_detalle(request, no_orden):
    if not request.user.is_authenticated:
        return redirect("staff_login")

    if request.method == "GET":
        queryset_general = KpisGeneral.objects.order_by("-fecha_hora_entrada").filter(no_orden=no_orden).first()

        context = {}
        context["titulo"] = "KPIS"
        context["orden"] = queryset_general

        queryset_tecnico = Items.objects.filter(no_orden=no_orden)
        context["tecnico_inmediato"] = queryset_tecnico.filter(estado="Inmediato")
        context["tecnico_recomendado"] = queryset_tecnico.filter(estado="Recomendado")
        context["tecnico_no_aplica"] = queryset_tecnico.filter(estado="No Aplica")
        context["tecnico_buen_estado"] = queryset_tecnico.filter(estado="Buen Estado")

        context["items_tecnico"] = Items.objects.filter(no_orden=no_orden)
        context["refacciones"] = Refacciones.objects.filter(no_orden=no_orden)
        context["mano_de_obra"] = ManoDeObra.objects.filter(no_orden=no_orden)
        context["autorizados"] = Autorizaciones.objects.filter(no_orden=no_orden, autorizacion=True).values_list(
            "item_id", flat=True
        )

        # Evidencias
        context["evidencias_ssl"] = Evidencias.objects.filter(no_orden=no_orden)
        context["videos_ssl"] = []
        for file in context["evidencias_ssl"]:
            file_type = mimetypes.guess_type(file.evidencia)[0]
            try:
                if "video" in file_type:
                    context["videos_ssl"].append(file.evidencia)
            except Exception as error:
                print(error)
    return render(request, "kpis_hyundai_mx/general_detalle.html", context)


def kpis_general_detalle_pdf(request, no_orden):
    if not request.user.is_authenticated:
        return redirect("staff_login")

    queryset_general = (
        KpisGeneral.objects.order_by("-fecha_hora_entrada")
        .filter(no_orden=no_orden)
        .values(
            "no_orden",
            "no_placas",
            "fecha_hora_entrada",
            "fecha_hora_salida",
            "kilometraje",
            "fecha",
            "asesor",
            "vin",
            "modelo",
            "year_vehiculo",
            "cliente",
            "telefono",
            "multipuntos",
            "tecnico",
            "inmediato",
            "buen_estado",
            "recomendado",
            "videos",
            "fotos",
            "cotizacion_refacciones",
            "cotizacion_mo",
            "envio_cotizacion",
            "envio_email",
            "envio_whatsapp",
            "vista_cliente",
            "autorizados",
            "detalle_items_autorizados",
            "detalle_refacciones_autorizadas",
            "detalle_items_no_autorizados",
            "detalle_refacciones_no_autorizadas",
            "total_cotizado_mo",
            "total_cotizado_repuestos",
            "total_cotizado",
            "monto_autorizado",
            "monto_autorizado_refacciones",
            "monto_autorizado_mo",
            "no_autorizados",
            "monto_no_autorizado",
            "porcentaje_autorizado",
            "porcentaje_no_autorizado",
        )
    )
    return ExcelResponse(queryset_general)


class PantallaRecepcionView(TemplateView):
    template_name = "seguimientolite_hyundai_mx/pantalla_recepcion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["con_cita"] = VPantallaRecepcion.objects.filter(cita=1)
        context["sin_cita"] = VPantallaRecepcion.objects.filter(cita=0)
        return context
