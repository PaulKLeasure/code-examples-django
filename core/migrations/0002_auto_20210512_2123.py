# Generated by Django 3.1.7 on 2021-05-12 21:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='effectDate',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]
