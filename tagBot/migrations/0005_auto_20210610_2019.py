# Generated by Django 3.1.7 on 2021-06-10 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagBot', '0004_auto_20210610_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagbotmapping',
            name='nomenclature',
            field=models.CharField(db_column='nomenclature', max_length=16),
        ),
    ]
