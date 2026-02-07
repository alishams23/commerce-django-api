from django.urls import path
from .views import BrandListView, CategoryListView, ColorListView, GalleryView, ProductsByCategoryView, ProductDetailView, ProductsListView

urlpatterns = [
    # ------------------- Home/Index -------------------
    path('brands-list/',BrandListView.as_view(),name = "brand-list"),
    path('colors-list/',ColorListView.as_view(),name = "color-list"),
    path('categories-list/',CategoryListView.as_view(),name = "categories-list"),
    path('categories/<int:id>/products/',ProductsByCategoryView.as_view(),name = "category-products-list"),
    path('list/',ProductsListView.as_view(),name = "products-list"),
    path('gallery/',GalleryView.as_view(),name = "products-list"),
    
    # ------------------- Detail -------------------
    path('product-detail/<int:id>/',ProductDetailView.as_view(),name = "product-detail"),
]
