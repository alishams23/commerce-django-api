import django_filters
from django_filters import rest_framework as filters
from product.models import Product

class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="gte")

    max_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="lte")

    brand = NumberInFilter(field_name="brand__id",lookup_expr='in')

    color = NumberInFilter(field_name="colors__color__id",lookup_expr = 'in')

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "brand", "color"]

