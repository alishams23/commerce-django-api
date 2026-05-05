import django_filters

from blog.models import Blog
from core.filters.char_filter import CharInFilter


class BlogFilter(django_filters.FilterSet):
    
    category = CharInFilter(field_name = 'category__name',lookup_expr = 'in')

    class Meta:
        model = Blog
        fields = ['category']