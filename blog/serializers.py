from rest_framework import serializers

from blog.models import Blog, BlogComment, CategoryBlog
from user.serializers import UserCommentsSerializer


class CategoryBlogSerializer(serializers.ModelSerializer):
    count_articles = serializers.SerializerMethodField()

    class Meta:
        model = CategoryBlog
        fields = ['id','name','count_articles']
        
    def get_count_articles(self,obj):
        return obj.blogs.count()

class BlogListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source = "category.name")
    class Meta:
        model = Blog
        fields = ['category','title','slug','published_at','reading_time','cover']


class BlogDetailSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source = "created_by.get_full_name")
    user_liked = serializers.SerializerMethodField()
    liked_count = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = ['id','cover','published_at','reading_time','created_by','user_liked','liked_count','title','text_body']
    
    def get_user_liked(self,obj):
        user = self.context.get("request").user 
        if user.is_authenticated:
            return(user.liked_blogs.filter(id = obj.id).exists())
        return False
    
    def get_liked_count(self,obj):
        return obj.likes.count()
    
class BlogCommentSerializer(serializers.ModelSerializer):
    created_by = UserCommentsSerializer()
    replies = serializers.SerializerMethodField("get_replies")

    class Meta:
        model = BlogComment
        fields = ["id", "created_by", "created_at" ,"text", "replies"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return BlogCommentSerializer(obj.replies.all(), many=True).data
        return None

class BlogAddCommentSerializer(serializers.Serializer):
    blog_id = serializers.IntegerField(required = True)
    comment_id = serializers.IntegerField(required = False,help_text = "The ID of the parent comment if this comment is a reply")
    text = serializers.CharField(max_length=700)