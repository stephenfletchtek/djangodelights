from decimal import Decimal

from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from .forms import MenuAddForm
from .forms import UpdateMenuDescriptionForm, MenuSelectForm
from .forms import IngredientAddForm, IngredientEditForm
from .forms import AddForm, BasketAddForm, BasketUpdateForm, EditBasketFormset
from .forms import PurchaseAddForm, PurchaseEditForm
from .forms import RecipeAddForm
from .forms import UpdateMenuFormSet, UpdateStockFormset
from .forms import CreateOrderForm, UpdateMenuDetailsFormSet
from .models import Basket, MenuItem, Ingredient, Recipe, Purchase, OrderNumber, Order


class SignUp(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("home")


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/home.html"

    def get_context_data(self):
        context = super().get_context_data()
        context["menu"] = MenuItem.objects.all()
        return context


class IngredientView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = 'inventory/ingredient.html'


class CreateIngredientView(LoginRequiredMixin, CreateView):
    model = Ingredient
    template_name = 'inventory/add_ingredient.html'
    form_class = IngredientAddForm


class UpdateIngredientView(LoginRequiredMixin, UpdateView):
    model = Ingredient
    template_name = 'inventory/update_ingredient.html'
    form_class = IngredientEditForm

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        name = self.kwargs['name']
        ingredient = get_object_or_404(Ingredient, name=name)
        return ingredient


class DeleteIngredientView(LoginRequiredMixin, DeleteView):
    model = Ingredient
    template_name = 'inventory/delete_ingredient.html'
    success_url = '/stock/ingredients/'

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        name = self.kwargs['name']
        ingredient = get_object_or_404(Ingredient, name=name)
        return ingredient


class MenuView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'inventory/menu.html'
    form_class = MenuSelectForm


class CreateMenuView(LoginRequiredMixin, CreateView):
    model = MenuItem
    template_name = 'inventory/add_menu.html'
    form_class = MenuAddForm
    success_url = '/menu/displayupdate/'


class UpdateMenuView(LoginRequiredMixin, FormView):
    model = MenuItem
    template_name = 'inventory/update_menu.html'
    form_class = UpdateMenuFormSet

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse('menu')


class UpdateMenuDescriptionView(LoginRequiredMixin, UpdateView):
    model = MenuItem
    template_name = 'inventory/update_menu_description.html'
    form_class = UpdateMenuDescriptionForm

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        title = self.kwargs['menu_item']
        menu_item = get_object_or_404(MenuItem, title=title)
        return menu_item

    # kwarg in success_url
    def get_success_url(self, **kwargs):
        menu_item = self.kwargs['menu_item']
        return reverse('menu_item_edit', kwargs={'menu_item': menu_item})


# formset menu_item details
class UpdateMenuDetailsView(LoginRequiredMixin, FormView):
    model = Recipe
    template_name = 'inventory/edit_menu_details.html'
    form_class = UpdateMenuDetailsFormSet

    # have to do this when using formset
    def form_valid(self, form):
        form.save(commit=False)
        for obj in form.deleted_objects:
            obj.delete()
        form.save()
        return super().form_valid(form)

    # put menu_item into context
    def get_context_data(self, **kwargs):
        title = self.kwargs['menu_item']
        menu_item = get_object_or_404(MenuItem, title=title)
        context = super().get_context_data(**kwargs)
        context['menu_item'] = menu_item
        return context

    # put menu_item object into form kwargs
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'menu_item': self.get_object()})
        return kwargs

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        title = self.kwargs['menu_item']
        menu_item = get_object_or_404(MenuItem, title=title)
        return menu_item

    def get_success_url(self, **kwargs):
        menu_item = self.kwargs['menu_item']
        return reverse('details', kwargs={'menu_item': menu_item})


class DeleteMenuView(LoginRequiredMixin, DeleteView):
    model = MenuItem
    template_name = 'inventory/delete_menu.html'
    success_url = '/menu'

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        title = self.kwargs['menu_item']
        menu_item = get_object_or_404(MenuItem, title=title)
        return menu_item


# *** BASKET STUFF ***
# view basket
class BasketView(LoginRequiredMixin, ListView):
    model = Basket
    template_name = 'inventory/basket.html'


# add any ingredient
class AddBasketView(LoginRequiredMixin, CreateView):
    model = Basket
    template_name = 'inventory/add_basket.html'
    form_class = AddForm

    # horrible hack for create_or_update
    def form_valid(self, form):
        ingredient = form.instance.ingredient
        quantity = form.instance.quantity
        if ingredient.in_basket():
            # amend quantity
            basket_obj = get_object_or_404(Basket, ingredient=ingredient)
            basket_obj.change_quantity(quantity)
            return HttpResponseRedirect(reverse('basket_view'))
        else:
            # add ingredient
            return super().form_valid(form)


# add item from restock list
class CreateBasketView(LoginRequiredMixin, CreateView):
    model = Basket
    template_name = 'inventory/add_basket.html'
    form_class = BasketAddForm
    success_url = '/stock/shoppinglist/'

    # add ingredient after valid form is posted
    # this would overwrite form if field was exposed
    def form_valid(self, form):
        form.instance.ingredient = self.get_object()
        return super().form_valid(form)

    # put ingredient into context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredient'] = self.kwargs['ingredient']
        return context

    # put ingredient object into form kwargs
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'ingredient_obj': self.get_object()})
        return kwargs

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        name = self.kwargs['ingredient']
        ingredient = get_object_or_404(Ingredient, name=name)
        return ingredient


# add in item from restock list
class UpdateBasketView(LoginRequiredMixin, UpdateView):
    model = Basket
    template_name = 'inventory/update_basket.html'
    form_class = BasketUpdateForm
    success_url = '/stock/shoppinglist/'

    # override form to add quantity to amount already in basket
    def form_valid(self, form):
        in_basket = self.get_object().quantity
        form.instance.quantity += in_basket
        return super().form_valid(form)

    # put ingredient into context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredient'] = self.kwargs['ingredient']
        return context

    # put basket object into form kwargs
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'basket_obj': self.get_object()})
        return kwargs

    # overriding get_object() means no need to slug_the_url_conf
    def get_object(self, queryset=None):
        name = self.kwargs['ingredient']
        basket = get_object_or_404(Basket, ingredient__name=name)
        return basket


# Edit the basket
class EditBasketView(LoginRequiredMixin, FormView):
    model = Basket
    template_name = 'inventory/edit_basket.html'
    form_class = EditBasketFormset
    success_url = '/stock/basket/'

    def form_valid(self, form):
        # cannot commit form to database if about to delete
        form.save(commit=False)
        for obj in form.deleted_objects:
            obj.delete()
        form.save()
        return super().form_valid(form)


# view orders
class OrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'inventory/orders.html'


# creates an order_number and then flushes basket into orders
class CreateOrderView(LoginRequiredMixin, CreateView):
    model = OrderNumber
    template_name = 'inventory/add_order.html'
    form_class = CreateOrderForm


class PurchaseView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'inventory/purchase.html'


class CreatePurchaseView(LoginRequiredMixin, CreateView):
    model = Purchase
    template_name = 'inventory/add_purchase.html'
    form_class = PurchaseAddForm

    # decrease stock when purchase is added
    def form_valid(self, form):
        menu_item = form.instance.menu_item
        delta = -form.instance.quantity
        success = menu_item.adjust_stock(delta)
        return super().form_valid(form)


class UpdatePurchaseView(LoginRequiredMixin, UpdateView):
    model = Purchase
    template_name = 'inventory/update_purchase.html'
    form_class = PurchaseEditForm

    # adjust stock up or down by difference between form and model
    def form_valid(self, form):
        order = self.get_object()
        menu_item = order.menu_item
        delta = order.quantity - form.instance.quantity
        menu_item.adjust_stock(delta)
        return super().form_valid(form)


class DeletePurchaseView(LoginRequiredMixin, DeleteView):
    model = Purchase
    template_name = 'inventory/delete_purchase.html'
    success_url = '/purchases'

    # increase stock if purchase is deleted
    # *** THIS CANNOT WORK IF MENU_ITEM IS DELETED!!! ***
    def delete(self, *args, **kwargs):
        order = self.get_object()
        menu_item = order.menu_item
        delta = order.quantity
        if self.restock:
            menu_item.adjust_stock(delta)
        return super().delete(*args, **kwargs)

    # grab restock checkbox from form
    def post(self, request, *args, **kwargs):
        self.restock = request.POST.get('restock')
        self.delete(self)
        return HttpResponseRedirect(self.success_url)


class MenuDetailsView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = "inventory/details.html"

    def get_queryset(self):
        title = self.kwargs['menu_item']
        return Recipe.objects.filter(menu_item__title=title)

    def get_context_data(self, **kwargs):
        title = self.kwargs['menu_item']
        context = super().get_context_data(**kwargs)
        context['menu_item'] = get_object_or_404(MenuItem, title=title)
        return context


class CreateRecipeView(LoginRequiredMixin, CreateView):
    model = Recipe
    template_name = 'inventory/add_recipe.html'
    form_class = RecipeAddForm

    # add menu_item after valid form is posted
    # this would overwrite form if field was exposed
    def form_valid(self, form):
        title=self.kwargs['menu_item']
        menu_item = get_object_or_404(MenuItem, title=title)
        form.instance.menu_item = menu_item
        return super().form_valid(form)

    # put menu_item into form kwargs
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'menu_item': self.kwargs['menu_item']})
        return kwargs

    # put menu_item into context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_item'] = self.kwargs['menu_item']
        return context


class SalesProfitView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/sales_profit.html"


class ReportView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'inventory/report.html'

    def get_queryset(self):
        try:
            purchases = Purchase.objects.all()
            # revenue
            total = Sum(F('menu_item__price') * F('quantity'))
            revenue = purchases.aggregate(total=total)['total']
            # costs
            orders = [
                obj.quantity * obj.menu_item.dish_cost() for obj in purchases
            ]
            self.orders_cost = sum(orders)
            # profit
            self.profit = revenue - self.orders_cost
            # format for display
            revenue = revenue.quantize(Decimal('0.01'))
            self.orders_cost = self.orders_cost.quantize(Decimal('0.01'))
            self.profit = self.profit.quantize(Decimal('0.01'))
        except:
            revenue = Decimal(0).quantize(Decimal('0.01'))
            self.orders_cost = Decimal(0).quantize(Decimal('0.01'))
            self.profit = Decimal(0).quantize(Decimal('0.01'))

        return revenue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.orders_cost
        context['profit'] = self.profit
        return context


class BestSellerView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'inventory/best_sellers.html'

    def get_queryset(self):
        # dict comprehension of menu_item__title and aggregated quantity
        field = 'menu_item__title'
        titles = Purchase.objects.order_by().values(field).distinct()
        total = Sum(F('quantity'))
        result = {
            key[field]: Purchase.objects.filter(menu_item__title=key[field])
            .aggregate(total=total)['total'] for key in titles
        }

        # find menu_item with highest quantity and return it
        best_seller = max(result, key=lambda key:result[key])
        return {best_seller: result[best_seller]}


class StockView(LoginRequiredMixin, TemplateView):
    template_name = "inventory/stock.html"


class CurrentStockView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = 'inventory/current_stock.html'

    # ingredients in stock
    def get_queryset(self):
        return Ingredient.objects.filter(quantity__gt=0)


class UpdateStockView(LoginRequiredMixin, FormView):
    model = Ingredient
    template_name = 'inventory/update_stock.html'
    form_class = UpdateStockFormset
    success_url = '/stock/currentstock/'

    # have to to this with formset
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class StockedRecipes(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = "inventory/stocked_recipes.html"

    def get_queryset(self):
        menu = MenuItem.objects.all()
        stocked = [obj for obj in menu if obj.stock_item]
        return stocked


class ShoppingList(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = "inventory/shopping_list.html"

    def get_queryset(self):
        ingredients = Ingredient.objects.all()
        self.shopping_list = [obj for obj in ingredients if obj.buy()]
        return self.shopping_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['basket'] = Basket.objects.all()
        return context


class OrphanIngredientView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = "inventory/orphans.html"

    def get_queryset(self):
        ingredients = Ingredient.objects.all()
        self.no_recipe = [obj for obj in ingredients if obj.no_recipe()]
        non_stock = [obj for obj in ingredients if obj.non_stock()]
        return non_stock

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['no_recipe'] = self.no_recipe
        return context
