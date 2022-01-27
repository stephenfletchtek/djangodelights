from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import MenuItem, Ingredient, Recipe, Purchase


class HomeView(TemplateView):
  template_name = "inventory/home.html"

  def get_context_data(self):
    context = super().get_context_data()
    context["menu"] = MenuItem.objects.all()
    context["ingredients"] = Ingredient.objects.all()
    context["recipes"] = Recipe.objects.all()
    return context


class MenuView(ListView):
  model = MenuItem
  template_name = 'inventory/menu.html'
