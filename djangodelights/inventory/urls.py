from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('account/', include('django.contrib.auth.urls')),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('menu/displayupdate/', views.UpdateMenuDisplayView.as_view(), name='update_menu_display'),
    path('menu/new/', views.CreateMenuView.as_view(), name='create_menu'),
    path('menu/<pk>/nameupdate/', views.UpdateMenuNameView.as_view(), name='update_menu_name'),
    path('menu/<menu_item>/priceupdate/', views.UpdateMenuPriceView.as_view(), name='update_menu_price'),
    path('menu/<menu_item>/delete/', views.DeleteMenuView.as_view(), name='delete_menu'),
    path('purchases/', views.PurchaseView.as_view(), name='purchases'),
    path('purchases/new/', views.CreatePurchaseView.as_view(), name='create_purchases'),
    path('purchases/<pk>/update/', views.UpdatePurchaseView.as_view(), name='update_purchases'),
    path('purchases/<pk>/delete/', views.DeletePurchaseView.as_view(), name='delete_purchases'),
    path('menu/<menu_item>', views.Details.as_view(), name='details'),
    path('menu/<menu_item>/edit/', views.UpdateMenuDescriptionView.as_view(), name='menu_item_edit'),
    path('menu/<menu_item>/edit/new/', views.CreateRecipeView.as_view(), name='create_recipe'),
    path('menu/<menu_item>/edit/<ingredient>/qty/', views.UpdateRecipeView.as_view(), name='update_recipe'),
    path('menu/<menu_item>/edit/<ingredient>/delete/', views.DeleteRecipeView.as_view(), name='delete_recipe'),
    path('salesprofit/', views.SalesProfitView.as_view(), name='sales_profit'),
    path('salesprofit/reports/', views.ReportView.as_view(), name='report'),
    path('salesprofit/bestsellers', views.BestSellerView.as_view(), name='best_sellers'),
    path('stock/', views.StockView.as_view(), name='stock'),
    path('stock/currentstock/', views.CurrentStockView.as_view(), name='current_stock'),
    path('stock/currentstock/update/', views.UpdateStockView.as_view(), name='update_stock'),
    path('stock/stockedrecipes/', views.StockedRecipes.as_view(), name='stocked_recipes'),
    path('stock/shoppinglist/', views.ShoppingList.as_view(), name='shopping_list'),
    path('stock/ingredients/', views.IngredientView.as_view(), name='ingredients'),
    path('stock/ingredients/new/', views.CreateIngredientView.as_view(), name='create_ingredients'),
    path('stock/ingredients/<name>/update/', views.UpdateIngredientView.as_view(), name='update_ingredients'),
    path('stock/ingredients/<name>/delete/', views.DeleteIngredientView.as_view(), name='delete_ingredients'),
    path('stock/ingredients/orphans/', views.OrphanIngredientView.as_view(), name='orphans'),
]
