# Generated by Django 3.1 on 2022-02-23 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iv_logger', '0006_ivaultlog_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ivaultlog',
            name='data',
            field=models.CharField(db_column='data', default='Empty log data.', max_length=1500),
        ),
    ]
