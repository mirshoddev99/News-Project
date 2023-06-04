from django.contrib import admin
from news_app.models import Category, News, Contact, Comment


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_time', 'status']
    list_filter = ['title', 'status', 'created_time', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['status', 'published_time']
    search_fields = ['title', 'status']
    date_hierarchy = 'published_time'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email']
    search_fields = ['name', 'email']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'active']
    search_fields = ['name', 'created_time']
