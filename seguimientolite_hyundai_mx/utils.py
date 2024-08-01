from asyncio.log import logger
import json
import logging
import mimetypes
import os

import requests as api
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django_drf_filepond.models import TemporaryUpload
from webpush import send_user_notification
from webpush.models import PushInformation

from .models import Evidencias, Informacion, VInformacion

MEDIA_DIR = settings.MEDIA_ROOT
COREAPI_URL = settings.COREAPI
HEADERS = {"Content-Type": "application/json"}

logger = logging.getLogger(__name__)


class NotificacionCorreo:
    def __init__(
        self,
        asunto=None,
        direccion_email=None,
        titulo=None,
        mensaje=None,
        cita=None,
        asesor=None,
        servicios=None,
        preview=None,
    ):
        self.asunto = asunto
        self.direccion_email = direccion_email
        self.mensaje = mensaje
        self.context = {
            # INFORMACION GENERICA
            "preview": preview,
            "titulo": titulo,
            "mensaje": mensaje,
            # ELEMENTOS UI
            "asesor": asesor,
            "cita": cita,
            "servicios": servicios,
            "logo": settings.LOGO,
        }
        self.html = self.render(self.context)

    def render(self, context):
        html = render_to_string("seguimientolite_hyundai_mx/correo.html", context)
        return html

    def enviar(self):
        try:

            email = EmailMessage(subject=self.asunto, body=self.html, to=self.direccion_email)
            email.content_subtype = "html"
            email.send(fail_silently=False)
            return True, self.mensaje
        except Exception as error:
            return False, self.mensaje


def push_groups(no_orden, groups):
    """SENDS NOTIFICATIONS PER GROUP

    Args:
        no_orden (STRING): ORDER IN NOTIFICATION LINK
        groups (LIST): LIST OF GROUPS RECEIVING THE NOTIFICATION
    """
    try:
        for group in groups:
            if group == "asesores":
                tipo = "asesor"
            if group == "jefe de taller":
                tipo = "jefedetaller"
            if group == "repuestos":
                tipo = "refacciones"
            payload = {
                "head": "Seguimiento en Linea | " + settings.AGENCIA,
                "body": f"La inspeccion No. {no_orden} ha sido realizada",
                "url": f"https://{settings.DOMINIO}:{settings.PUERTO}/{tipo}/{no_orden}",
                "icon": settings.LOGO,
            }

            usuarios = User.objects.filter(groups__name=group)
            for usuario in usuarios:
                try:
                    send_user_notification(user=usuario, payload=payload, ttl=1000)
                except Exception:
                    pass
        return True
    except Exception:
        return False


def mail_groups(no_orden, groups, mailing_list):
    """SENDS MAIL PER GROUP

    Args:
        no_orden (STRING): ORDER IN LINK
        groups (LIST): LIST OF GROUPS RECEIVING THE MAIL
        mailing_list (LIST): MAIL ADDRESSES
    """

    try:
        for group in groups:
            if group == "asesores":
                tipo = "asesor"
                mailing_list = settings.SEGUIMIENTOLITE_CORREOS_ASESORES
            if group == "jefe de taller":
                tipo = "jefedetaller"
                mailing_list = settings.SEGUIMIENTOLITE_CORREOS_MANO_DE_OBRA
            if group == "repuestos":
                tipo = "refacciones"
                mailing_list = settings.SEGUIMIENTOLITE_CORREOS_REFACCIONES

            body = f"""La inspeccion No. {no_orden} ha sido realizada \n\n <a href="https://{settings.DOMINIO}:{settings.PUERTO}/{tipo}/{no_orden}"><b>Click Aqui</b></a> """
            email = EmailMessage(
                "Seguimiento en Linea | " + settings.AGENCIA,
                body,
                settings.EMAIL_HOST_USER,
                mailing_list,
            )
            email.content_subtype = "html"
            email.send()
        return True
    except Exception:
        return False


def save_filepond(saving_list):
    """SAVES FILEPOND UPLOADS

    Args:
        saving_list (LIST): FILE'S SERVER ID LIST
    """
    elements = TemporaryUpload.objects.filter(upload_id__in=saving_list)
    for element in elements:
        try:
            os.rename(element.get_file_path(), os.path.join(MEDIA_DIR, element.upload_name))
            element.delete()
        except FileExistsError:
            try:
                element.delete()
            except Exception:
                pass
        logger.debug("Filepond actualizado")


def enviar_whatsapp(prefijo, telefono, mensaje):
    data = {
        "phone": f"{prefijo}{telefono}",
        "body": mensaje,
    }
    try:
        post = api.post(url=COREAPI_URL, data=json.dumps(data), headers=HEADERS)
        if post.status_code == 200:
            return "CORE API: MENSAJE DE WHATSAPP ENVIADO"
        else:
            return "CORE API: ERROR"
    except Exception as error:
        return error


def get_evidencias(context, no_orden):
    """
    Añadir evidencias el context
    """
    context["filas_media"] = []
    context["filas_video"] = []
    media = Evidencias.objects.filter(no_orden=no_orden)
    for file in media:
        try:
            file_type = mimetypes.guess_type(file.evidencia)[0]
            if "video" in file_type:
                context["filas_video"].append(file)
            else:
                context["filas_media"].append(file)
        except Exception as error:
            logger.warning(error)


def crear_actualizar_info(no_orden):
    """
    Crear o actualizar la informacion de la orden
    """
    try:
        inf = VInformacion.objects.filter(no_orden=no_orden).first()
        defaults_informacion = {
            "no_orden": no_orden,
            "id_hd": inf.id_hd,
            "vin": inf.vin,
            "kilometraje": inf.kilometraje,
            "asesor": inf.asesor,
            "cliente": inf.cliente,
            "telefono": inf.telefono,
            "email": inf.email,
            "placas": inf.placas,
            "vehiculo": inf.vehiculo,
            "modelo": inf.modelo,
            "color": inf.color,
            "fecha_hora_ingreso": inf.fecha_hora_ingreso,
            "tecnico": inf.tecnico,
        }
        Informacion.objects.update_or_create(no_orden=no_orden, defaults=defaults_informacion)
    except Exception as error:
        logger.warning(error)


def notificaciones_push(request, context):
    try:
        PushInformation.objects.filter(user=request.user)
        context["user_have_push"] = True
    except Exception:
        context["user_have_push"] = False
