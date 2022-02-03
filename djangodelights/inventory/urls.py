from django.urls import path

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('ingredients/', views.IngredientView.as_view(), name='ingredients'),
    path('ingredients/new/', views.CreateIngredientView.as_view(), name='create_ingredients'),
    path('ingredients/<pk>/update/', views.UpdateIngredientView.as_view(), name='update_ingredients'),
    path('ingredients/<pk>/stock/', views.IngredientStockView.as_view(), name='update_stock'),
    path('ingredients/<pk>/delete/', views.DeleteIngredientView.as_view(), name='delete_ingredients'),
    path('inventory/', views.InvetoryView.as_view(), name='inventory'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('menu/new/', views.CreateMenuView.as_view(), name='create_menu'),
    path('menu/<pk>/nameupdate/', views.UpdateMenuNameView.as_view(), name='update_menu_name'),
    path('menu/<pk>/priceupdate/', views.UpdateMenuPriceView.as_view(), name='update_menu_price'),
    path('menu/<pk>/delete/', views.DeleteMenuView.as_view(), name='delete_menu'),
    path('purchases/', views.PurchaseView.as_view(), name='purchases'),
    path('purchases/new/', views.CreatePurchaseView.as_view(), name='create_purchases'),
    path('purchases/<pk>/update/', views.UpdatePurchaseView.as_view(), name='update_purchases'),
    path('purchases/<pk>/delete/', views.DeletePurchaseView.as_view(), name='delete_purchases'),
    path('menu/recipe/<recipe>/', views.RecipeView.as_view(), name='recipe_view'),
    path('menu/recipe/<recipe>/new/', views.CreateRecipeView.as_view(), name='create_recipe'),
    path('menu/recipe/<pk>/update/', views.UpdateRecipeView.as_view(), name='update_recipe'),
    path('menu/recipe/<pk>/delete/', views.DeleteRecipeView.as_view(), name='delete_recipe'),
    path('reports/', views.ReportView.as_view(), name='report'),
]
