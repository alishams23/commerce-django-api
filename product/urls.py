from django.urls import path
from .views import CategoryListView,ProductCategoryView, ProductDetailView, ProductsListView

urlpatterns = [
    path('categories-list/',CategoryListView.as_view(),name = "categories-list"),
    path('category-products-list/<int:id>/',ProductCategoryView.as_view(),name = "category-products-list"),
    path('products-list/',ProductsListView.as_view(),name = "products-list"),
    path('product-detail/<int:id>/',ProductDetailView.as_view(),name = "product-detail"),
]
