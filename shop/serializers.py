from rest_framework import serializers

from shop.models import AboutUs, ShopSettings


class ShopSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopSettings
        fields = (
            "name",
            "logo",
            "support_phone",
            "support_mobile",
            "instagram_url",
            "telegram_url",
            "shop_address",
            "factory_address",
            "footer_text",
        )


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = (
            "title",
            "text",
            "media_type",
            "media_url",
            "media_file",
        )
