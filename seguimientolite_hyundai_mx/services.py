from rest_framework import viewsets, status, views, decorators
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.conf import settings
from pathlib import Path
from .pdf_cotizacion import cotizacion_pdf

from .models import Informacion, Items, Refacciones, ManoDeObra, ListaItems, VTecnicos, VInformacion

class GetCotizacionPDF(APIView):

    def post(self, request):
        
        if request.data.get("no_orden"):
            orden = request.data["no_orden"]

            try:
                refacciones = Refacciones.objects.filter(no_orden=orden).values_list("id", flat=True)
                mano_de_obra = ManoDeObra.objects.filter(no_orden=orden).values_list("id", flat=True)
                pdf = cotizacion_pdf(request.data["no_orden"], refacciones_ids=refacciones, mano_de_obra_ids= mano_de_obra)

                FOLDER_COTIZACION = Path(settings.MEDIA_ROOT / "cotizacion_pdf" / f"{orden}.pdf")

                URL_ARCHIVO_COTIZACION = settings.DOMINIO + ":" + settings.PUERTO + f"/media/cotizacion_pdf/{orden}.pdf"
                
                
                with FOLDER_COTIZACION.open("wb") as f:
                    f.write(pdf.getbuffer())
                
                return Response({"details":"Archivo generado correctamente, la URL del archivo es el valor de la clave url","success": True, "url":URL_ARCHIVO_COTIZACION}, status=status.HTTP_200_OK)


            except Exception as error:
                print(error)
                return Response({"details":"Ha ocurrido un error al generar el archivo","success":False}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"details":"El request debe contener el número de orden como no_orden", "success":False}, status=status.HTTP_400_BAD_REQUEST)



class GetVehicleHealthCheck(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        
        if not request.data.get("no_orden"):
            return Response({"details":"Debe especificar el número de orden como 'no_orden' en formato JSON", "success":False}, status=status.HTTP_400_BAD_REQUEST )
        
        response = {}
        orden = request.data["no_orden"]
        query_tecnico = Items.objects.filter(no_orden=orden).exclude(estado__contains="Buen").exclude(estado__contains="Aplica").values()
        response["no_orden"] = request.data["no_orden"]
        response["items_revisados"] = []

        if query_tecnico.count() > 0:
            try:
                for item in query_tecnico:    
                    response["items_revisados"].append({
                        "item" : ListaItems.objects.get(id=item["item_id"]).descripcion,
                        "estado" : item["estado"],
                        "comentarios": item["comentarios"],
                        "valor" : item["valor"],
                        "unidad" : ListaItems.objects.get(id=item["item_id"]).unidad,
                        "tecnico" : VTecnicos.objects.get(id_empleado=item["tecnico"]).nombre_empleado,
                        "fecha_hora_fin" : item["fecha_hora_fin"],
                    })
            
                response["success"] = True
                return Response(data=response, status=status.HTTP_200_OK)
            
            except Exception as error:
                return Response({"success":False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        else:
            return Response({"details":"No existe revisión del técnico o no hay ítems reportados como Recomendados o Inmediatos","success":False}, status=status.HTTP_404_NOT_FOUND)


class GetItemsRejected(APIView):
    parser_clases =[JSONParser]

    def post(self, request):
        if not request.data.get("vin"):
            return Response({
                "details":"Debe especificar la clave VIN como vin", 
                "success":False},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = {}
        vin = request.data.get("vin")
        query = VInformacion.objects.filter(vin=vin).values_list("no_orden", flat=True)

        print(query)
            


        



    


