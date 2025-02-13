# Generated by Django 5.1.5 on 2025-02-08 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_alter_usuario_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='contador_reenvios',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='usuario',
            name='token_expiracion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='ultimo_reenvio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
