# Generated by Django 3.2.9 on 2022-02-04 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_ingredient_unit_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='re_order',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='threshold',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
