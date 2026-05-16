from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from product.models import (
    Brand,
    Category,
    CategoryChildren,
    Color,
    Product,
    ProductComment,
)
from django.db.models import Count, Prefetch
from product.pagination import SearchPagination
from product.serializers import (
    ProductAddCommentSerializer,
    ProductCommentSerializer,
    BrandSerializer,
    CategoryListSerializer,
    ColorSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from product.utils import decode_product_id

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
            is_active=True, is_deleted=False
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
    queryset = (
        Product.objects.filter(is_published=True, is_deleted=False)
        .prefetch_related("colors__images", "colors__color")
        .annotate(rating=Count("interested_users", distinct=True))
        .distinct().order_by('-created_at')
    )

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
        "rating",
    ]


@extend_schema(
    summary="Retrieve Product",
    description="""
        Returns full details of a single published product.
        Includes brand, colors, images and comments.
    """,
    tags=["Product"],
)
class ProductDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = "slug"
    pagination_class = SearchPagination

    queryset = (
        Product.objects.filter(is_published=True, is_deleted=False)
        .prefetch_related("colors", "colors__images")
        .select_related("brand")
    )
    @extend_schema(
        summary="Retrieve Comments for a Product",
        description="""
            Returns a paginated list of top-level comments for a specific product.
            Replies are nested within each parent comment.
        """,
        responses=ProductCommentSerializer,
        tags=["Product"],
    )
    @action(detail=True, methods=["get"], url_path="comments")
    def product_comments(self, request, slug=None):
        return self.get_paginated_response(
            ProductCommentSerializer(
                self.paginate_queryset(
                    self.get_object()
                    .comments.filter(reply__isnull=True)
                    .order_by("-created_at")
                ),
                many=True,
                context={"request": request},
            ).data
        )


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
    queryset = Brand.objects.filter(is_deleted=False).only("id", "name")


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
    queryset = Color.objects.filter(is_deleted=False).only("id", "name", "code")





@extend_schema(
    summary="Add Comment to Product ",
    description="""
        Allows a user to add a comment to a specific product
        Supports:
        - Ability to reply to an existing comment by providing its ID.
        - Requires user authentication.
    """,
    tags=["Product"],
)
class AddCommentProductView(generics.CreateAPIView):
    serializer_class = ProductAddCommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = decode_product_id(serializer.validated_data["product_id"])
        product = get_object_or_404(Product, id=product_id)
        reply = serializer.validated_data.get("comment_id")

        if reply:
            reply = ProductComment.objects.filter(id=reply, product=product).first()

        ProductComment.objects.create(
            product=product,
            created_by=self.request.user,
            text=serializer.validated_data["text"],
            reply=reply,
        )

        return Response(
            {"status": "Success", "message": "Add Comment Successfully"},
            status=status.HTTP_201_CREATED,
        )
