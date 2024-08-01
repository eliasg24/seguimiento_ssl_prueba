from django.conf import settings
from django.db import migrations

TABLERO_DB = settings.TABLERO_DB


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("seguimientolite_hyundai_mx", "0002_vistas"),
    ]

    operations = [
        migrations.RunSQL(
            f"""
            create view [dbo].[v_tecnicos] as 
            select * from [{TABLERO_DB}].dbo.tb_tecnicos
            """
        ),
        migrations.RunSQL(
            f"""
            create view [dbo].[v_usuarios] as
            select a.*,
            id = row_number() over (order by a.pass desc),
            last_login='',
            Is_superuser= case when a.cvePerfil=1 then 1 else 0 end,
            last_name= getdate(),
            is_staff= 1,
            is_active= 1,
            date_joined= cast('20190101' as datetime)
            from {TABLERO_DB}.dbo.sccusuarios as a
            """
        ),
    ]
