# Generated by Django 3.1 on 2022-12-30 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assetFilterAdmin', '0003_auto_20221230_1732'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='filter',
            name='filterGroups',
        ),
        migrations.RemoveField(
            model_name='filtergroup',
            name='filterGroupItems',
        ),
    ]
