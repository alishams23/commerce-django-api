from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from product.models import Brand, Category, CategoryChildren, Color, Gallery, Product
from django.db.models import Prefetch
from product.pagination import SearchPagination
from product.serializers import (
    BrandSerializer,
    CategoryListSerializer,
    ColorSerializer,
    GallerySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter


@extend_schema(
    summary="List Categories",
    description="""
        Returns active categories with their active children.
        Used for category navigation and menus.
    """,
    tags=["Home"],
)
class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategoryListSerializer

    def get_queryset(self):
        children_qs = CategoryChildren.objects.filter(
            is_active=True,show_in_menu = True,is_deleted=False
        ).order_by("order", "created_at")
        return (
            Category.objects.filter(is_active=True, is_deleted=False)
            .prefetch_related(Prefetch("children", queryset=children_qs))
            .order_by("order", "created_at")
        )


@extend_schema(
    summary="List Products",
    description="""
        Returns paginated list of published products.

        Supports:
        - search (name, description, specifications)
        - ordering (fixed_price, created_at)
        - filters (price range, brand, color)
    """,
    tags=["Home"],
)
class ProductsListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    pagination_class = SearchPagination
    queryset = Product.objects.filter(is_published=True, is_deleted=False).prefetch_related("colors__images","colors__color").distinct()

    filterset_class = ProductFilter

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    search_fields = [
        "name",
        "description",
        "specifications",
    ]

    ordering_fields = [
        "fixed_price",
        "created_at",
        # "is_favorite",#TODO
        # "rating",#TODO
    ]


@extend_schema(
    summary="List Products By Category (Children)",
    description="""
        Returns paginated products of a specific **category child**.

        The `id` in the URL must be the **CategoryChildren ID** (not parent category).

        Supports:
        - search
        - ordering
        - filters (price, brand, color)
    """,
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="CategoryChildren ID",
            required=True,
        ),
    ],
    tags=["Product"],
)
class ProductsByCategoryView(ProductsListView):
    def get_queryset(self):
        return Product.objects.filter(
            category__id=self.kwargs["id"],
            is_published=True,
            is_deleted=False,
            category__is_active=True,
            category__is_deleted=False,
        ).prefetch_related("colors", "colors__images")


@extend_schema(
    summary="Retrieve Product",
    description="""
        Returns full details of a single published product.
        Includes brand, colors, images and comments.
    """,
    tags=["Product"],
)
class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    queryset = (
        Product.objects.filter(is_published=True, is_deleted=False)
        .prefetch_related("colors", "colors__images", "comments")
        .select_related("brand")
    )
    lookup_field = "id"


@extend_schema(
    summary="List Brands",
    description="""
        Returns list of available brands.
        Used for product filtering.
    """,
    tags=["Product"],
)
class BrandListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BrandSerializer
    queryset = Brand.objects.filter(is_deleted = False).only('id','name')


@extend_schema(
    summary="List Colors",
    description="""
        Returns list of available colors.
        Used for product variations and filters.
    """,
    tags=["Product"],
)
class ColorListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ColorSerializer
    queryset = Color.objects.filter(is_deleted = False).only('id','name','code')

@extend_schema(
    summary="Gallery",
    description="""
        Returns list of Images.
        Used for Gallery.
    """,
    tags=["Home"],
)

class GalleryView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = GallerySerializer
    queryset = Gallery.objects.filter(is_published = True,is_deleted = False).only('id','image','order')