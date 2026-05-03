from rest_framework import pagination


class Pagination10(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    last_page_strings = ('last_page',)
    