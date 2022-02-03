from django.db.models import Sum, F
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import MenuItem, Ingredient, Recipe, Purchase

from .forms import MenuAddForm, MenuEditNameForm, MenuEditPriceForm
from .forms import IngredientAddForm, IngredientEditForm, IngredientStockForm
from .forms import PurchaseAddForm, PurchaseEditForm
from .forms import RecipeAddForm, RecipeEditForm


class HomeView(TemplateView):
  template_name = "inventory/home.html"

  def get_context_data(self):
    context = super().get_context_data()
    context["menu"] = MenuItem.objects.all()
    return context


class IngredientView(ListView):
  model = Ingredient
  template_name = 'inventory/ingredient.html'


class CreateIngredientView(CreateView):
  model = Ingredient
  template_name = 'inventory/add_ingredient.html'
  form_class = IngredientAddForm


class UpdateIngredientView(UpdateView):
  model = Ingredient
  template_name = 'inventory/update_ingredient.html'
  form_class = IngredientEditForm


class IngredientStockView(UpdateView):
    model = Ingredient
    template_name = 'inventory/update_ingredient_stock.html'
    form_class = IngredientStockForm


class DeleteIngredientView(DeleteView):
  model = Ingredient
  template_name = 'inventory/delete_ingredient.html'
  success_url = '/ingredients'


class InvetoryView(ListView):
    model = Ingredient
    template_name = 'inventory/inventory.html'

    # ingredients in stock
    def get_queryset(self):
        return Ingredient.objects.filter(quantity__gt=0)


class MenuView(ListView):
  model = MenuItem
  template_name = 'inventory/menu.html'


class CreateMenuView(CreateView):
  model = MenuItem
  template_name = 'inventory/add_menu.html'
  form_class = MenuAddForm


class UpdateMenuNameView(UpdateView):
  model = MenuItem
  template_name = 'inventory/update_menu_name.html'
  form_class = MenuEditNameForm


class UpdateMenuPriceView(UpdateView):
  model = MenuItem
  template_name = 'inventory/update_menu_price.html'
  form_class = MenuEditPriceForm


class DeleteMenuView(DeleteView):
  model = MenuItem
  template_name = 'inventory/delete_menu.html'
  success_url = '/menu'


class PurchaseView(ListView):
  model = Purchase
  template_name = 'inventory/purchase.html'


class CreatePurchaseView(CreateView):
    model = Purchase
    template_name = 'inventory/add_purchase.html'
    form_class = PurchaseAddForm

    def form_valid(self, form):
        # decrease stock when purchase is added
        order_quantity = form.instance.quantity
        menu_item = form.instance.menu_item
        recipe = menu_item.recipe_set.filter(menu_item=menu_item)

        for recipe_obj in recipe:
            pk = recipe_obj.ingredient.pk
            quantity = F('quantity') - recipe_obj.quantity * order_quantity
            Ingredient.objects.filter(pk=pk).update(quantity=quantity)

        return super().form_valid(form)


class UpdatePurchaseView(UpdateView):
    model = Purchase
    template_name = 'inventory/update_purchase.html'
    form_class = PurchaseEditForm

    def form_valid(self, form):
        # adjust stock up or down by difference between form and model
        order = self.get_object()
        recipe = order.menu_item.recipe_set.filter(menu_item=order.menu_item)
        delta = order.quantity - form.instance.quantity

        for recipe_obj in recipe:
            pk = recipe_obj.ingredient.pk
            quantity = F('quantity') + recipe_obj.quantity * delta
            Ingredient.objects.filter(pk=pk).update(quantity=quantity)

        return super().form_valid(form)


class DeletePurchaseView(DeleteView):
    model = Purchase
    template_name = 'inventory/delete_purchase.html'
    success_url = '/purchases'

    def delete(self, *args, **kwargs):
        # increase stock if purchase is deleted
        order = self.get_object()
        recipe = order.menu_item.recipe_set.filter(menu_item=order.menu_item)

        for recipe_obj in recipe:
            pk = recipe_obj.ingredient.pk
            quantity = F('quantity') + recipe_obj.quantity * order.quantity
            Ingredient.objects.filter(pk=pk).update(quantity=quantity)

        return super().delete(*args, **kwargs)


class RecipeView(ListView):
    model = Recipe
    template_name = 'inventory/recipe.html'

    def get_queryset(self):
        self.menu_item = get_object_or_404(MenuItem, title=self.kwargs['recipe'])
        return Recipe.objects.filter(menu_item__title=self.menu_item)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu_recipe'] = self.menu_item
        return context


class CreateRecipeView(CreateView):
    model = Recipe
    template_name = 'inventory/add_recipe.html'
    form_class = RecipeAddForm

    # add menu_item after valid form is posted
    # this would overwrite form if field was exposed
    def form_valid(self, form):
        title=self.kwargs['recipe']
        menu_item = get_object_or_404(MenuItem, title=title)
        form.instance.menu_item = menu_item
        return super().form_valid(form)

    # put recipe into form kwargs
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'recipe': self.kwargs['recipe']})
        return kwargs

    # put recipe into context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe'] = self.kwargs['recipe']
        return context

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()


class UpdateRecipeView(UpdateView):
    model = Recipe
    template_name = 'inventory/update_recipe.html'
    form_class = RecipeEditForm


class DeleteRecipeView(DeleteView):
    model = Recipe
    template_name = 'inventory/delete_recipe.html'

    def get_success_url(self, **kwargs):
        return self.object.get_absolute_url()


class ReportView(ListView):
    model = Purchase
    template_name = 'inventory/report.html'

    def get_queryset(self):
        # messy way to get cost of all orders
        self.orders_cost = 0

        # menu items actually purchased
        purchases = Purchase.objects.order_by()
        purchases = purchases.values_list('menu_item__title', flat=True)
        purchases = purchases.distinct()

        for item in purchases:
            # number of orders
            orders = Purchase.objects.filter(menu_item__title=item)
            orders = orders.aggregate(total=Sum('quantity'))['total']
            # dish cost
            dish_cost = Recipe.objects.filter(menu_item__title=item)
            total = Sum(F('ingredient__unit_price') * F('quantity'))
            dish_cost = dish_cost.aggregate(total=total)['total']

            self.orders_cost += orders * dish_cost

        revenue = Purchase.objects.all()
        total = Sum(F('menu_item__price') * F('quantity'))
        revenue = revenue.aggregate(total=total)['total']
        self.profit = revenue - self.orders_cost
        return revenue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.orders_cost
        context['profit'] = self.profit
        return context
