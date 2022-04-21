from django import forms, template

from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, BaseModelFormSet

from .models import Basket, Ingredient, MenuItem, Recipe, Purchase, OrderNumber, Order


# Add any item to basket
class AddForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = '__all__'


# Add item from restock list to basket
class BasketAddForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ['quantity']

    def __init__(self, ingredient_obj=None, **kwargs):
        super().__init__(**kwargs)
        self.initial['quantity'] = ingredient_obj.re_order


# Add in item from restock list to basket as an update
class BasketUpdateForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ['quantity']

    def __init__(self, basket_obj=None, **kwargs):
        super().__init__(**kwargs)
        self.initial['quantity'] = basket_obj.ingredient.re_order


# Edit basket
EditBasketFormset = modelformset_factory(
    Basket, fields=('quantity',), can_delete=True, extra=0
)


# create order
class CreateOrderForm(forms.ModelForm):
    class Meta:
        model = OrderNumber
        fields = "__all__"


# used to add
class IngredientAddForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientEditForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            'name', 'unit', 'unit_price', 'kanban', 'threshold', 're_order'
        ]


class MenuSelectForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['display']

    # makes it auto validate on tick box
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['display'].widget.attrs.update({'onchange': 'submit();'})


DisplayFormset = modelformset_factory(MenuItem, fields=('stock_item','display',), extra=0)


# only display 'in stock' ingredients in formset
class BaseStockFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Ingredient.objects.filter(quantity__gt=0)


UpdateStockFormset = modelformset_factory(Ingredient, fields=('quantity',), formset=BaseStockFormSet, extra=0)


# used to add menu item
class MenuAddForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'


# used to update description
class MenuEditDescription(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["description"]


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
        filter_list = [item.title for item in menu if item.available() > 0]
        in_stock = MenuItem.objects.filter(title__in=filter_list)
        self.fields['menu_item'].queryset = in_stock

    # cleaned quantity must not be > available
    def clean_quantity(self):
        data = self.cleaned_data['quantity']
        menu_item = self.cleaned_data['menu_item']
        available = menu_item.available()

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
        available = menu_item.available()
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
