# Generated by Django 3.2.9 on 2022-04-19 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0031_alter_shop_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='basket',
            name='delete',
            field=models.BooleanField(default=False),
        ),
    ]
