from decimal import Decimal

from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
# from django.views.generic.edit import FormMixin

from .forms import MenuAddForm, MenuEditNameForm, MenuEditPriceForm
from .forms import MenuSelectForm, DisplayFormset
from .forms import IngredientAddForm, IngredientEditForm, IngredientStockForm
from .forms import PurchaseAddForm, PurchaseEditForm
from .forms import RecipeAddForm, RecipeEditForm
from .models import MenuItem, Ingredient, Recipe, Purchase


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


class IngredientStockView(LoginRequiredMixin, UpdateView):
    model = Ingredient
    template_name = 'inventory/update_ingredient_stock.html'
    form_class = IngredientStockForm


class DeleteIngredientView(LoginRequiredMixin, DeleteView):
  model = Ingredient
  template_name = 'inventory/delete_ingredient.html'
  success_url = '/ingredients'


class InventoryView(LoginRequiredMixin, ListView):
    model = Ingredient
    template_name = 'inventory/inventory.html'

    # ingredients in stock
    def get_queryset(self):
        return Ingredient.objects.filter(quantity__gt=0)


class MenuView(LoginRequiredMixin, ListView):
    model = MenuItem
    template_name = 'inventory/menu.html'
    form_class = MenuSelectForm


class CreateMenuView(LoginRequiredMixin, CreateView):
  model = MenuItem
  template_name = 'inventory/add_menu.html'


class UpdateMenuDisplayView(LoginRequiredMixin, FormView):
    model = MenuItem
    template_name = 'inventory/update_menu_display.html'
    form_class = DisplayFormset
    success_url = '/menu'

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.success_url)


class UpdateMenuNameView(LoginRequiredMixin, UpdateView):
  model = MenuItem
  template_name = 'inventory/update_menu_name.html'
  form_class = MenuEditNameForm


class UpdateMenuPriceView(LoginRequiredMixin, UpdateView):
  model = MenuItem
  template_name = 'inventory/update_menu_price.html'
  form_class = MenuEditPriceForm


class DeleteMenuView(LoginRequiredMixin, DeleteView):
  model = MenuItem
  template_name = 'inventory/delete_menu.html'
  success_url = '/menu'


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


class Details(LoginRequiredMixin, ListView):
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


class RecipeView(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'inventory/recipe.html'

    def get_queryset(self):
        title = self.kwargs['menu_item']
        self.menu_item = get_object_or_404(MenuItem, title=title)
        return Recipe.objects.filter(menu_item__title=title)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_item'] = self.menu_item
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

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()


class UpdateRecipeView(LoginRequiredMixin, UpdateView):
    model = Recipe
    template_name = 'inventory/update_recipe.html'
    form_class = RecipeEditForm


# Delete recipe will cause associated orders to delete
# But it won't increment stock
class DeleteRecipeView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = 'inventory/delete_recipe.html'

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()


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
                item.quantity * item.menu_item.dish_cost()
                for item in purchases
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
