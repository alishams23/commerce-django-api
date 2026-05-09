from django.urls import path
from .views import AddCommentProductView, BrandListView, CategoryListView, ColorListView, GalleryView, ProductDetailViewSet, ProductsListView
from rest_framework.routers import DefaultRouter


urlpatterns = [
    # ------------------- Home/Index -------------------
    path('brands-list/',BrandListView.as_view(),name = "brand-list"),
    path('colors-list/',ColorListView.as_view(),name = "color-list"),
    path('categories-list/',CategoryListView.as_view(),name = "categories-list"),
    path('list/',ProductsListView.as_view(),name = "products-list"),
    path('gallery/',GalleryView.as_view(),name = "gallery"),
    
    # ------------------- Detail -------------------
    path('add-comment/',AddCommentProductView.as_view(),name = "add-comment"),
]

router = DefaultRouter()
router.register('detail', ProductDetailViewSet, basename="product-detail")
urlpatterns += router.urls