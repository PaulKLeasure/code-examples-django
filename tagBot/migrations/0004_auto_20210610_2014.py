# Generated by Django 3.1.7 on 2021-06-10 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tagBot', '0003_auto_20210610_2012'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tagbotmapping',
            old_name='code',
            new_name='nomenclature',
        ),
    ]
