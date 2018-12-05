from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    bio = serializers.CharField(allow_blank=True, required=False)
    
    class Meta:
        model = Profile
        fields = ('username', 'email', 'bio', 'image', 'following')
        read_only_fields = ('username',)