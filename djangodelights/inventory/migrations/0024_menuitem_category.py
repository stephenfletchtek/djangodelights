# Generated by Django 3.2.9 on 2022-03-04 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_remove_menuitem_made_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='category',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='inventory.category'),
        ),
    ]
