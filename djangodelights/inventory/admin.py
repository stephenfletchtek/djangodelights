from django.contrib import admin
from .models import Category, Ingredient, MenuItem, Recipe, Purchase

# Register your models here.
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(MenuItem)
admin.site.register(Recipe)
admin.site.register(Purchase)
