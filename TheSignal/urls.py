"""
URL configuration for TheSignal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from news import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Public
    path('django-admin/', admin.site.urls),
    path('',                          views.home,                name='home'),
    path('article/<int:pk>/',         views.article_detail,      name='article_detail'),
    path('login/',                    views.login_view,          name='login'),
    path('logout/',                   views.logout_view,         name='logout'),
    path('register/',                 views.register_view,       name='register'),
    # Comments
    path('article/<int:article_pk>/comment/',      views.add_comment,    name='add_comment'),
    path('comment/<int:comment_pk>/reply/',        views.reply_comment,  name='reply_comment'),
    path('comment/<int:pk>/edit/',views.edit_comment,   name='edit_comment'),
    path('comment/<int:pk>/delete/',views.delete_comment, name='delete_comment'),
    path('article/<int:pk>/like/',views.like_article,   name='like_article'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    # Admin
    path('admin-panel/activity/load-more/',   views.load_more_activities, name='load_more_activities'),
    path('admin-panel/article/new/',          views.admin_article_create, name='admin_article_create'),
    path('admin-panel/article/<int:pk>/edit/',views.admin_article_edit,   name='admin_article_edit'),
    path('admin-panel/article/<int:pk>/del/', views.admin_article_delete, name='admin_article_delete'),
    path('admin-panel/users/',                views.admin_users,          name='admin_users'),
    path('admin-panel/users/<int:pk>/block/', views.admin_block_user,     name='admin_block_user'),
     path('admin-panel/users/<int:pk>/promote/', views.admin_make_author, name='admin_make_author'),
    path('admin-panel/comment/<int:pk>/del/', views.admin_delete_comment, name='admin_delete_comment'),
    path('newsletter/unsubscribe/<str:token>/', views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('admin-panel/send-newsletter/', views.admin_send_newsletter, name='admin_send_newsletter'),
    path('admin-panel/preview-newsletter/', views.admin_preview_newsletter, name='admin_preview_newsletter'),
    path('newsletter/unsubscribe-success/', views.unsubscribe_success, name='unsubscribe_success'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('admin-panel/users/<int:pk>/demote/', views.admin_demote_author, name='admin_demote_author'),
    path('export/users/', views.export_users_csv, name='export_users_csv'),
    path('export/articles/', views.export_articles_csv, name='export_articles_csv'),
    path('export/comments/', views.export_comments_csv, name='export_comments_csv'),
    path('api/breaking-news/', views.breaking_news_api, name='breaking_news_api'),
    path('export/summary/', views.export_platform_summary_csv, name='export_platform_summary_csv'),
    path('admin-panel/content/warn/<str:content_type>/<int:pk>/', views.admin_warn_content, name='admin_warn_content'),
    path('admin-panel/content/delete/<str:content_type>/<int:pk>/', views.admin_delete_content, name='admin_delete_content'),
    # path('accounts/', include('django.contrib.auth.urls'))
    path('password-reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='registration/password_reset_form.html',
         email_template_name='registration/password_reset_email.html',
         subject_template_name='registration/password_reset_subject.txt'
     ),
     name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
             # Breaking News
    path('api/breaking-news/', views.breaking_news_api, name='breaking_news_api'),
    path('admin/breaking-news/add/', views.admin_breaking_news_add, name='admin_breaking_news_add'),
    path('admin/breaking-news/<int:pk>/edit/', views.admin_breaking_news_edit, name='admin_breaking_news_edit'),
    path('admin/breaking-news/<int:pk>/delete/', views.admin_breaking_news_delete, name='admin_breaking_news_delete'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('terms/', views.terms_page, name='terms'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
