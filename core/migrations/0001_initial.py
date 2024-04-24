# Generated by Django 3.2 on 2021-04-09 19:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_column='name', default='Needs category name', max_length=64)),
                ('description', models.CharField(db_column='descr', max_length=128, null=1)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupName', models.CharField(db_column='grp', max_length=128)),
                ('definition', models.CharField(db_column='def1', max_length=128)),
                ('groupSort', models.SmallIntegerField(blank=1, db_column='grp_srt', null=1)),
            ],
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fileName', models.FileField(db_column='f_name', max_length=128, upload_to='iVault2/media/')),
                ('search_string', models.CharField(db_column='s_string', default='Empty search string.', max_length=256)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('effectDate', models.DateTimeField(default=django.utils.timezone.now, editable=False, null=True)),
                ('categories', models.ManyToManyField(to='core.Category')),
                ('options', models.ManyToManyField(to='core.Option')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
