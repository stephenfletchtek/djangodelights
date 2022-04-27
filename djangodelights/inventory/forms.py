from django import forms, template

from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, BaseModelFormSet

from .models import Basket, Ingredient, MenuItem, Recipe, Purchase, OrderNumber, Order
from .models import TableOrder

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
        self.initial['quantity'] = ingredient_obj.buy()


# Add in item from restock list to basket as an update
class BasketUpdateForm(forms.ModelForm):
    class Meta:
        model = Basket
        fields = ['quantity']

    def __init__(self, basket_obj=None, **kwargs):
        super().__init__(**kwargs)
        self.initial['quantity'] = basket_obj.ingredient.buy()


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


# class MenuSelectForm(forms.ModelForm):
#     class Meta:
#         model = MenuItem
#         fields = ['display']
#
#     # makes it auto validate on tick box
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['display'].widget.attrs.update({'onchange': 'submit();'})


UpdateMenuFormSet = modelformset_factory(
    MenuItem,
    fields=('title', 'price', 'stock_item','display',),
    extra=0,
    # widgets={'display': forms.CheckboxInput(attrs={'onchange': 'submit();'})}
)


# only display 'in stock' ingredients in formset
class BaseStockFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Ingredient.objects.filter(quantity__gt=0)


UpdateStockFormset = modelformset_factory(
    Ingredient,
    fields=('quantity',),
    formset=BaseStockFormSet,
    extra=0
)


# used to add menu item
class MenuAddForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'


# display recipe items linked to menu_item
class BaseMenuDetailsFormSet(BaseModelFormSet):
    def __init__(self, menu_item=None, **kwargs):
        super().__init__(**kwargs)
        self.queryset = Recipe.objects.filter(menu_item=menu_item)


# update recipe item quantities or delete
UpdateMenuDetailsFormSet = modelformset_factory(
    Recipe,
    fields=('quantity',),
    formset=BaseMenuDetailsFormSet,
    can_delete=True,
    extra=0
)


# update menu_item details
class UpdateMenuDescriptionForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["description"]


############################################
# Add and update menu_items on table_order #
############################################
# used to add purchase item
class PurchaseAddForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['menu_item', 'quantity']

    # only list dishes available to purchase
    def __init__(self, table_order=None, **kwargs):
        # exclude objects already on the order
        purchase = Purchase.objects.filter(table_order__id=table_order)
        excl_list = [item.menu_item.id for item in purchase]
        menu = MenuItem.objects.exclude(id__in=excl_list)
        # list items in stock
        filter_list = [item.id for item in menu if item.available() > 0]
        in_stock = MenuItem.objects.filter(id__in=filter_list)
        super().__init__(**kwargs)
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


###########################
# Adding a customer order #
###########################
class TableOrderAddForm(forms.ModelForm):
    class Meta:
        model = TableOrder
        fields = ['timestamp', 'table']
