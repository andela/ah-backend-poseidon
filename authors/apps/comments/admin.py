from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Comment


 # Register your models here.
class CommentAdmin(admin.ModelAdmin):
    fields = ('author', 'body', 'parent', 'slug')
    list_display = ('body', 'author', 'created_at',
                    'updated_at', 'parent', 'id', 'slug', 'start')
admin.site.register(Comment)
