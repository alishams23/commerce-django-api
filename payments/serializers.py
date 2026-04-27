import re
from rest_framework import serializers


class DetailPaySerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length = 50)
    last_name = serializers.CharField(max_length = 50)
    email = serializers.EmailField(required = False)
    is_different_address = serializers.BooleanField(default = False)
    province = serializers.CharField(max_length=20)
    city = serializers.CharField(max_length=30)
    address = serializers.CharField()
    zip_code = serializers.CharField(max_length=10)
    description = serializers.CharField(required = False)

    def validate_zip_code(self, value):
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Zip Code must 10 character")
        return value