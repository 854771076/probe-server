# Generated by Django 3.2.5 on 2024-02-27 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='genderCode',
            field=models.IntegerField(default=1, null=True, verbose_name='性别id 男 1 女 0'),
        ),
        migrations.AlterField(
            model_name='user',
            name='points',
            field=models.IntegerField(default=0, null=True, verbose_name='积分'),
        ),
    ]
