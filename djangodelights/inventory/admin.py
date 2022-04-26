from django.contrib import admin
from .models import Basket, Category, Ingredient, MenuItem
from .models import Purchase, Recipe, OrderNumber, Order
from .models import Table, TableOrder

# Register your models here.
admin.site.register(Basket)
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(MenuItem)
admin.site.register(Recipe)
admin.site.register(Purchase)
admin.site.register(Order)
admin.site.register(OrderNumber)
admin.site.register(Table)
admin.site.register(TableOrder)
