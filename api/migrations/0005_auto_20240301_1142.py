# Generated by Django 3.2.5 on 2024-03-01 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20240301_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clickitems',
            name='item_id',
            field=models.CharField(max_length=255, unique=True, verbose_name='物品id'),
        ),
        migrations.AlterField(
            model_name='staritems',
            name='item_id',
            field=models.CharField(max_length=255, unique=True, verbose_name='物品id'),
        ),
    ]
