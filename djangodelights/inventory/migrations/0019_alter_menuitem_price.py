# Generated by Django 3.2.9 on 2022-02-07 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_alter_menuitem_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]