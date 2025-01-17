# Generated by Django 3.2 on 2024-01-24 10:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('seguimientolite_hyundai_mx', '0003_vistas2'),
    ]

    operations = [
        migrations.CreateModel(
            name='KpisGeneral',
            fields=[
                ('no_orden', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('no_placas', models.CharField(blank=True, max_length=10, null=True)),
                ('fecha_hora_entrada', models.DateTimeField(blank=True, null=True)),
                ('fecha_hora_salida', models.DateTimeField(blank=True, null=True)),
                ('kilometraje', models.IntegerField(blank=True, null=True)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('asesor', models.CharField(blank=True, max_length=150, null=True)),
                ('vin', models.CharField(blank=True, max_length=50, null=True)),
                ('modelo', models.CharField(blank=True, max_length=250, null=True)),
                ('year_vehiculo', models.IntegerField(blank=True, null=True)),
                ('cliente', models.CharField(blank=True, max_length=200, null=True)),
                ('telefono', models.CharField(blank=True, max_length=50, null=True)),
                ('multipuntos', models.IntegerField()),
                ('tecnico', models.CharField(blank=True, max_length=60, null=True)),
                ('inmediato', models.IntegerField(blank=True, null=True)),
                ('buen_estado', models.IntegerField(blank=True, null=True)),
                ('recomendado', models.IntegerField(blank=True, null=True)),
                ('videos', models.IntegerField(blank=True, null=True)),
                ('fotos', models.IntegerField(blank=True, null=True)),
                ('cotizacion', models.IntegerField()),
                ('envio_cotizacion', models.IntegerField()),
                ('envio_email', models.IntegerField(blank=True, null=True)),
                ('envio_whatsapp', models.IntegerField(blank=True, null=True)),
                ('vista_cliente', models.IntegerField()),
                ('autorizados', models.IntegerField(blank=True, null=True)),
                ('detalle_items_autorizados', models.TextField(blank=True, null=True)),
                ('monto_autorizado', models.DecimalField(blank=True, decimal_places=2, max_digits=38, null=True)),
                ('monto_no_autorizado', models.DecimalField(blank=True, decimal_places=2, max_digits=38, null=True)),
                ('porcentaje_autorizado', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
                ('porcentaje_no_autorizado', models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True)),
            ],
            options={
                'db_table': 'kpis_general',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VPantallaRecepcion',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('asesor', models.CharField(blank=True, max_length=150, null=True)),
                ('hora_asesor', models.CharField(blank=True, max_length=5, null=True)),
                ('hora_recepcion', models.CharField(blank=True, max_length=5, null=True)),
                ('tipo_llegada', models.CharField(max_length=5)),
                ('placas', models.CharField(blank=True, max_length=10, null=True)),
                ('cliente', models.CharField(blank=True, max_length=25, null=True)),
                ('servicio_capturado', models.CharField(blank=True, max_length=25, null=True)),
                ('vehiculo', models.CharField(blank=True, max_length=20, null=True)),
                ('estatus_orden', models.CharField(max_length=30)),
                ('tipo_cliente', models.CharField(blank=True, max_length=25, null=True)),
                ('numcita', models.CharField(db_column='NUMCITA', max_length=25)),
                ('cita', models.IntegerField()),
            ],
            options={
                'db_table': 'v_pantalla_recepcion',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='VRevisionCalidadRi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_calidad', models.IntegerField()),
                ('id_sector', models.IntegerField()),
                ('id_item', models.IntegerField()),
                ('id_opcion', models.IntegerField()),
                ('opcion', models.CharField(max_length=50)),
                ('nombre', models.CharField(blank=True, max_length=200, null=True)),
                ('no_orden', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'v_revision_calidad_ri',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ArchivoFirmasTecnico',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('id_tecnico', models.CharField(blank=True, max_length=50, null=True)),
                ('imagen_firma', models.FileField(blank=True, null=True, upload_to='firmas_tecnico')),
            ],
        ),
        migrations.CreateModel(
            name='ArchivosFirmasAsesor',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('id_asesor', models.CharField(blank=True, max_length=50, null=True)),
                ('imagen_firma', models.FileField(blank=True, null=True, upload_to='firmas_asesor')),
            ],
        ),
        migrations.AlterModelOptions(
            name='listaitems',
            options={'managed': True, 'verbose_name': 'Item', 'verbose_name_plural': 'Lista de Items'},
        ),
        migrations.AlterModelOptions(
            name='listaitemstecnicocaptura',
            options={'managed': True, 'verbose_name': 'Item de Captura', 'verbose_name_plural': 'Lista de Items de Captura'},
        ),
        migrations.AlterModelOptions(
            name='revisiones',
            options={'managed': True, 'verbose_name': 'Revisión', 'verbose_name_plural': 'Revisiones'},
        ),
        migrations.AddField(
            model_name='listaitems',
            name='no_aplica_x',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listaitems',
            name='no_aplica_y',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listaitems',
            name='no_x',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listaitems',
            name='no_y',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listaitems',
            name='si_x',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listaitems',
            name='si_y',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='listaitems',
            name='unidad',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='revisiones',
            name='guia_mantenimiento',
            field=models.FileField(blank=True, null=True, upload_to='guias_mantenimiento'),
        ),
        migrations.CreateModel(
            name='ListaItemsFamilias',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('orden', models.IntegerField(blank=True, null=True)),
                ('nombre', models.CharField(blank=True, max_length=100, null=True)),
                ('descripcion', models.CharField(blank=True, max_length=300, null=True)),
                ('descripcion_adicional', models.CharField(blank=True, max_length=1000, null=True)),
                ('imagen', models.FileField(blank=True, null=True, upload_to='lista_items_familias')),
                ('video', models.FileField(blank=True, null=True, upload_to='lista_items_familias')),
                ('revision', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='seguimientolite_hyundai_mx.revisiones')),
            ],
            options={
                'verbose_name': 'Familia de Items',
                'verbose_name_plural': 'Familias de Items',
                'db_table': 'lista_items_familias',
                'managed': True,
            },
        ),
        migrations.AlterField(
            model_name='listaitems',
            name='familia',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='seguimientolite_hyundai_mx.listaitemsfamilias'),
        ),
    ]
