import os
import io
from decimal import Decimal

from django.db.models import Sum, F, DecimalField
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .models import Informacion, Items, Refacciones, ManoDeObra


CWD = os.path.dirname(os.path.abspath(__file__))
# Imágenes del pdf
CABECERA = os.path.join(CWD, "pdf", "cabecera.png")
MARCA_DE_AGUA = os.path.join(CWD, "pdf", "marca_de_agua.png")
PIE_DE_PAGINA = os.path.join(CWD, "pdf", "pie_de_pagina.png")

# Iconos para el estado del item
IDANGER = Image(os.path.join(CWD, "pdf", "danger.jpg"))
IDANGER.drawHeight = 0.5 * cm
IDANGER.drawWidth = 0.5 * cm

IWARNING = Image(os.path.join(CWD, "pdf", "warning.jpg"))
IWARNING.drawHeight = 0.5 * cm
IWARNING.drawWidth = 0.5 * cm

TEXT = False

STYLES = getSampleStyleSheet()
STYLEN = STYLES["Heading5"]
STYLEN.alignment = TA_CENTER
STYLEN = STYLES["BodyText"]
STYLEN.alignment = TA_CENTER
STYLEHD = STYLES["Heading5"]
STYLEHD.alignment = TA_LEFT
STYLEBH = STYLES["Normal"]
STYLEBH.alignment = TA_CENTER


def cotizacion_pdf(no_orden, refacciones_ids, mano_de_obra_ids):
    # Información de la orden
    info = Informacion.objects.get(no_orden=no_orden)
    items_tecnico = Items.objects.filter(no_orden=no_orden).exclude(estado="Buen Estado").exclude(estado="No aplica")
    refacciones = Refacciones.objects.filter(no_orden=no_orden, id__in=refacciones_ids)
    mano_de_obra = ManoDeObra.objects.filter(no_orden=no_orden, id__in=mano_de_obra_ids)

    no_item = 1

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=40,
        topMargin=100,
        bottomMargin=35,
    )
    story = []

    # Table header
    table_header = get_table_header(info)
    story.append(table_header)
    story.append(Spacer(0, 1.0 * cm))

    # Tablas de items
    for item in items_tecnico:
        data_item = []
        item_header = get_item_header(item, no_item)
        data_item.append(item_header)
        if refacciones_ids:
            refacciones_header = get_refacciones_header()
            data_item.append(refacciones_header)
            refacciones_rows = get_refacciones_rows(refacciones, item)
            data_item += refacciones_rows
        if mano_de_obra_ids:
            mo_header = get_mano_de_obra_header()
            data_item.append(mo_header)
            mano_de_obra_rows = get_mano_de_obra_rows(mano_de_obra, item)
            data_item += mano_de_obra_rows
        table_item = get_table_item(data_item)
        story.append(table_item)
        story.append(Spacer(0, 1.2 * cm))
        no_item += 1

    # Tabla de totales
    table_totales = get_table_totales(refacciones, mano_de_obra)

    story.append(table_totales)
    doc.build(story)
    buffer.seek(0)

    pdf = decorate(buffer)
    return pdf


def get_table_header(info):
    h_orden = Paragraph(f"<b>No. de Orden: {info.no_orden}</b>", STYLEHD)
    h_cliente = Paragraph(f"<b>Cliente: {info.cliente} </b>", STYLEHD)
    h_asesor = Paragraph(f"<b>Asesor: {info.asesor}</b>", STYLEHD)
    h_placa = Paragraph(f"<b>No. de Placas:{info.placas}</b>", STYLEHD)
    h_tel = Paragraph(f"<b>Teléfono: {info.telefono}</b>", STYLEHD)
    h_tecnico = Paragraph(f"<b>Técnico: {info.tecnico}</b>", STYLEHD)
    h_vin = Paragraph(f"<b>VIN: {info.vin}</b>", STYLEHD)
    h_email = Paragraph(f"<b>Email: {info.email}</b>", STYLEHD)
    h_vehiculo = Paragraph(f"<b>Vehículo: {info.vehiculo}</b>", STYLEHD)

    data_header = [
        [h_orden, h_placa, h_vin],
        [h_cliente, h_tel, h_email],
        [h_asesor, h_tecnico, h_vehiculo],
    ]

    table_header = Table(data_header, colWidths=[7.0 * cm, 7.0 * cm, 7.0 * cm])
    table_header.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.15, colors.white),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table_header


def get_item_header(item, no_item):
    if item.estado == "Recomendado":
        icon = IWARNING
    if item.estado == "Inmediato":
        icon = IDANGER
    item_header = [
        icon,
        Paragraph(f"{no_item}. {item.item.descripcion}", STYLEHD),
        "",
        "",
        "",
    ]
    return item_header


def get_refacciones_header():
    h_cantidad = Paragraph("<b>Cantidad</b>", STYLEN)
    h_descripcion = Paragraph("<b>Descripcion</b>", STYLEN)
    h_costo_ref = Paragraph("<b>Costo Repuestos</b>", STYLEN)
    h_desc_ref = Paragraph("<b>%Desc.</b>", STYLEN)
    h_subtotal = Paragraph("<b>Subtotal</b>", STYLEN)

    refacciones_header = [h_cantidad, h_descripcion, h_costo_ref, h_desc_ref, h_subtotal]
    return refacciones_header


def get_refacciones_rows(refacciones, item):
    refacciones_rows = []
    for refaccion in refacciones:
        if refaccion.item == item:
            refacciones_rows.append(
                [
                    Paragraph(str(refaccion.cantidad), STYLEBH),
                    Paragraph(str(refaccion.nombre), STYLEBH),
                    Paragraph(str(refaccion.precio_unitario), STYLEBH),
                    Paragraph(str(refaccion.porcentaje_descuento), STYLEBH),
                    Paragraph(str(refaccion.subtotal), STYLEBH),
                ]
            )
    return refacciones_rows


def get_mano_de_obra_header():
    h_cantidad = Paragraph("<b>Cantidad</b>", STYLEN)
    h_descripcion = Paragraph("<b>Descripcion</b>", STYLEN)
    h_costo_mo = Paragraph("<b>Mano de obra</b>", STYLEN)
    h_desc_mo = Paragraph("<b>%Desc.</b>", STYLEN)
    h_subtotal = Paragraph("<b>Subtotal</b>", STYLEN)

    refacciones_header = [h_cantidad, h_descripcion, h_costo_mo, h_desc_mo, h_subtotal]
    return refacciones_header


def get_mano_de_obra_rows(mano_de_obra, item):
    mano_de_obra_rows = []
    for mo in mano_de_obra:
        if mo.item == item:
            mano_de_obra_rows.append(
                [
                    Paragraph(str(mo.cantidad_uts), STYLEBH),
                    Paragraph(str(mo.nombre), STYLEBH),
                    Paragraph(str(round(mo.precio_ut * mo.cantidad_uts, 2)), STYLEBH),
                    Paragraph(str(mo.porcentaje_descuento), STYLEBH),
                    Paragraph(str(mo.subtotal), STYLEBH),
                ]
            )
    return mano_de_obra_rows


def get_table_item(data_item):
    table = Table(
        data_item,
        colWidths=[
            1.95 * cm,
            4.0 * cm,
            2.8 * cm,
            1.8 * cm,
            2.5 * cm,
        ],
    )
    table.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.1, colors.white),
                ("BOX", (0, 0), (-1, -1), 0.1, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("SPAN", (1, 0), (4, 0)),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return table


def get_table_totales(refacciones, mano_de_obra):
    data_totales = []

    subtotal_ref_no_desc = 0
    subtotal_ref_desc = 0
    subtotal_ref_iva = 0

    subtotal_mo_no_desc = 0
    subtotal_mo_desc = 0
    subtotal_mo_iva = 0

    try:
        porcentaje_iva = refacciones.first().porcentaje_iva
    except Exception:
        porcentaje_iva = mano_de_obra.first().porcentaje_iva

    if refacciones:
        subtotal_ref_no_desc = refacciones.aggregate(
            total=Sum(F("precio_unitario") * F("cantidad"), output_field=DecimalField(max_digits=18, decimal_places=2))
        )["total"]
        subtotal_ref_desc = refacciones.aggregate(Sum("subtotal"))["subtotal__sum"]
        subtotal_ref_iva = refacciones.aggregate(Sum("subtotal_iva"))["subtotal_iva__sum"]
        if not subtotal_ref_no_desc:
            subtotal_ref_no_desc = 0
        if not subtotal_ref_desc:
            subtotal_ref_desc = 0
        if not subtotal_ref_iva:
            subtotal_ref_iva = 0
        subtotales_ref = [
            ["", "", "SUBTOTAL REPUESTOS", str(subtotal_ref_no_desc)],
            ["", "", "DESCUENTO REPUESTOS", str(subtotal_ref_no_desc - subtotal_ref_desc)],
        ]
        data_totales += subtotales_ref

    if mano_de_obra:
        subtotal_mo_no_desc = mano_de_obra.aggregate(
            total=Sum(F("cantidad_uts") * F("precio_ut"), output_field=DecimalField(max_digits=18, decimal_places=2))
        )["total"]
        subtotal_mo_desc = mano_de_obra.aggregate(Sum("subtotal"))["subtotal__sum"]
        subtotal_mo_iva = mano_de_obra.aggregate(Sum("subtotal_iva"))["subtotal_iva__sum"]
        if not subtotal_mo_no_desc:
            subtotal_mo_no_desc = 0
        if not subtotal_mo_desc:
            subtotal_mo_desc = 0
        if not subtotal_mo_iva:
            subtotal_mo_iva = 0
        subtotales_mo = [
            ["", "", "SUBTOTAL MANO DE OBRA", str(round(subtotal_mo_no_desc, 2))],
            ["", "", "DESCUENTO MANO DE OBRA", str(round(subtotal_mo_no_desc - subtotal_mo_desc, 2))],
        ]
        data_totales += subtotales_mo

    totales_fin = [
        ["", "", "SUBTOTAL NETO", str(round(subtotal_ref_no_desc + subtotal_mo_no_desc, 2))],
        ["*** VALIDEZ DE PROFORMA 15 DIAS ", "", "IVA", str(porcentaje_iva)[2:] + "%"],
        [
            "",
            "",
            "TOTAL A PAGAR:",
            str(subtotal_mo_iva + subtotal_ref_iva),
        ],
    ]
    data_totales += totales_fin

    table_totales = Table(data_totales, colWidths=[6.0 * cm, 6.0 * cm, 4.5 * cm, 3.0 * cm])
    table_totales.setStyle(
        TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.15, colors.white),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (3, 0), (3, 6), "LEFT"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("SPAN", (0, 5), (1, 5)),
                ("SPAN", (0, 6), (1, 6)),
            ]
        )
    )
    return table_totales


def decorate(buff):
    pdfbuff = io.BytesIO()
    c = canvas.Canvas(pdfbuff)

    try:
        c.drawImage(CABECERA, 1, 719, 21.2 * cm, 2.5 * cm, mask="auto")
    except Exception:
        pass
    try:
        c.drawImage(MARCA_DE_AGUA, 50, 140, 18 * cm, 15 * cm, mask="auto")
    except Exception:
        pass

    try:
        c.drawImage(PIE_DE_PAGINA, 5, 5, 21.2 * cm, 1.3 * cm, mask="auto")
    except Exception:
        pass

    # fondo(c)
    if TEXT:
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.white)
        c.drawString(5.7 * cm, 720, TEXT)
        c.setFillColor(colors.black)
        c.drawString(8.6 * cm, 700, "PRESUPUESTO")
    c.save()
    pdfbuff.seek(0)

    output_file = PdfFileWriter()
    input_file = PdfFileReader(buff)
    watermark = PdfFileReader(pdfbuff)
    page_count = input_file.getNumPages()
    for page_number in range(page_count):
        input_page = input_file.getPage(page_number)
        input_page.mergePage(watermark.getPage(0))
        output_file.addPage(input_page)

    finalpdf = io.BytesIO()
    output_file.write(finalpdf)
    finalpdf.seek(0)
    return finalpdf
