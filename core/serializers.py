from rest_framework import serializers
from .models import Post, SocialMediaPost

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'platform', 'username', 'text', 'timestamp']

class SocialMediaPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaPost
        fields = '__all__'