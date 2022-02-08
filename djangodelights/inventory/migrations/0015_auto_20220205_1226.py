# Generated by Django 3.2.9 on 2022-02-05 12:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_alter_purchase_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='quantity',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='quantity',
            field=models.DecimalField(decimal_places=3, default=1, max_digits=10),
        ),
    ]
