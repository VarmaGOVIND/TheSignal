from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from cloudinary.models import CloudinaryField

TOPIC_CHOICES = [
    ('Politics','Politics'), ('Technology','Technology'), ('Science','Science'),
    ('Markets','Markets'), ('World','World'), ('Culture','Culture'),
    ('Sports','Sports'), ('Health','Health'), ('Climate','Climate'),
    ('AI','AI'), ('Space','Space'), ('Business','Business'),
    ('Law','Law'), ('Education','Education'), ('Entertainment','Entertainment'),
    ('Travel','Travel'), ('Food','Food'), ('Automotive','Automotive'),
    ('Defense','Defense'),
]
TAG_CHOICES = [('','None'),('BREAKING','Breaking'),('EXCLUSIVE','Exclusive'),('LIVE','Live')]

class User(AbstractUser):
    """Extended user with role and block support."""
    ROLE_CHOICES = [('user','User'), ('author','Author'), ('admin','Admin')]
    role      = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    
    bio       = models.TextField(blank=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = CloudinaryField('image', folder='avatars/', blank=True, null=True)
    profile_picture = CloudinaryField('image', folder='profile_pics/', blank=True, null=True)
    social_link = models.URLField(blank=True, null=True, help_text="Enter Your social media link ")
    last_name_change = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin_role(self):
        return self.role == 'admin'


class Article(models.Model):
    """News article with category, image, author, tags."""
    title      = models.CharField(max_length=300)
    excerpt    = models.TextField()
    body       = models.TextField()
    category   = models.CharField(max_length=30, choices=TOPIC_CHOICES, default='World')
    tag        = models.CharField(max_length=20, choices=TAG_CHOICES, blank=True)
    author     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    image = CloudinaryField('image', folder='articles/', blank=True, null=True)
    likes      = models.ManyToManyField(User, blank=True, related_name='liked_articles')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_time  = models.CharField(max_length=20, default='5 min')
    views      = models.PositiveIntegerField(default=0)
    dark_mode = models.BooleanField(default=False, help_text="Article stays dark in light mode")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.filter(parent__isnull=True).count()


class Comment(models.Model):
    """Threaded comments: top-level + one level of replies."""
    article  = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent   = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    text     = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"@{self.author.username} on '{self.article.title[:40]}'"


class UserActivity(models.Model):
    """Simple audit log for admin."""
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    action  = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)



class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class BreakingNews(models.Model):
    text = models.CharField(max_length=200, help_text="Breaking news text (Max 200 characters)")
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='breaking_news_items',
        help_text="Optional: If want to link any article Then Select Kisi "
    )
    external_url = models.URLField(
        null=True, 
        blank=True, 
        help_text="Optional: Outsider link  (e.g., BBC, Reuters)"
    )
    is_active = models.BooleanField(default=True, help_text="Want to show in Ticker or not ")
    order = models.IntegerField(default=0, help_text="Priority (0 top )")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Breaking News"
        ordering = ['-order', '-created_at']

    def __str__(self):
        return self.text[:50]

