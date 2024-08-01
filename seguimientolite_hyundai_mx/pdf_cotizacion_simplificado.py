from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Literal

from django.conf import settings
from django.db.models import Sum
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import Informacion, Items, ManoDeObra, Refacciones, VTecnicos

FOLDER_PDF: Path = Path(__file__).parent.resolve() / "pdf"

# Imágenes del pdf
CABECERA: Path = FOLDER_PDF / "cabecera.png"
MARCA_DE_AGUA: Path = FOLDER_PDF / "marca_de_agua.png"
PIE_DE_PAGINA: Path = FOLDER_PDF / "pie_de_pagina.png"

# Iconos para el estado del item
IDANGER = Image(FOLDER_PDF / "danger.jpg")
IDANGER.drawHeight = 0.5 * cm
IDANGER.drawWidth = 0.5 * cm
IWARNING = Image(FOLDER_PDF / "warning.jpg")
IWARNING.drawHeight = 0.5 * cm
IWARNING.drawWidth = 0.5 * cm

TEXT: Literal[False] = False

STYLES = getSampleStyleSheet()
STYLEN = STYLES["Heading5"]
STYLEN.alignment = TA_CENTER
STYLEN = STYLES["BodyText"]
STYLEN.alignment = TA_CENTER
STYLEHD = STYLES["Heading5"]
STYLEHD.alignment = TA_LEFT
STYLEBH = STYLES["Normal"]
STYLEBH.alignment = TA_CENTER

STYLEHEADER = STYLES["Heading6"]
STYLEHEADER.alignment = TA_CENTER


class CotizacionSimplificada:
    def __init__(self, no_orden: str):
        self.info: Informacion = Informacion.objects.get(no_orden=no_orden)

        self.items_tecnico = Items.objects.filter(no_orden=no_orden).exclude(estado__in=["Buen Estado", "No Aplica"])
        self.refacciones = Refacciones.objects.filter(no_orden=no_orden)
        self.mano_de_obra = ManoDeObra.objects.filter(no_orden=no_orden)

        self.buffer = BytesIO()

        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=20,
            leftMargin=40,
            topMargin=100,
            bottomMargin=35,
        )

        self.story = []

    def pdf(self):
        # Table header
        table_header = self.get_table_header(self.info)
        self.story.append(table_header)
        self.story.append(Spacer(0, 1.0 * cm))

        # Tablas de items
        no_item = 1
        for item in self.items_tecnico:
            data_item = []

            item_header = self.get_item_header(item, no_item)
            data_item.append(item_header)

            item_body = self.get_item_body(item)
            data_item.append(item_body)

            table_item = self.get_table_item(data_item)
            self.story.append(table_item)

            self.story.append(Spacer(0, 1.2 * cm))

            no_item += 1

        table_totales = self.get_table_totales()
        self.story.append(table_totales)

        self.doc.build(self.story)
        self.buffer.seek(0)

        pdf = self.decorate(self.buffer)
        return pdf

    def get_table_header(self, info: Informacion):
        nombre_tecnico = VTecnicos.objects.get(id_empleado=info.tecnico).nombre_empleado
        h_orden = Paragraph(f"<b>No. de Orden: {info.no_orden}</b>", STYLEHD)
        h_cliente = Paragraph(f"<b>Cliente: {info.cliente} </b>", STYLEHD)
        h_asesor = Paragraph(f"<b>Asesor: {info.asesor}</b>", STYLEHD)
        h_placa = Paragraph(f"<b>No. de Placas:{info.placas}</b>", STYLEHD)
        h_tel = Paragraph(f"<b>Teléfono: {info.telefono}</b>", STYLEHD)
        h_tecnico = Paragraph(f"<b>Técnico: {nombre_tecnico}</b>", STYLEHD)
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
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        return table_header

    def get_item_header(self, item, no_item):
        if item.estado == "Recomendado":
            icon = IWARNING
        elif item.estado == "Inmediato":
            icon = IDANGER
        item_header = [
            icon,
            Paragraph(f"Item Reportado", STYLEHEADER),
            Paragraph("Costo Refacciones", STYLEHEADER),
            Paragraph("Costo Mano de Obra", STYLEHEADER),
            Paragraph("Subtotal", STYLEHEADER),
        ]
        return item_header

    def get_item_body(self, item: Items):
        # Costos
        costo_refacciones = self.refacciones.filter(item=item).aggregate(Sum("subtotal"))["subtotal__sum"]
        if not costo_refacciones:
            costo_refacciones = Decimal("0.00")
        costo_mano_obra = self.mano_de_obra.filter(item=item).aggregate(Sum("subtotal"))["subtotal__sum"]
        if not costo_mano_obra:
            costo_mano_obra = Decimal("0.00")

        subtotal = costo_refacciones + costo_mano_obra

        item_detalle = [
            Paragraph("1", STYLEBH),
            Paragraph(f"{item.item.descripcion}", STYLEBH),
            Paragraph(f"{round(costo_refacciones, 2)}", STYLEBH),
            Paragraph(f"{round(costo_mano_obra, 2)}", STYLEBH),
            Paragraph(f"{round(subtotal, 2)}", STYLEBH),
        ]
        return item_detalle

    def get_table_item(self, data_item):
        table = Table(
            data_item,
            colWidths=[
                1.5 * cm,
                5.5 * cm,
                4.2 * cm,
                4.2 * cm,
                4.2 * cm,
            ],
        )
        table.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (-1, -1), 0.1, colors.black),
                    ("BOX", (0, 0), (-1, -1), 0.1, colors.white),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("SPAN", (1, 0), (1, 0)),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        return table

    def get_table_totales(self):
        data_totales = []

        subtotal_mano_obra = 0
        subtotal = 0
        iva = Decimal("16.00")
        total = 0

        subtotal_refacciones = self.refacciones.aggregate(Sum("subtotal"))["subtotal__sum"]
        if not subtotal_refacciones:
            subtotal_refacciones = 0

        subtotal_mano_obra = self.mano_de_obra.aggregate(Sum("subtotal"))["subtotal__sum"]
        if not subtotal_mano_obra:
            subtotal_mano_obra = 0

        subtotal = subtotal_refacciones + subtotal_mano_obra
        if not subtotal:
            subtotal = 0

        total = subtotal * (1 + (iva / 100))
        if not total:
            total = 0

        data_totales = [
            ["", "", "Subtotal refacciones: ", round(subtotal_refacciones, 2)],
            ["", "", "Subtotal mano de obra: ", round(subtotal_mano_obra, 2)],
            ["", "", "Subtotal neto: ", round(subtotal, 2)],
            ["", "", "IVA: ", str(iva) + "%"],
            ["", "", "Total a pagar: ", round(total, 2)],
        ]

        table_totales = Table(data_totales, colWidths=[7.0 * cm, 7.0 * cm, 7.0 * cm, 7.0 * cm])
        table_totales.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (-1, -1), 0.15, colors.white),
                    ("BOX", (0, 0), (-1, -1), 0.25, colors.white),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                ]
            )
        )
        return table_totales

    def decorate(self, buff):
        pdfbuff = BytesIO()
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

        finalpdf = BytesIO()
        output_file.write(finalpdf)
        finalpdf.seek(0)
        return finalpdf
