# Generated by Django 5.1.5 on 2025-02-10 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0007_remove_usuario_email_sent_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='reset_password_token',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='reset_password_token_created',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
