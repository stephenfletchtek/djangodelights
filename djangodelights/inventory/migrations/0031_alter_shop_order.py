# Generated by Django 3.2.9 on 2022-04-19 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0030_auto_20220419_0847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='order',
            field=models.PositiveIntegerField(),
        ),
    ]
