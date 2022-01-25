from django.db import models


class Ingredient(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(unique=True, max_length=200)
    quantity = models.IntegerField(unique=False, blank=True, max_length=10)
    unit = models.CharField(unique=False, blank=True, max_length=10)
    unit_price = models.DecimalField(unique=False, blank=True, max_digits=6, decimal_places=3)
    kanban = models.BooleanField(default=False)
    threshold = models.IntegerField(unique=False, blank=True, max_length=10)
    re_order = models.IntegerField(unique=False, blank=True, max_length=10)

    def get_absolute_url(self):
        return '/ingredients'

    def __str__(self):
        return f'{self.name}, {self.unit}'


class MenuItem(models.Model):
    class Meta:
        ordering = ['title']

    title = models.CharField(unique=True, max_length=200)
    price = models.DecimalField(unique=False, blank=True, max_digits=6, decimal_places=2)
    made_stock = models.IntegerField(unique=False, blank=True, max_length=10)

    def get_absolute_url(self):
        return '/menu'

    def __str__(self):
        return f'{self.title}'


class Recipe(models.Model):
    class Meta:
        unique_together = ['menu_item', 'ingredient']
        ordering = ['menu_item', 'ingredient']

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(unique=False, blank=True, max_digits=10, decimal_places=3)

    def get_absolute_url(self):
        return '/recipe'

    def __str__(self):
        return f'{self.menu_item} -- {self.ingredient}'


class Purchase(models.Model):
    class Meta:
        ordering = ['timestamp']

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(unique=False)
    quantity = models.IntegerField(unique=False, blank=True, max_length=10)

    def get_absolute_url(self):
        return '/purchase'

    def __str__(self):
        return f'{self.menu_item}'
