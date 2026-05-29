from product.serializers import ProductListSerializer
from promotions.models import Banner, Campaign, Gallery
from rest_framework import serializers


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["title","text","image","url"]
        
class CampaignSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many = True)
    class Meta:
        model = Campaign
        fields = ["title","start_time","end_time","products"]


# <------------ Gallery ---------------->


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ["id", "order", "image"]
