from django.contrib import admin
from .models import Product, ProductCategory, Article, Comment, Tag

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    list_per_page = 20

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'sales_count', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_active']
    list_per_page = 20
    ordering = ['-created_at']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'article_type', 'created_at', 'is_draft', 'views_count']
    list_filter = ['article_type', 'is_draft']
    search_fields = ['title', 'content']
    list_editable = ['is_draft']
    list_per_page = 20
    ordering = ['-created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['article', 'author', 'content', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content']
    list_per_page = 20
    ordering = ['-created_at']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_per_page = 20 