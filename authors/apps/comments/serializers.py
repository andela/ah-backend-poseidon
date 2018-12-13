from django.shortcuts import get_object_or_404
from rest_framework import serializers
from authors.apps.authentication.models import User
from authors.apps.profiles.models import Profile
from authors.apps.profiles.serializers import ProfileSerializer
from .models import Comment


class Validate_method:

    error_message = NotImplemented

    @classmethod
    def validate(cls, data):
        body = data.get('body', None)
        if body is None:
            raise serializers.ValidationError(cls.error_message)
        return data


class CommentSerializer(Validate_method, serializers.ModelSerializer):
    """
        Class Handles comment data
    """
    replies = serializers.SerializerMethodField('get_is_parent')
    commented_by = serializers.ReadOnlyField(source='commented_by.username')
    parent = serializers.ReadOnlyField(source='commented_by.parent')

    error_message = {"message": 'Please insert comment'}

    class Meta:
        model = Comment
        fields = ('id', 'body', 'commented_by', 'created_at', 'updated_at',
                  'replies', 'parent')

    def get_is_parent(self, object):
        if not object.is_parent:
            return CommentChildSerializer(object.children(), many=True).data
        return object.parent


class CommentChildSerializer(Validate_method, serializers.ModelSerializer):
    """
        Class Handles child comment data
    """
    error_message = {"message": 'Please insert reply'}

    commented_by = serializers.ReadOnlyField(source='commented_by.username')

    class Meta:
        model = Comment
        fields = ('body', 'commented_by', 'created_at', 'updated_at', 'parent')
