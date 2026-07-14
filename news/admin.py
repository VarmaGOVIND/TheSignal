from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Article, Comment, UserActivity
from .models import NewsletterSubscriber
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

from news.utils import generate_unsubscribe_token



@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('username','email','role','is_blocked','date_joined')
    list_filter   = ('role','is_blocked')
    search_fields = ('username','email')
    fieldsets     = UserAdmin.fieldsets + ((None, {'fields':('role','bio','avatar','is_blocked')}),)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display  = ('title','category','tag','author','is_published','created_at','get_like_count')
    list_filter   = ('category','tag','is_published')
    search_fields = ('title','excerpt','body')
    date_hierarchy = 'created_at'
    readonly_fields = ('views','created_at','updated_at')
    def get_like_count(self,obj):
        return obj.likes.count()
    get_like_count.short_description = 'Total Likes'
    get_like_count.admin_order_field = 'likes'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author','article','parent','created_at','is_deleted')
    list_filter  = ('is_deleted',)
    search_fields = ('text','author__username')

@admin.register(UserActivity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user','action','created_at')
    readonly_fields = ('user','action','created_at')



@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active', 'quick_unsubscribe')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def quick_unsubscribe(self, obj):
        """Admin panel mein ek-click unsubscribe button"""
        if obj.is_active:
            token = generate_unsubscribe_token(obj.email)
            from django.utils.html import format_html
            return format_html(
                '<a href="/newsletter/unsubscribe/{}/" style="color:#ff4444;">Unsubscribe</a>',
                token
            )
        return '❌ Already Unsubscribed'
    quick_unsubscribe.short_description = 'Unsubscribe'
    
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} subscribers activated!')
    activate_subscribers.short_description = "✅ Activate Selected"
    
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} subscribers deactivated!')
    deactivate_subscribers.short_description = "❌ Deactivate Selected"