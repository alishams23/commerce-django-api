import django_filters
from core.filters.boolean_filter import OnlyTrueFilter
from core.filters.char_filter import CharInFilter
from product.models import Product



class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="gte")

    max_price = django_filters.NumberFilter(field_name="fixed_price", lookup_expr="lte")

    brand = CharInFilter(field_name="brand__name",lookup_expr='in')

    color = CharInFilter(field_name="colors__color__name",lookup_expr = 'in')

    category = CharInFilter(field_name="category__name",lookup_expr = 'in')

    popular = OnlyTrueFilter(field_name="is_favorite")
    class Meta:
        model = Product
        fields = ["min_price", "max_price", "brand", "color","category","popular"]

