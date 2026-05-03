import django_filters

from django_filters import rest_framework as filters

from blog.models import Blog


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class BlogFilter(django_filters.FilterSet):
    
    category = CharInFilter(field_name = 'category__name',lookup_expr = 'in')

    class Meta:
        model = Blog
        fields = ['category']