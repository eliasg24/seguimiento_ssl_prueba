# chat/urls.py
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import client_autologin

from . import services, views

urlpatterns = [
    # Login
    path("login", views.staff_login, name="staff_login"),
    path("logout", LogoutView.as_view(), name="logout"),
    # Técnico
    path("tecnico/<str:id_tecnico>/<str:no_orden>", views.tecnico, name="tecnico"),
    # Refacciones
    path("refacciones", views.refacciones, name="refacciones"),
    path("refacciones/<str:no_orden>", views.refacciones_detalle, name="refacciones_detalle"),
    # Mano de obra
    path("mano_de_obra", views.mano_de_obra, name="mano_de_obra"),
    path("mano_de_obra/<str:no_orden>", views.mano_de_obra_detalle, name="mano_de_obra_detalle"),
    # ASESOR
    path("asesor", views.asesor, name="ordenes"),
    path("asesor/<str:no_orden>", views.asesor_detalle, name="detalle_ordenes"),
    # PDF CALIDAD
    path("calidad_pdf/<str:no_orden>", views.hoja_multipuntos_pdf, name="pdf_multipuntos"),
    # HISTORIAL
    path("historial", views.historial, name="historial"),
    path("historial/<str:no_orden>", views.historial_detalle, name="historial_detalle"),
    # CLIENTE
    path('cliente/<str:encrypt_number_no_orden>/', views.client_autologin, name="cliente_login"),
    path("cotizacion/<str:encrypt_number_no_orden>/", views.cliente_detalle, name="cliente_cotizacion"),
    path("error/", views.Error404View.as_view(), name="error_404"),
      path('error/', views.Error500View.as_view(), name='error_500'),
    # REDIRIGIR A LOGIN
    path("", views.staff_login, name="re_login"),
    # KPIS
    path("kpis/resumen", views.kpis_resumen, name="kpis_resumen"),
    path("kpis/financiero", views.kpis_financiero, name="kpis_financiero"),
    path("kpis/general/", views.kpis_general, name="kpis_general"),
    path(
        "kpis/general_pdf/<str:fecha_inicio>/<str:fecha_fin>/<str:asesores>/",
        views.kpis_general_pdf,
        name="kpis_general_pdf",
    ),
    path("kpis/general/<str:no_orden>/", views.kpis_general_detalle, name="kpis_general_detalle"),
    path(
        "kpis/general_pdf/<str:no_orden>/",
        views.kpis_general_detalle_pdf,
        name="kpis_general_detalle_pdf",
    ),
    # SERVICIOS
    path("services/get_pdf_cotizacion", services.GetCotizacionPDF.as_view(), name="get_pdf_cotizacion"),
    path(
        "services/get_vehicle_health_check", services.GetVehicleHealthCheck.as_view(), name="get_vehicle_health_check"
    ),
    path("services/get_items_rejected", services.GetItemsRejected.as_view(), name="get_items_rejected"),
    # ESPECIALES
    path("pantalla_recepcion/", views.PantallaRecepcionView.as_view(), name="pantalla_recepcion"),
]

handler404 = 'seguimientolite_hyundai_mx.views.handler404'
handler500 = 'seguimientolite_hyundai_mx.views.handler500'