from django.conf import settings
from django.db import migrations

TABLERO_DB = settings.TABLERO_DB


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("seguimientolite_hyundai_mx", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            f"""
            create view [dbo].[v_informacion] as
            select distinct 
            no_orden = a.noorden,
            id_hd = a.id_hd,
            vin= a.vin,
            kilometraje= a.Kilometraje,
            asesor= case when a.idasesor = '' then 'Sin asesor registrado' else (select top 1 nombre from {TABLERO_DB}.dbo.SccUsuarios where cveAsesor=a.idAsesor) end,
            cliente= a.cliente,
            telefono= a.ContactoTelefono,
            email= a.ContactoNombre,
            placas= a.noPlacas,
            vehiculo= a.Vehiculo,
            modelo= '',
            color = '',
            tecnico = (select top 1 idtecnico from [{TABLERO_DB}].[dbo].[Tb_CITAS] where noorden = a.NOORDEN and servicioCapturado <>'lavado' and idTecnico not like '%c%'),
            fecha_hora_ingreso= a.Horallegada
            from [{TABLERO_DB}].dbo.tb_citas_header_nw as a with (nolock)
            """
        ),
        migrations.RunSQL(
            f"""
            CREATE view [dbo].[v_operaciones_tecnico] as 
            select top 100 percent
                id = row_number() over (order by a.fecha desc),
                id_hd= a.id_hd,
                vin=a.vin,
                no_orden = a.noorden,
                placas= b.noplacas,
                tecnico = t.NOMBRE_EMPLEADO,
                asesor = case when a.idasesor = '' then 'Sin asesor registrado' else (select top 1 nombre from {TABLERO_DB}.dbo.SccUsuarios where cveAsesor=a.idAsesor) end,
                vehiculo = b.vehiculo,
                fecha_llegada = cast(b.horallegada as date),
                hora_promesa = b.fecha_hora_com,
                cliente=b.cliente,

                servicio_capturado = (case 

                when a.serviciocapturado like '%Servicio%' then 'Servicio'
                when a.servicioCapturado like '%Diagnostico%' then 'Diagnostico'
                when a.servicioCapturado like '%Reparacion%' then 'Reparacion'
                else a.servicioCapturado end)	
                from [{TABLERO_DB}].dbo.tb_citas as a 
                join [{TABLERO_DB}].dbo.Tb_CITAS_HEADER_NW as b on a.id_hd = b.id_hd
                left join [{TABLERO_DB}].dbo.tb_tecnicos as t on a.idTecnico = t.id_empleado

                where t.NOMBRE_EMPLEADO<>'NO SHOW'
                and b.HoraRetiro is null
                and b.Horallegada is not null
                and b.noOrden <> '0'
                and b.fecha > '20191101'
                and a.servicioCapturado <> 'Lavado'
            """
        ),
        migrations.RunSQL(
            f"""
            CREATE view [dbo].[v_operaciones_refacciones] as 

            with cte_realizadas_tecnico as (
                select distinct 
                    a.no_orden, 
                    tecnico= (select top 1 nombre_empleado from {TABLERO_DB}.dbo.Tb_TECNICOS  where ID_EMPLEADO = a.tecnico ),
                    fin_tecnico=max(a.fecha_hora_fin) 
                from actividades_tecnico as a with (nolock)
                where fecha_hora_fin is not null
                group by no_orden, tecnico

            ),
            cte_ordenes_activas as(
                select distinct
                    a.no_orden,
                    fecha_ingreso = a.fecha_llegada,
                    vin = a.vin,
                    vehiculo = a.vehiculo,
                    placas = a.placas,
                    asesor = a.asesor

                from v_operaciones_tecnico as a with (nolock)
            )

                select 
                    b.no_orden,
                    b.tecnico,
                    b.fin_tecnico,
                    a.fecha_ingreso,
                    a.vin,
                    a.vehiculo,
                    a.placas,
                    a.asesor

                from  cte_ordenes_activas as a 
                inner join cte_realizadas_tecnico as b on a.no_orden collate DATABASE_DEFAULT =b.no_orden collate DATABASE_DEFAULT 
            """
        ),
        migrations.RunSQL(
            f"""
            CREATE view [dbo].[v_operaciones_asesor_alt] as 

            select distinct 

            no_orden,
            placas,
            vin,
            vehiculo,
            asesor

            from v_operaciones_tecnico
            where no_orden in (select no_orden from actividades_refacciones where fecha_hora_fin is not null)
            """
        ),
    ]
