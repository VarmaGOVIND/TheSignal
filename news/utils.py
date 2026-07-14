import hashlib
from django.core.mail import send_mail
from django.conf import settings
from news.models import NewsletterSubscriber, Article

def generate_unsubscribe_token(email):
    """Email se unique token generate karta hai"""
    secret_key = settings.SECRET_KEY
    return hashlib.sha256(f"{email}{secret_key}".encode()).hexdigest()[:32]

def send_daily_newsletter():
    """Send daily newsletter using Django's send_mail (Brevo SMTP)"""
    
    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    articles = Article.objects.filter(is_published=True).order_by('-created_at')[:5]
    
    if not subscribers.exists() or not articles.exists():
        print("⚠️ No subscribers or articles found")
        return 0
    
    subject = '📧 Daily Briefing - The Signal'
    sent_count = 0
    
    
    html_content = '<div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">'
    html_content += '<h2 style="color: #333; text-align: center;">📰 The Signal - Daily Briefing</h2>'
    html_content += '<p style="color: #666;">Good Morning! Here are today\'s top stories:</p><hr>'
    
    for i, article in enumerate(articles, 1):
        html_content += f'''
        <div style="margin-bottom: 20px;">
            <h3 style="color: #0056b3; margin-bottom: 5px;">{i}. {article.title}</h3>
            <p style="color: #555; font-size: 14px;">{article.excerpt}</p>
            <a href="https://thesignal-2pdo.onrender.com/article/{article.pk}/" style="color: #0056b3; text-decoration: none; font-weight: bold;">Read More →</a>
        </div>
        <hr style="border: 0; border-top: 1px solid #eee;">
        '''
    
    html_content += '<p style="text-align: center; font-size: 12px; color: #999;"><em>The Signal - No noise, just signal.</em></p></div>'
    
    for subscriber in subscribers:
        token = generate_unsubscribe_token(subscriber.email)
        unsubscribe_url = f"https://thesignal-2pdo.onrender.com/newsletter/unsubscribe/{token}/"
        
        final_html = html_content + f'<div style="text-align: center; margin-top: 20px; font-size: 12px;"><a href="{unsubscribe_url}" style="color: #999;">Unsubscribe</a></div>'
        
        plain_message = f"The Signal - Daily Briefing\n\n"
        for i, article in enumerate(articles, 1):
            plain_message += f"{i}. {article.title}\n{article.excerpt}\nRead more: https://thesignal-2pdo.onrender.com/article/{article.pk}/\n\n"
        plain_message += f"Unsubscribe: {unsubscribe_url}"
        
        try:
            print(f"📤 Sending email to {subscriber.email} via Brevo SMTP...")
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                html_message=final_html,
                fail_silently=False,
            )
            sent_count += 1
            print(f"✅ Email sent successfully to {subscriber.email}")
        except Exception as e:
            print(f"❌ Error sending to {subscriber.email}: {e}")
    
    print(f"🎉 Total emails sent: {sent_count}")
    return sent_count