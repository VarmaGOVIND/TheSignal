import hashlib,csv
import time
from datetime import timedelta, date
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .utils import generate_unsubscribe_token

from django.http import JsonResponse, HttpResponseForbidden , HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, F
from django.core.paginator import Paginator
from .models import NewsletterSubscriber, User, Article, Comment, UserActivity, BreakingNews 
from .forms  import RegisterForm, ArticleForm, CommentForm
from .forms import NewsletterForm

from news.models import TOPIC_CHOICES
from django.core.mail import send_mail
from django.conf import settings



def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

def is_author_or_admin(user):
    return user.is_authenticated and user.role in ['admin', 'author']

def log(user, action):
    UserActivity.objects.create(user=user, action=action)

def breaking_news_api(request):
    news_items = BreakingNews.objects.filter(is_active=True)

    data = []
    for item in news_items:
        url = '#'
        if item.article:
            url = f"/article/{item.article.pk}/"
        elif item.external_url:
            url = item.external_url

        data.append({
            'text': item.text,
            'url': url,
            'is_clickable': bool(item.article or item.external_url)
        })

    return JsonResponse(data, safe=False)


def home(request):
    topic    = request.GET.get('topic','All')
    query    = request.GET.get('q', '').strip()
    articles = Article.objects.filter(is_published=True).annotate(num_likes=Count('likes')).order_by('-created_at')

    user_is_subscribed = False
    if request.user.is_authenticated:
        user_is_subscribed = NewsletterSubscriber.objects.filter(
            email=request.user.email, 
            is_active=True
        ).exists()

    date_filter = request.GET.get('date_filter', 'all')
    today = timezone.now().date()

    if date_filter == 'today':
        articles = articles.filter(created_at__date=today)
    elif date_filter == 'week':
        articles = articles.filter(created_at__date__gte=today - timedelta(days=7))
    elif date_filter == 'month':
        articles = articles.filter(created_at__date__gte=today - timedelta(days=30))
    elif date_filter == 'year':
        articles = articles.filter(created_at__date__gte=today - timedelta(days=365))
    elif date_filter == 'custom':
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if from_date:
            articles = articles.filter(created_at__date__gte=from_date)
        if to_date:
            articles = articles.filter(created_at__date__lte=to_date)

    if query:
            from django.db.models import Q
            articles = articles.filter(
                Q(title__icontains=query) | 
                Q(excerpt__icontains=query) | 
                Q(category__icontains=query)
            )

    if topic != 'All':
        articles = articles.filter(category=topic)

    paginator = Paginator(articles, 12)
    page      = paginator.get_page(request.GET.get('page',1))
    trending  = Article.objects.filter(is_published=True).annotate(
        num_likes=Count('likes')).order_by('-num_likes')[:5]
    return render(request, 'news/home.html', {
        'page':      page,
        'topics':    [c[0] for c in Article._meta.get_field('category').choices],
        'active':    topic,
        'trending':  trending,
        'featured':  articles.first(),
        'user_is_subscribed': user_is_subscribed,
        'date_filter': date_filter,
        'query': query,  
    })


def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    Article.objects.filter(pk=pk).update(views=F('views')+1)
    comments = article.comments.filter(parent__isnull=True, is_deleted=False).prefetch_related(
        'replies','author','replies__author'
    )
    comment_form = CommentForm()
    return render(request, 'news/article_detail.html', {
        'article':      article,
        'comments':     comments,
        'comment_form': comment_form,
        'liked':        request.user.is_authenticated and article.likes.filter(pk=request.user.pk).exists(),
    })




def login_view(request):
    error = ''
    if request.method == 'POST':
        u = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if u:
            if u.is_blocked:
                error = 'Your account has been blocked.'
            else:
                login(request, u)
                remember_me = request.POST.get('remember')
                if remember_me:
                    request.session.set_expiry(1209600)  
                    #2 weeks (14 days)
                else:
                    request.session.set_expiry(0)
                    #browser close it will expire
            
                request.session.modified = True
                
                return redirect('admin_dashboard' if u.is_admin_role else 'home')
        else:
            error = 'Invalid credentials.'
    return render(request, 'news/login.html', {'error': error})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')
    return render(request, 'news/register.html', {'form': form})




@login_required
@require_POST
def add_comment(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk, is_published=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.article = article
        c.author  = request.user
        c.save()
        log(request.user, f"Commented on '{article.title[:60]}'")
    return redirect('article_detail', pk=article_pk)

@login_required
@require_POST
def reply_comment(request, comment_pk):
    parent  = get_object_or_404(Comment, pk=comment_pk)
    text    = request.POST.get('text','').strip()
    if text:
        Comment.objects.create(article=parent.article, author=request.user, parent=parent, text=text)
        log(request.user, f"Replied to comment #{comment_pk}")
    return redirect('article_detail', pk=parent.article.pk)

@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        comment.text = request.POST.get('text','').strip() or comment.text
        comment.save()
        log(request.user, f"Edited comment #{pk}")
    return redirect('article_detail', pk=comment.article.pk)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user and not request.user.is_admin_role:
        return HttpResponseForbidden()
    article_pk = comment.article.pk
    comment.delete()
    log(request.user, f"Deleted comment #{pk}")
    return redirect('article_detail', pk=article_pk)

@login_required
@require_POST
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.likes.filter(pk=request.user.pk).exists():
        article.likes.remove(request.user)
        liked = False
    else:
        article.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': article.likes.count()})





@user_passes_test(is_author_or_admin)
def admin_dashboard(request):
    if request.user.role == 'author':
        articles = Article.objects.filter(author=request.user).annotate(num_likes=Count('likes')).order_by('-created_at')
        categories_data = Article.objects.filter(author=request.user).values('category').annotate(count=Count('id')).order_by('-count')
        top_articles = articles.order_by('-views')[:5]
        all_comments = Comment.objects.filter(article__author=request.user).select_related('article', 'author').order_by('-created_at')[:20]
        recent_activity = UserActivity.objects.filter(user=request.user).order_by('-created_at')[:15]
    else:
        articles = Article.objects.annotate(num_likes=Count('likes')).order_by('-created_at')
        categories_data = Article.objects.values('category').annotate(count=Count('id')).order_by('-count')
        top_articles = articles.order_by('-views')[:5]
        all_comments = Comment.objects.select_related('article', 'author').order_by('-created_at')[:20]
        recent_activity = UserActivity.objects.order_by('-created_at')[:15]
    
    
    cat_labels = [item['category'] for item in categories_data]
    cat_counts = [item['count'] for item in categories_data]
    
    art_labels = [a.title[:20] + '...' if len(a.title) > 20 else a.title for a in top_articles]
    art_views = [a.views for a in top_articles]

    
    today = date.today()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    line_labels = [d.strftime('%b %d') for d in last_7_days]
    
    line_counts = []
    for d in last_7_days:
        if request.user.role == 'author':
            count = Article.objects.filter(author=request.user, created_at__date=d).count()
        else:
            count = Article.objects.filter(created_at__date=d).count()
        line_counts.append(count)

    categories = [c[0] for c in TOPIC_CHOICES]
    all_users = User.objects.all().order_by('username')
    
    breaking_news_items = BreakingNews.objects.all().order_by('-order', '-created_at')
    
    
    if request.user.role == 'author':
        all_articles_for_breaking = Article.objects.filter(author=request.user).order_by('-created_at')
        print(f" AUTHOR MODE: Showing only {request.user.username}'s articles")
    else:
        all_articles_for_breaking = Article.objects.all().order_by('-created_at')
        print(f"👑 ADMIN MODE: Showing all articles")
    
    print(f"📊 Total articles in dropdown: {all_articles_for_breaking.count()}")

    context = {
        'articles': articles,
        'top_articles': top_articles,
        'all_comments': all_comments,
        'recent_activity': recent_activity,
        'categories': categories,
        'all_users': all_users,
        'cat_labels': cat_labels,
        'cat_counts': cat_counts,
        'art_labels': art_labels,
        'art_views': art_views,
        'line_labels': line_labels,
        'line_counts': line_counts,
        'breaking_news_items': breaking_news_items,
        'all_articles_for_breaking': all_articles_for_breaking,
    }
    
    
    if request.user.role == 'admin':
        context.update({
            'total_users': User.objects.count(),
            'total_articles': Article.objects.count(),
            'total_comments': Comment.objects.count(),
            'blocked_users': User.objects.filter(is_blocked=True).count(),
            'users': User.objects.exclude(pk=request.user.pk).order_by('-date_joined'),
        })
    else:
        
        context.update({
            'total_articles': Article.objects.filter(author=request.user).count(),
            'total_comments': Comment.objects.filter(article__author=request.user).count(),
        })

    return render(request, 'news/admin_dashboard.html', context)


@user_passes_test(is_author_or_admin)
def admin_breaking_news_add(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        article_id = request.POST.get('article')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if text:
            article = None
            if article_id:
                try:
                    article = Article.objects.get(pk=article_id)
                except Article.DoesNotExist:
                    article = None
            
            BreakingNews.objects.create(
                text=text,
                article=article,
                order=int(order) if order else 0,
                is_active=is_active
            )
            messages.success(request, "Breaking news added successfully!")
            log(request.user, f"Added breaking news: '{text[:50]}'")
        else:
            messages.error(request, "Text is required!")
    
    return redirect('admin_dashboard')


@user_passes_test(is_author_or_admin)
def admin_breaking_news_edit(request, pk):
    news_item = get_object_or_404(BreakingNews, pk=pk)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        article_id = request.POST.get('article')
        order = request.POST.get('order', 0)
        is_active = request.POST.get('is_active') == 'on'
        
        if text:
            news_item.text = text
            news_item.order = int(order) if order else 0
            news_item.is_active = is_active
            
            if article_id:
                try:
                    news_item.article = Article.objects.get(pk=article_id)
                except Article.DoesNotExist:
                    news_item.article = None
            else:
                news_item.article = None
            
            news_item.save()
            messages.success(request, "Breaking news updated successfully!")
            log(request.user, f"Edited breaking news: '{text[:50]}'")
        else:
            messages.error(request, "Text is required!")
        
        return redirect('admin_dashboard')
    
        
    if request.user.role == 'author':
        articles_for_breaking = Article.objects.filter(author=request.user).order_by('-created_at')
    else:
        articles_for_breaking = Article.objects.all().order_by('-created_at')
    
    return render(request, 'news/admin_breaking_news_edit.html', {
        'news_item': news_item,
        'all_articles_for_breaking': articles_for_breaking
    })


@user_passes_test(is_author_or_admin)
def admin_breaking_news_delete(request, pk):
    if request.method == 'POST':
        news_item = get_object_or_404(BreakingNews, pk=pk)
        log(request.user, f"Deleted breaking news: '{news_item.text[:50]}'")
        news_item.delete()
        messages.success(request, "Breaking news deleted successfully!")
    
    return redirect('admin_dashboard')




@login_required
@user_passes_test(is_author_or_admin)
def admin_article_create(request):
    form = ArticleForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        a = form.save(commit=False)
        a.author = request.user
        if request.POST.get('action') == 'draft':
            a.is_published = False
        else:
            a.is_published = True
        
        a.save()
        log(request.user, f"Created article '{a.title[:60]}'")
        
        
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('home')  
        #author go to home page
    
    from news.models import TOPIC_CHOICES
    categories = [c[0] for c in TOPIC_CHOICES]
    all_users = User.objects.all().order_by('username')
    return render(request, 'news/article_form.html', {
        'form': form, 
        'action': 'Create',
        'categories': categories,
        'all_users': all_users,
    })



@user_passes_test(is_author_or_admin)
def admin_article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user != article.author and request.user.role != 'admin':
        messages.error(request, "You don't have permission to edit this article.")
        return redirect('home')
    
    form = ArticleForm(request.POST or None, request.FILES or None, instance=article)
    if request.method == 'POST' and form.is_valid():
        a = form.save(commit=False)
        
        
        if request.POST.get('clear_image') == '1':
            if a.image:
                a.image.delete(save=False)  
                a.image = None  
        
        if request.POST.get('action') == 'draft':
            a.is_published = False
        else:
            a.is_published = True
            
        a.save()
        log(request.user, f"Edited article '{article.title[:60]}'")
        return redirect('admin_dashboard')
        
    from news.models import TOPIC_CHOICES
    categories = [c[0] for c in TOPIC_CHOICES]
    all_users = User.objects.all().order_by('username')
    return render(request, 'news/article_form.html', {'form': form, 'action':'Edit','article': article,'categories': categories,'all_users': all_users,})



@login_required
@user_passes_test(is_author_or_admin)
def admin_article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    
    
    if request.user.role != 'admin' and article.author != request.user:
        messages.error(request, "You don't have permission to delete this article.")
        return redirect('home')
    
    log(request.user, f"Deleted article '{article.title[:60]}'")
    article.delete()
    
    
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('admin_dashboard')

@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.exclude(pk=request.user.pk).order_by('-date_joined')
    
    
    active_count = User.objects.filter(is_blocked=False, role__in=['user', 'author']).count()
    blocked_count = User.objects.filter(is_blocked=True).count()
    new_this_week = User.objects.filter(
        date_joined__gte=timezone.now()-timedelta(days=7)
    ).count()
    
    context = {
        'users': users,
        'active_count': active_count,
        'blocked_count': blocked_count,
        'new_this_week': new_this_week,
    }
    
    return render(request, 'news/admin_users.html', context)

@user_passes_test(is_admin)
def admin_block_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_blocked = not user.is_blocked
    user.save()
    action = "Blocked" if user.is_blocked else "Unblocked"
    log(request.user, f"{action} user @{user.username}")
    return redirect('admin_users')

@user_passes_test(is_admin)
def admin_delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    log(request.user, f"Admin deleted comment #{pk} by @{comment.author.username}")
    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))



def newsletter_subscribe(request):
    print("📧 === NEWSLETTER FUNCTION CALLED ===")
    print(f"Method: {request.method}")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        print(f"📧 Email received: {email}")
        
        if email:
            try:
                
                if NewsletterSubscriber.objects.filter(email=email).exists():
                    print("⚠️ Already subscribed")
                    from django.contrib import messages
                    messages.info(request, 'You are already subscribed! 📧')
                else:
                    
                    NewsletterSubscriber.objects.create(email=email)
                    print(f"✅ Saved to database: {email}")
                    from django.contrib import messages
                    messages.success(request, 'Successfully subscribed to Daily Briefing! 🎉')
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                from django.contrib import messages
                messages.error(request, f'Error: {str(e)}')
        else:
            print("❌ No email in POST data")
            from django.contrib import messages
            messages.error(request, 'Please enter a valid email address.')
        
        print("📧 Redirecting to home...")
        return redirect('home')
    
    return redirect('home')


def newsletter_unsubscribe(request, token):
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    
    
    target_subscriber = None
    for sub in subscribers:
        if generate_unsubscribe_token(sub.email) == token:
            target_subscriber = sub
            break
    
    if target_subscriber:
        
        target_subscriber.is_active = False
        target_subscriber.save()
        return redirect('unsubscribe_success')
    else:
        
        return render(request, 'news/unsubscribe_invalid.html')

def unsubscribe_success(request):
    """Success page shown after successful unsubscription"""
    return render(request, 'news/unsubscribe_success.html')



@user_passes_test(is_admin)
def admin_preview_newsletter(request):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')[:5]
    subscribers_count = NewsletterSubscriber.objects.filter(is_active=True).count()
    
    return render(request, 'news/preview_newsletter.html', {
        'articles': articles,
        'subscribers_count': subscribers_count
    })

@user_passes_test(is_admin)
def admin_send_newsletter(request):
    articles = Article.objects.filter(is_published=True).order_by('-created_at')[:5]
    subscribers_count = NewsletterSubscriber.objects.filter(is_active=True).count()
    
    if request.method == 'POST':
        try:
            
            from news.utils import send_daily_newsletter as resend_newsletter
            count = resend_newsletter()
            
            if count and count > 0:
                success_msg = f'✅ Done sending all users today\'s updated news! ({count} subscribers)'
                log(request.user, f"Sent newsletter to {count} subscribers")
                
                return render(request, 'news/preview_newsletter.html', {
                    'articles': articles,
                    'subscribers_count': subscribers_count,
                    'success_message': success_msg,
                    'is_sent': True
                })
            else:
                error_msg = '⚠️ No subscribers or no articles to send!'
        except Exception as e:
            error_msg = f'❌ Error sending newsletter: {str(e)}'
            print(f"Newsletter error: {e}")
        
        return render(request, 'news/preview_newsletter.html', {
            'articles': articles,
            'subscribers_count': subscribers_count,
            'error_message': error_msg
        })
    
    return redirect('admin_dashboard')


@login_required
def my_profile(request):
    user = request.user
    
    can_change_name = True
    if user.role == 'admin' and user.last_name_change:
        if user.last_name_change > timezone.now() - timedelta(days=180):
            can_change_name = False

    if request.method == 'POST':
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        if 'social_link' in request.POST:
            user.social_link = request.POST['social_link']
        
        if 'first_name' in request.POST and can_change_name:
            user.first_name = request.POST['first_name']
            user.last_name_change = timezone.now() 
        
        user.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated!',
                'new_image_url': user.profile_picture.url if user.profile_picture else None,
                'cache_buster': int(time.time())
            })

        messages.success(request, "Profile successfully updated!")
        return redirect('my_profile')


    context = {
        'user': user,
        'can_change_name': can_change_name,
        'my_comments': Comment.objects.filter(author=user).select_related('article').order_by('-created_at')[:10],
        'liked_articles': Article.objects.filter(likes=user).order_by('-created_at')[:10],
        'cache_buster': int(time.time()),
    }
    

    if user.role == 'admin':
        context['published_articles'] = Article.objects.filter(author=user).order_by('-created_at')
        
    return render(request, 'news/my_profile.html', context)

def author_profile(request, username):
    author = get_object_or_404(User, username=username)
    published_articles = Article.objects.filter(author=author, is_published=True).order_by('-created_at')
    return render(request, 'news/author_profile.html', {
        'author': author, 
        'published_articles': published_articles
    })


@user_passes_test(is_admin)
def admin_make_author(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user.role == 'user':
        target_user.role = 'author'
        target_user.save()
        log(request.user, f"Promoted @{target_user.username} to Author")
        messages.success(request, f"@{target_user.username} is now an Author! ✍️")
    else:
        messages.info(request, f"@{target_user.username} is already an Author or Admin.")
    return redirect('admin_users')

@user_passes_test(is_admin)
def admin_demote_author(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user.role == 'author':
        target_user.role = 'user'
        target_user.save()
        log(request.user, f"Demoted @{target_user.username} from Author to User")
        messages.success(request, f"@{target_user.username} is now a regular User.")
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Role', 'Status', 'Joined Date'])
    
    for u in User.objects.exclude(role='admin').order_by('-date_joined'):
        status = 'Blocked' if u.is_blocked else 'Active'
        writer.writerow([u.username, u.email, u.role.upper(), status, u.date_joined.strftime('%Y-%m-%d')])
    return response

@user_passes_test(is_admin)
def export_articles_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="articles_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Author', 'Category', 'Views', 'Likes', 'Published'])
    
    for a in Article.objects.all().order_by('-created_at'):
        writer.writerow([a.title, a.author.username if a.author else '-', a.category, a.views, a.likes.count(), a.is_published])
    return response

@user_passes_test(is_admin)
def export_comments_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comments_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['User', 'Article', 'Comment', 'Date'])
    
    for c in Comment.objects.all().order_by('-created_at'):
        writer.writerow([c.author.username, c.article.title, c.text[:50], c.created_at.strftime('%Y-%m-%d')])
        
    return response

@user_passes_test(is_admin)
def export_platform_summary_csv(request):
    from django.db.models import Count, Max
    from datetime import timedelta
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="platform_summary.csv"'
    
    writer = csv.writer(response)
    
    
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(is_published=True).count()
    draft_articles = Article.objects.filter(is_published=False).count()
    total_users = User.objects.exclude(role='admin').count()
    active_users = User.objects.filter(is_blocked=False).exclude(role='admin').count()
    blocked_users = User.objects.filter(is_blocked=True).count()
    total_comments = Comment.objects.count()
    
    
    top_category = Article.objects.values('category').annotate(count=Count('id')).order_by('-count').first()
    top_cat_name = top_category['category'] if top_category else 'N/A'
    top_cat_count = top_category['count'] if top_category else 0
    
    
    most_viewed = Article.objects.order_by('-views').first()
    most_viewed_title = most_viewed.title if most_viewed else 'N/A'
    most_viewed_views = most_viewed.views if most_viewed else 0
    
    
    most_liked = Article.objects.annotate(like_count=Count('likes')).order_by('-like_count').first()
    most_liked_title = most_liked.title if most_liked else 'N/A'
    most_liked_count = most_liked.like_count if most_liked else 0
    
    
    new_users_week = User.objects.filter(date_joined__gte=timezone.now()-timedelta(days=7)).count()
    
    
    writer.writerow(['Platform Summary Report'])
    writer.writerow(['Generated On', timezone.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Articles', total_articles])
    writer.writerow(['Published Articles', published_articles])
    writer.writerow(['Draft Articles', draft_articles])
    writer.writerow(['Total Users', total_users])
    writer.writerow(['Active Users', active_users])
    writer.writerow(['Blocked Users', blocked_users])
    writer.writerow(['New Users (This Week)', new_users_week])
    writer.writerow(['Total Comments', total_comments])
    writer.writerow([])
    
    writer.writerow(['Top Performing Metrics'])
    writer.writerow(['Top Category', f"{top_cat_name} ({top_cat_count} articles)"])
    writer.writerow(['Most Viewed Article', f"{most_viewed_title} ({most_viewed_views} views)"])
    writer.writerow(['Most Liked Article', f"{most_liked_title} ({most_liked_count} likes)"])
    
    return response


def user_profile(request, user_id):
    """Universal profile page with role-based restrictions"""
    profile_user = get_object_or_404(User, id=user_id)
    articles = Article.objects.filter(author=profile_user, is_published=True).order_by('-created_at')
    is_admin = request.user.is_authenticated and request.user.role == 'admin'
    is_author_viewing_own = request.user.is_authenticated and request.user.id == profile_user.id and request.user.role == 'author'
    if is_admin or is_author_viewing_own:
        
        comments = Comment.objects.filter(author=profile_user, is_deleted=False).select_related('article').order_by('-created_at')[:20]
        liked_articles = Article.objects.filter(likes=profile_user, is_published=True).order_by('-created_at')[:20]
    else:
        
        comments = []
        liked_articles = []
    context = {
        'profile_user': profile_user,
        'articles': articles,
        'comments': comments,
        'liked_articles': liked_articles,
        'is_admin': is_admin,
        'is_own_profile': request.user.is_authenticated and request.user.id == profile_user.id,
    }
    
    return render(request, 'news/user_profile.html', context)

@user_passes_test(is_admin)
def admin_warn_content(request, content_type, pk):
    """Admin sends a warning to a user for a specific article or comment."""
    if request.method == 'POST':
        if content_type == 'article':
            content = get_object_or_404(Article, pk=pk)
            target_user = content.author
            log(request.user, f"Warned user @{target_user.username} regarding article: '{content.title[:50]}'")
            messages.warning(request, f"Warning sent to @{target_user.username} about their article.")
        elif content_type == 'comment':
            content = get_object_or_404(Comment, pk=pk)
            target_user = content.author
            log(request.user, f"Warned user @{target_user.username} regarding a comment.")
            messages.warning(request, f"Warning sent to @{target_user.username} about their comment.")

        #send warning email with safety net
        try:
            print(f"🚨 DEBUG: Trying to send warn email to -> {target_user.email}")
            if target_user.email:
                subject = "Warning from Admin - The Signal"

                if content_type == 'article':
                    content_info = f"Article: {content.title[:100]}"
                else:
                    content_info = f"Comment: {content.text[:100]}"

                message = f"""Dear {target_user.get_full_name() or target_user.username},

We are writing to inform you that our moderation team has reviewed your recent content and found it requires attention.

Details:
{content_info}

Please review your content and make the necessary adjustments to comply with our community guidelines. If you believe this review was conducted in error, please reach out to our support team.

Thank you for your cooperation.

Best Regards,
The Admin Team
The Signal
"""
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[target_user.email],
                    fail_silently=False,
                )
                messages.success(request, f"Warning email successfully sent to {target_user.email}")
            else:
                messages.warning(request, f"User @{target_user.username} has no email on file. Warning logged only.")

        except Exception as e:
            messages.warning(request, "User has been warned, but the email could not be sent due to a server timeout. Please check manually later.")
            print(f"Warning email error: {e}")

        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')


@user_passes_test(is_admin)
def admin_delete_content(request, content_type, pk):
    """Admin can delete any article or comment"""
    if request.method == 'POST':
        if content_type == 'article':
            content = get_object_or_404(Article, pk=pk)
            target_user = content.author
            log(request.user, f"🗑️ Deleted article '{content.title[:50]}' by @{target_user.username}")
            content.delete()
            messages.success(request, f"Article by @{target_user.username} deleted successfully.")
        elif content_type == 'comment':
            content = get_object_or_404(Comment, pk=pk)
            target_user = content.author
            log(request.user, f"🗑️ Deleted comment by @{target_user.username}")
            content.delete()
            messages.success(request, f"Comment by @{target_user.username} deleted successfully.")
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')

def about_page(request):
    return render(request, 'news/about.html')

def contact_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f"Contact Form: Message from {name}"
            plain_message = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
            html_content = f"""
            <h2>New Contact Form Submission</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
            """
            
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['thesignalset@gmail.com'], 
                html_message=html_content,
                fail_silently=False,
            )
            messages.success(request, f"Thanks {name}! Your message has been sent successfully.")
            return redirect('contact')
            
        except Exception as e:
            messages.error(request, f"Sorry, there was an error sending your message. Please try again later.")
            print(f"Contact form error: {e}")
    
    return render(request, 'news/contact.html')

def privacy_page(request):
    return render(request, 'news/privacy.html')

def terms_page(request):
    return render(request, 'news/terms.html')