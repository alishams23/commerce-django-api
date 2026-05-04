import django_filters
from django_filters import rest_framework as filters
from product.models import Product

class NameInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="gte")

    max_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="lte")

    brand = NameInFilter(field_name="brand__name",lookup_expr='in')

    color = NameInFilter(field_name="colors__color__name",lookup_expr = 'in')

    category = NameInFilter(field_name="category__name",lookup_expr = 'in')

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "brand", "color","category"]

