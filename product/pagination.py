from rest_framework import pagination
from rest_framework.response import Response

class SearchPagination(pagination.PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )
    #For Swagger
    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "links": {
                    "type": "object",
                    "properties": {
                        "next": {"type": "string", "nullable": True},
                        "previous": {"type": "string", "nullable": True},
                    },
                },
                "count": {"type": "integer"},
                "total_pages": {"type": "integer"},
                "results": schema,
            },
        }
