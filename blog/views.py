from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters, viewsets, status
from rest_framework.permissions import AllowAny
from blog.filters import BlogFilter
from blog.models import Blog, CategoryBlog, BlogComment
from blog.serializers import (
    BlogAddCommentSerializer,
    BlogCommentSerializer,
    BlogDetailSerializer,
    BlogListSerializer,
    CategoryBlogSerializer,
)
from product.pagination import SearchPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema

# Create your views here.


@extend_schema(
    summary="Retrieve a list of active and non-deleted blog categories",
    description="""
        Returns a list of active, non-deleted blog categories, sorted by 'order' and 'created_at'. 
        Accessible to all user.
        """,
    tags=["Blog"],
)
class CategoryBlogListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategoryBlogSerializer

    def get_queryset(self):
        return CategoryBlog.objects.filter(is_active=True, is_deleted=False).order_by(
            "order", "created_at"
        )


@extend_schema(
    summary="List Blogs",
    description="""
        Returns paginated list of published blogs.

        Supports:
        - search (title, text_body)
        - filters (category)
    """,
    tags=["Blog"],
)
class BlogListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogListSerializer
    pagination_class = SearchPagination
    queryset = Blog.objects.select_related("category").filter(
        is_published=True, is_deleted=False, category__is_active=True
    )

    filterset_class = BlogFilter

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    search_fields = [
        "title",
        "text_body",
    ]


@extend_schema(
    summary="Retrieve Blog Details",
    description="""
        Returns details of a published blog post.
    """,
    tags=["Blog"],
)
class BlogDetailViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = BlogDetailSerializer
    lookup_field = "slug"
    queryset = Blog.objects.filter(
        is_published=True, is_deleted=False
    ).prefetch_related("comments")
    pagination_class = SearchPagination

    @extend_schema(
        summary="Retrieve Comments for Blog Post",
        description="""
            Returns a paginated list of comments for a specific blog post
        """,
        responses=BlogCommentSerializer,
        tags=["Blog"],
    )
    @action(detail=True, methods=["GET"])
    def comments(self, request, slug):
        return self.get_paginated_response(
            BlogCommentSerializer(
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
    summary="Manage Liked Blogs",
    description="""
        Authenticated users to add or remove blogs from their liked list.
    """,
    parameters=[
        OpenApiParameter(
            name="id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="Blog ID",
            required=True,
        ),
    ],
    tags=["Blog"],
)
class BlogLikeViewSet(viewsets.ViewSet):
    lookup_field = "id"

    @action(detail=True, methods=["POST"])
    def add(self, request, id):
        self.request.user.liked_blogs.add(get_object_or_404(Blog, id=id))
        return Response({"status": "Success", "Message": "Blog Add To liked."})

    @action(detail=True, methods=["Delete"])
    def remove(self, request, id):
        self.request.user.liked_blogs.remove(get_object_or_404(Blog, id=id))
        return Response({"status": "Success", "Message": "Blog Removed To liked."})


@extend_schema(
    summary="Add Comment to Blog ",
    description="""
        Allows a user to add a comment to a specific Blog
        Supports:
        - Ability to reply to an existing comment by providing its ID.
        - Requires user authentication.
    """,
    tags=["Blog"],
)
class AddCommentBlogView(generics.CreateAPIView):
    serializer_class = BlogAddCommentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blog = get_object_or_404(Blog, id=serializer.validated_data["blog_id"])
        reply = serializer.validated_data.get("comment_id")

        if reply:
            reply = BlogComment.objects.filter(id=reply, blog=blog).first()

        BlogComment.objects.create(
            blog=blog,
            created_by=self.request.user,
            text=serializer.validated_data["text"],
            reply=reply,
        )

        return Response(
            {"status": "Success", "message": "Add Comment Successfully"},
            status=status.HTTP_201_CREATED,
        )
