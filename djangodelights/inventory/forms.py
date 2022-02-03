from django import forms, template

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
        # hide timestamp as it defaults to 'now'
        fields = ["menu_item", "quantity"]

# used to update purchase item
class PurchaseEditForm(forms.ModelForm):
    class Meta:
        model = Purchase
        # hide timestamp as it defaults to 'now'
        fields = ["quantity"]


# used to add recipe ingredient
class RecipeAddForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["ingredient", "quantity"]

    def __init__(self, recipe=None, **kwargs):
        # only list ingredients not already in the recipe
        in_recipe = Recipe.objects.filter(menu_item__title=recipe)
        excludes = in_recipe.values_list('ingredient__name', flat=True)
        ingredients = Ingredient.objects.exclude(name__in=excludes)
        super().__init__(**kwargs)
        self.fields['ingredient'].queryset = ingredients


# used to update recipe ingredient
class RecipeEditForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ["quantity"]
