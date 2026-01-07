import django_filters

from product.models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="gte")

    max_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="lte")

    brand = django_filters.NumberFilter(field_name="brand__id")

    color = django_filters.NumberFilter(field_name="colors__color__id")

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "brand", "color"]

