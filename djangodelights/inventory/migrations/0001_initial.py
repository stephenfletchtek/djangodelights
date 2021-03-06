# Generated by Django 3.2.9 on 2022-01-25 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('quantity', models.IntegerField(blank=True, max_length=10)),
                ('unit', models.CharField(blank=True, max_length=10)),
                ('unit_price', models.DecimalField(blank=True, decimal_places=3, max_digits=6)),
                ('kanban', models.BooleanField(default=False)),
                ('threshold', models.IntegerField(blank=True, max_length=10)),
                ('re_order', models.IntegerField(blank=True, max_length=10)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, unique=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=6)),
                ('made_stock', models.IntegerField(blank=True, max_length=10)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('quantity', models.IntegerField(blank=True, max_length=10)),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.menuitem')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(blank=True, decimal_places=3, max_digits=10)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.ingredient')),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.menuitem')),
            ],
            options={
                'ordering': ['menu_item', 'ingredient'],
                'unique_together': {('menu_item', 'ingredient')},
            },
        ),
    ]
