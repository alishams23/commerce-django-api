from rest_framework import serializers

from user.models import User

class UserCommentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['get_full_name','profile_image']