from rest_framework.filters import BaseFilterBackend


class ProductSortFilterBackend(BaseFilterBackend):

    SORT_MAPPING = {
        "cheep":"fixed_price",
        "expensive":"-fixed_price",
        "newest":"-created_at",
        # "popular":"-sold_count",#TODO: Apply Popular
        # "top_rate":"-rating",#TODO: Apply top_rate
    }
    
    def filter_queryset(self, request, queryset, view):
        sort_param = request.query_params.get("sort")

        ordering = self.SORT_MAPPING.get(sort_param)
        
        if sort_param and ordering:
            return queryset.order_by(ordering)
        
        return queryset
        
        