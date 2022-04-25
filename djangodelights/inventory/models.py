import math

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.urls import reverse


class Category(models.Model):
    category = models.CharField(unique=True, max_length=200)

    def __str__(self):
        return f'{self.id} -- {self.category}'


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

    # Returns reorder quantity less basket quantity
    # if kanban is true and stock is below threshold
    def buy(self):
        if self.kanban and self.quantity < self.threshold:
            return self.re_order - self.in_basket()
        else:
            return 0

    # return basket quantity if item is in the basket else zero
    def in_basket(self):
        ingredients = [obj.ingredient for obj in Basket.objects.all()]
        if self in ingredients:
            basket = get_object_or_404(Basket, ingredient=self)
            return basket.quantity
        else:
            return 0

    # return 'True' if it's not in a recipe
    def no_recipe(self):
        recipes = self.recipe_set.all()
        if len(recipes) == 0:
            return True
        else:
            return False

    # return 'True' if ingredient appears in only one recipe
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

    # Returns how many of the menu_item can be made from stock
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

    # overrides ingredient.kanban according to menu_item.stock_item status
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # if dish is stocked then set each ingredient kanban to 'True'
        if self.stock_item == True:
            for obj in self.recipe_set.all():
                obj.ingredient.kanban = True
                obj.ingredient.save()
        else:
            for obj in self.recipe_set.all():
                # if ingredient is unique in this recipe only
                # set ingredient kanban to 'False' for unique items
                if len(Recipe.objects.filter(ingredient=obj.ingredient)) == 1:
                    obj.ingredient.kanban = False
                    obj.ingredient.save()
        return self

    def get_absolute_url(self):
        return reverse('menu')

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
        # currently selected menu item
        return reverse('menu_item_edit', args=[str(self.menu_item.title)])

    def __str__(self):
        return f'{self.ingredient.name} from {self.menu_item.title}'


# used to store customer purchases from the menu
class Purchase(models.Model):
    class Meta:
        ordering = ['-timestamp']

    menu_item = models.ForeignKey(
        MenuItem,
        models.SET_NULL,
        blank=True,
        null=True
    )
    menu_item_name = models.CharField(blank=True, max_length=200)
    timestamp = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    def get_absolute_url(self):
        return reverse('purchases')

    # clone title from menu_item object into CharField
    def save(self, **kwargs):
        self.menu_item_name = self.menu_item.title
        super().save(**kwargs)

    def __str__(self):
        return f'{self.id}: {self.menu_item_name}'


# use this model to hold the shopping basket
class Basket(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    # Adjusts quantity of basket object
    # Delta is an integer: positive for increase
    def change_quantity(self, delta):
        try:
            self.quantity += delta
            self.save()
            return True
        except:
            return False

    def get_absolute_url(self):
        return reverse('basket_view')

    def __str__(self):
        return f'{self.ingredient}'

###############################################################################
# OrderNumber and Order is clumsy approach where many-to-many for ingredients #
# in a single order would be better. But it works OK as a fisrt go!           #
###############################################################################

# create a unique order number(id) and timestamp for use with Orders
class OrderNumber(models.Model):
    class Meta:
        ordering = ['-id']

    timestamp = models.DateTimeField(default=timezone.now)

    # perform actions when model is saved (when an order is created)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # move contents of basket over into a new order
        # and increment stock of items ordered
        order_number = OrderNumber.objects.latest('id')
        basket = Basket.objects.all()
        for item in basket:
            # copy basket contents into Order
            Order.objects.create(
                order_number=order_number,
                ingredient_name=item.ingredient.name,
                quantity=item.quantity
            )
            # increment stock
            item.ingredient.quantity += item.quantity
            item.ingredient.save()
            # remove from basket
            item.delete()

    def get_absolute_url(self):
        return reverse('shopping_list')

    def __str__(self):
        return f'{self.id} -- {self.timestamp}'


# use ths model to store shopping lists after 'purchase'
class Order(models.Model):
    class Meta:
        ordering = ['order_number']

    order_number = models.ForeignKey(OrderNumber, on_delete=models.CASCADE)
    ingredient_name = models.CharField(blank=True, max_length=200)
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    def get_absolute_url(self):
        return reverse('shopping_list')

    def __str__(self):
        return f'{self.id} -- {self.ingredient_name}'
