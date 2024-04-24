# Generated by Django 3.1 on 2022-02-14 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagBot', '0005_auto_20210610_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagbotmapping',
            name='nomenclature',
            field=models.CharField(db_column='nomenclature', max_length=128),
        ),
        migrations.AlterField(
            model_name='tagbotmapping',
            name='optionIds',
            field=models.CharField(blank=1, db_column='option_ids', default='', max_length=128),
        ),
    ]
