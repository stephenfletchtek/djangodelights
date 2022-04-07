import math

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    category = models.CharField(unique=True, max_length=200)

    def __str__(self):
        return self.category


class Ingredient(models.Model):
    class Meta:
        ordering = ['name']

    name = models.CharField(unique=True, max_length=200)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    unit = models.CharField(max_length=10)
    unit_price = models.DecimalField(
        blank=True, null=True, max_digits=6, decimal_places=3
    )
    kanban = models.BooleanField(default=False)
    threshold = models.IntegerField(blank=True, null=True)
    re_order = models.IntegerField(blank=True, null=True)

    # Returns reorder quantity if kanban is true and stock is below threshold
    def buy(self):
        if self.kanban and self.quantity < self.threshold:
            return self.re_order
        else:
            return 0

    # return 'True' if it's not in a recipe
    def no_recipe(self):
        recipes = self.recipe_set.all()
        if len(recipes) == 0:
            return True
        else:
            return False

    # returns True if ingredient appears in only one recipe
    # and stock_item for that recipe is False
    def non_stock(self):
        recipes = self.recipe_set.all()
        if len(recipes) == 1 and recipes[0].menu_item.stock_item == False:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('ingredients')

    def __str__(self):
        return f'{self.name}, {self.unit}'


class MenuItem(models.Model):
    class Meta:
        ordering = ['title']

    title = models.CharField(unique=True, max_length=200)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # whether to display the menuitem in user interface
    display = models.BooleanField(default=True)
    # rich description of the dish
    description = models.TextField(blank=True, null=True)
    # whether the dish is stocked or not
    stock_item = models.BooleanField(default=True)

    # Takes a menu_item object
    # Returns how many of the dish can be made from stock
    def available(self):
        try:
            recipe = self.recipe_set.all()
            expression = F('ingredient__quantity') / F('quantity')
            result = math.floor(min(recipe.values_list(expression, flat=True)))
        except:
            result = 0
        return result

    # Adjusts stock of ingredients of menu_item object
    # Delta is an integer: positive increases stock
    def adjust_stock(self, delta):
        delta = delta or 0
        try:
            recipe = self.recipe_set.all()
            for item in recipe:
                pk = item.ingredient.pk
                quantity = F('quantity') + item.quantity * delta
                Ingredient.objects.filter(pk=pk).update(quantity=quantity)
            return True
        except:
            return False

    # Returns cost of ingredients for a particular menu_item
    def dish_cost(self):
        try:
            ingredients = self.recipe_set.all()
            total = Sum(F('ingredient__unit_price') * F('quantity'))
            result = ingredients.aggregate(total=total)['total']
        except:
            result = 0
        return result

    # Returns profit for a particular menu_item (called from template)
    def dish_profit(self):
        try:
            profit = (self.price - self.dish_cost()).quantize(Decimal('0.01'))
        except:
            profit = 0
        return profit

    # overrides kanban boolean in Ingredient model
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # if dish is stocked then set each ingredient kanban to 'True'
        if self.stock_item == True:
            for obj in self.recipe_set.all():
                obj.ingredient.kanban = True
                obj.ingredient.save()
        else:
            for obj in self.recipe_set.all():
                # ingredient is unique in this recipe only
                # set ingredient kanban to 'False' for unique items
                if len(Recipe.objects.filter(ingredient=obj.ingredient)) == 1:
                    obj.ingredient.kanban = False
                    obj.ingredient.save()
        return self

    def get_absolute_url(self):
        return '/menu'

    def __str__(self):
        available = self.available()
        return f'{self.title} -- {available} available'


class Recipe(models.Model):

    class Meta:
        unique_together = ['menu_item', 'ingredient']
        ordering = ['menu_item', 'ingredient']

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)

    def get_absolute_url(self):
        # this gets the currently selected menu item
        return reverse('menu_item_edit', args=[str(self.menu_item.title)])

    def __str__(self):
        return f'{self.ingredient.name} from {self.menu_item.title}'


class Purchase(models.Model):
    class Meta:
        ordering = ['timestamp']

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    def get_absolute_url(self):
        return '/purchases'

    def __str__(self):
        return f'{self.menu_item}'
