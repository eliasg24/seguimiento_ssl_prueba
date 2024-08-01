import io
import logging
import os
import textwrap
from datetime import datetime

from django.conf import settings
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize

from .models import (
    ActividadesAsesorFirmas,
    ActividadesTecnicoCaptura,
    ArchivoFirmasTecnico,
    ArchivosFirmasAsesor,
    Informacion,
    Items,
    ListaItems,
    ListaItemsTecnicoCaptura,
    Revisiones,
    VRevisionCalidadRi,
    VTecnicos,
    VUsuarios,
)

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
FORMATO_MULTIPUNTOS = os.path.join(THIS_FOLDER, "pdf", "hoja_multipuntos.pdf")


def get_pdf_calidad(no_orden):
    buffer = io.BytesIO()

    # Información general
    info = Informacion.objects.get(no_orden=no_orden)
    tecnico = VTecnicos.objects.get(id_empleado=info.tecnico).nombre_empleado
    lista_items = ListaItems.objects.all()
    lista_items_captura = ListaItemsTecnicoCaptura.objects.all()

    # Inspección de técnico
    queryset_tecnico = Items.objects.filter(no_orden=no_orden)
    queryset_tecnico_captura = ActividadesTecnicoCaptura.objects.filter(no_orden=no_orden)
    revisiones = queryset_tecnico.values_list("item__familia__revision", flat=True).distinct()

    # Inspección RI
    queryset_calidad_ri = VRevisionCalidadRi.objects.filter(no_orden=no_orden).order_by("-id_item")
    output = PdfFileWriter()

    for id_revision in revisiones:
        revision_pdf = Revisiones.objects.get(id=id_revision).guia_mantenimiento.path
        existing_pdf = PdfFileReader(open(revision_pdf, "rb"))
        for page_no in range(existing_pdf.getNumPages()):
            can = canvas.Canvas(buffer, pagesize=(620, 990))
            can.setFont("Helvetica-Bold", 7)

            caracter_default = "✓"
            caracter_no_default = "x"

            # Escritura de la información de la orden
            if page_no == 0:
                try:
                    can.drawString(250, 940, info.no_orden)
                    can.drawString(250, 927, info.cliente)
                    can.drawString(250, 914, info.vehiculo)
                    can.drawString(250, 900, info.placas)
                    can.drawString(250, 887, info.kilometraje)
                    can.drawString(360, 40, tecnico)
                    can.drawString(250, 874, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                    can.drawString(215, 40, info.asesor)
                    ## Información del distribuidor
                    can.drawString(425, 943, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_1)
                    can.drawString(425, 930, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_2)
                    can.drawString(425, 917, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_3)
                    can.drawString(425, 904, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_4)
                    can.drawString(425, 891, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_5)
                    can.drawString(425, 878, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_6)
                    can.drawString(425, 865, settings.SEGUIMIENTOLITE_ENCABEZADO_LINEA_7)
                except Exception:
                    pass

            # Escritura del estado de la revisión de RI

            coord_y = 170
            for item in queryset_calidad_ri:
                if "bien" in str(item.opcion).lower():
                    can.drawString(555, coord_y, caracter_default)
                    coord_y += 15

                else:
                    can.drawString(555, coord_y, caracter_no_default)
                    coord_y += 15

            # Escritura del estado de cada item de la hoja multipuntos
            for item_formato in lista_items.filter(revision_id=id_revision, pagina=page_no):
                if queryset_tecnico.filter(item=item_formato, item__familia__revision_id=id_revision).exists():
                    item_inspeccionado = queryset_tecnico.get(item=item_formato, item__familia__revision_id=id_revision)

                    # Estado del item
                    try:
                        if item_inspeccionado.estado == "Buen Estado":
                            can.drawString(item_formato.g_x, item_formato.g_y, caracter_default)
                        if item_inspeccionado.estado == "Recomendado":
                            try:
                                can.drawString(item_formato.y_x, item_formato.y_y, caracter_no_default)
                            except Exception:
                                can.drawString(item_formato.r_x, item_formato.r_y, caracter_no_default)
                        if item_inspeccionado.estado == "Inmediato":
                            can.drawString(item_formato.r_x, item_formato.r_y, caracter_no_default)
                    except Exception:
                        pass

                    # Valor capturado
                    try:
                        if item_inspeccionado.valor:
                            can.drawString(
                                item_formato.valor_x,
                                item_formato.valor_y,
                                item_inspeccionado.valor,
                            )
                    except Exception:
                        pass

                    # Item cambiado
                    if item_inspeccionado.cambiado:
                        can.drawString(
                            item_formato.modificado_x,
                            item_formato.modificado_y,
                            caracter_default,
                        )
                else:
                    logger.debug(f"Hoja Multipuntos: no se encuentra el item '{item_formato.descripcion}'")

            # Escritura de comentarios de diagnostico
            if queryset_tecnico_captura:
                can.setFont("Helvetica", 9)
                for item_formato in lista_items_captura:
                    try:
                        item_inspeccionado = queryset_tecnico_captura.filter(item=item_formato.nombre).first()

                        text = textwrap.fill(item_inspeccionado.valor, item_formato.line_size)
                        box = can.beginText(item_formato.x, item_formato.y)
                        box.textLines(text)
                        can.drawText(box)
                    except Exception as error:
                        logger.warning(error)

            # Escritura de la firma
            can.setFont("Helvetica-Bold", 7)
            try:
                firma = ActividadesAsesorFirmas.objects.get(no_orden=no_orden).firma
                can.drawImage(os.path.join(settings.MEDIA_ROOT, firma), 362, 22, 90, 45, mask="auto")
            except Exception as error:
                logger.debug(f"Hoja multipuntos: No hay firma de cliente: {error}")

            # firma del asesor y tecnico
            try:
                id_asesor = VUsuarios.objects.get(nombre=info.asesor).cveasesor

                firma_asesor = ArchivosFirmasAsesor.objects.get(id_asesor=id_asesor).imagen_firma
                can.drawImage(os.path.join(settings.MEDIA_ROOT, str(firma_asesor)), 205, 45, 120, 60, mask="auto")

                firma_tecnico = ArchivoFirmasTecnico.objects.get(id_tecnico=info.tecnico).imagen_firma
                can.drawImage(os.path.join(settings.MEDIA_ROOT, str(firma_tecnico)), 350, 45, 120, 60, mask="auto")

            except Exception as error:
                logger.debug(f"Hoja Multipuntos: no se encuentra la firma del asesor o del técnico: {error}")

            can.showPage()
            can.save()
            buffer.seek(0)

            datos_multipuntos = PdfFileReader(buffer)
            page = existing_pdf.getPage(page_no)
            page.mergePage(datos_multipuntos.getPage(0))

            output.addPage(page)
    buffer_pdf = io.BytesIO()
    output.write(buffer_pdf)
    buffer_pdf.seek(0)
    return buffer_pdf
