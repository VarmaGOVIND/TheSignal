from django import template

register = template.Library()

@register.filter(name='cat_color_bg')
def cat_color_bg(value):
    colors = {
        'Technology': 'rgba(0, 123, 255, 0.15)',
        'Sports': 'rgba(40, 167, 69, 0.15)',
        'Politics': 'rgba(220, 53, 69, 0.15)',
        'Entertainment': 'rgba(255, 193, 7, 0.15)',
        'Business': 'rgba(108, 117, 125, 0.15)',
        'Health': 'rgba(23, 162, 184, 0.15)',
        'Science': 'rgba(111, 66, 193, 0.15)',
    }
    
    return colors.get(str(value), 'rgba(255, 255, 255, 0.1)')

@register.filter(name='cat_color')
def cat_color(value):
    colors = {
        'Technology': '#007bff',
        'Sports': '#28a745',
        'Politics': '#dc3545',
        'Entertainment': '#ffc107',
        'Business': '#6c757d',
        'Health': '#17a2b8',
        'Science': '#6f42c1',
    }
    return colors.get(str(value), '#ffffff')

@register.filter(name='make_initials')
def make_initials(value):
    if not value:
        return "?"
    words = str(value).split()
    if len(words) > 1:
        return (words[0][0] + words[1][0]).upper()
    return words[0][0].upper()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def split(value, delimiter):
    if not value:
        return []
    return str(value).split(delimiter)

@register.filter
def default_image(category):
    """Topic ke hisaab se default image return karta hai"""
    CATEGORY_IMAGES = {
        'Politics': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80',
        'Technology': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80',
        'Science': 'https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=800&q=80',
        'Markets': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80',
        'World': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80',
        'Culture': 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=800&q=80',
        'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&q=80',
        'Health': 'https://images.unsplash.com/photo-1505751172876-fa1923c5c528?w=800&q=80',
        'Climate': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80',
        'AI': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80',
        'Space': 'https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80',
        'Business': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&q=80',
                'Law': 'https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=800&q=80',
        'Education': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80',
        'Entertainment': 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=800&q=80',
        'Travel': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800&q=80',
        'Food': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80',
        'Automotive': 'https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?w=800&q=80',
        'Defense': 'https://images.unsplash.com/photo-1542281286-9e0a16bb7366?w=800&q=80',
    }
    return CATEGORY_IMAGES.get(category, 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80')


@register.filter
def is_subscribed(user):
    """Check karta hai ki user subscribed hai ya nahi"""
    if not user.is_authenticated:
        return False
    from news.models import NewsletterSubscriber
    return NewsletterSubscriber.objects.filter(email=user.email, is_active=True).exists()