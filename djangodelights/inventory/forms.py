from django import forms, template

from django.core.exceptions import ValidationError

from .models import Ingredient, MenuItem, Recipe, Purchase


# used to add
class IngredientAddForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientEditForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        exclude = ['quantity']


class IngredientStockForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['quantity']


# used to add menu item
class MenuAddForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["title", "price"]


# used to uodate menu name
class MenuEditNameForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["title"]


# used to add menu item
class MenuEditPriceForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["price"]


# used to add purchase item
class PurchaseAddForm(forms.ModelForm):
    class Meta:
        model = Purchase
        exclude = ["timestamp"]

    # only list dishes available to purchase
    def __init__(self, **kwargs):
        self.menu = MenuItem.objects.all()
        super().__init__(**kwargs)
        menu = MenuItem.objects.all()
        filter_list = [item.title for item in menu if item.available(item) > 0]
        in_stock = MenuItem.objects.filter(title__in=filter_list)
        self.fields['menu_item'].queryset = in_stock

    # cleaned quantity must not be > available
    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        menu_item = self.cleaned_data['menu_item']
        available = menu_item.available(menu_item)

        if data > available:
            message = f'Only {available} of these are available'
            raise ValidationError(message)
            data = 0
        return data


# used to update purchase item
class PurchaseEditForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ["quantity"]

    # cleaned quantity must not be > available
    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        menu_item = self.instance.menu_item
        available = menu_item.available(menu_item)
        orig_qty = self.instance.quantity
        delta = data - orig_qty
        if delta > available:
            message = f'Current order {orig_qty} and {available} more available'
            raise ValidationError(message)
            data = orig_qty
        return data


# used to add recipe ingredient
class RecipeAddForm(forms.ModelForm):
    class Meta:
        model = Recipe
        exclude = ['menu_item']

    # only list ingredients not already in the recipe
    def __init__(self, menu_item=None, **kwargs):
        in_recipe = Recipe.objects.filter(menu_item__title=menu_item)
        excludes = in_recipe.values_list('ingredient__name', flat=True)
        ingredients = Ingredient.objects.exclude(name__in=excludes)
        super().__init__(**kwargs)
        self.fields['ingredient'].queryset = ingredients


# used to update recipe ingredient
class RecipeEditForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["quantity"]
