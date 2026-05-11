from django.contrib import admin
from .models import Category, Post ,BreakingNews

admin.site.register(Category)  
admin.site.register(Post)
admin.site.register(BreakingNews)
