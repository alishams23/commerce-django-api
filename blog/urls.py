from django.urls import path

from blog.views import AddCommentBlogView, BlogDetailViewSet, BlogLikeViewSet, BlogListView, CategoryBlogListView

from rest_framework.routers import DefaultRouter

urlpatterns = [
    path("categories-list/",CategoryBlogListView.as_view(),name = "categories-list"),
    path('list/',BlogListView.as_view(),name = "blogs-list"),
    path('add-comment/',AddCommentBlogView.as_view(),name = "add-comment"),
]

router = DefaultRouter()
router.register('detail', BlogDetailViewSet, basename="blog")
router.register("like",BlogLikeViewSet,basename = 'Like')

urlpatterns += router.urls