# Generated by Django 3.2.5 on 2024-03-01 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20240228_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='逻辑删除'),
        ),
        migrations.AddField(
            model_name='clickitems',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='逻辑删除'),
        ),
        migrations.AddField(
            model_name='commentitems',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='逻辑删除'),
        ),
        migrations.AddField(
            model_name='commentitems',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='最后修改时间'),
        ),
        migrations.AddField(
            model_name='logs',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='逻辑删除'),
        ),
        migrations.AddField(
            model_name='staritems',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='逻辑删除'),
        ),
        migrations.AddField(
            model_name='staritems',
            name='last_update',
            field=models.DateTimeField(auto_now=True, verbose_name='最后修改时间'),
        ),
    ]
