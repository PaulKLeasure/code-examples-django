# Generated by Django 3.1 on 2023-03-08 03:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0012_auto_20230116_2332'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(db_column='name', max_length=128)),
                ('mach_name', models.CharField(db_column='mach_name', max_length=128)),
                ('LocationPath', models.CharField(db_column='loc_path', max_length=256)),
                ('Description', models.CharField(blank=True, db_column='descr', max_length=128, null=True)),
                ('Sort', models.SmallIntegerField(db_column='sort', default=0)),
                ('Enabled', models.BooleanField(db_column='enabled', default=True)),
            ],
        ),
        migrations.CreateModel(
            name='FilterGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(db_column='name', max_length=128)),
                ('Description', models.CharField(blank=True, db_column='descr', max_length=128, null=True)),
                ('Sort', models.SmallIntegerField(db_column='sort', default=0)),
                ('selectionElement', models.CharField(default='checkbox', max_length=32)),
                ('parentFilter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assetFilterAdmin.filter')),
            ],
        ),
        migrations.CreateModel(
            name='FilterGroupItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Name', models.CharField(db_column='name', max_length=128)),
                ('Description', models.CharField(blank=True, db_column='descr', max_length=128, null=True)),
                ('Sort', models.SmallIntegerField(db_column='sort', default=0)),
                ('coreOption', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.option')),
                ('parentGroup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='assetFilterAdmin.filtergroup')),
            ],
        ),
    ]
