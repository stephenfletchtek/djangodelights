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
    context["ingredients"] = Ingredient.objects.all()
    context["recipes"] = Recipe.objects.all()
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


class UpdatePurchaseView(UpdateView):
  model = Purchase
  template_name = 'inventory/update_purchase.html'
  form_class = PurchaseEditForm


class DeletePurchaseView(DeleteView):
  model = Purchase
  template_name = 'inventory/delete_purchase.html'
  success_url = '/purchases'


class RecipeView(ListView):
    model = Recipe
    template_name = 'inventory/recipe.html'

    def get_queryset(self):
        self.menu_item = get_object_or_404(MenuItem, title=self.kwargs['recipe'])
        result = Recipe.objects.filter(menu_item__title=self.menu_item)
        return result

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
        kwargs = super(CreateRecipeView, self).get_form_kwargs()
        kwargs.update({'recipe': self.kwargs['recipe']})
        kwargs.update(self.kwargs)
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

        purchases = Purchase.objects.order_by()
        purchases = purchases.values_list('menu_item__title', flat=True)
        purchases = purchases.distinct()

        for item in purchases:
            orders = Purchase.objects.filter(menu_item__title=item)
            orders = orders.aggregate(total=Sum('quantity'))['total']

            dish_cost = Recipe.objects.filter(menu_item__title=item)
            expression = Sum(F('ingredient__unit_price') * F('quantity'))
            dish_cost = dish_cost.aggregate(total=expression)['total']

            self.orders_cost += orders * dish_cost

        result = Purchase.objects.all()
        purchase_expression = Sum(F('menu_item__price') * F('quantity'))
        result = result.aggregate(total=purchase_expression)['total']
        self.profit = result - self.orders_cost
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.orders_cost
        context['profit'] = self.profit
        return context
