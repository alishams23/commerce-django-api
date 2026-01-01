from rest_framework import generics
from rest_framework.permissions import AllowAny
from core.filters.product_sort import ProductSortFilterBackend
from product.models import Category, CategoryChildren, Product
from django.db.models import Prefetch
from product.serializers import CategoryChildrenDetailSerializer,CategoryListSerializer, ProductDetailSerializer, ProductListSerializer
# Create your views here.


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategoryListSerializer

    def get_queryset(self):
        children_qs = CategoryChildren.objects.filter(is_active = True,is_deleted = False).order_by('order','created_at')
        return Category.objects.filter(is_active = True,is_deleted = False).\
        prefetch_related(Prefetch('children',queryset = children_qs)).order_by('order','created_at')
    
class ProductCategoryView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategoryChildrenDetailSerializer
    # TODO: Filter Backend
    def get_queryset(self):
        queryset = CategoryChildren.objects.filter(id = self.kwargs['id'],is_active = True,is_deleted = False).\
            prefetch_related('products','products__colors')
        return queryset
    
    
    
class ProductsListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    filter_backends = [ProductSortFilterBackend]
    def get_queryset(self):
        return Product.objects.filter(is_published = True)
    
class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    lookup_field = 'id'