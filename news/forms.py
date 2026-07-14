import os
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Article, Comment, NewsletterSubscriber


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username').strip().lower()
        reserved_names = ['admin', 'administrator', 'support', 'moderator', 'thesignal', 'staff']
        if username in reserved_names:
            raise ValidationError("This username is reserved and cannot be used.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters long.")
        if len(username) > 30:
            raise ValidationError("Username is too long. Maximum 30 characters allowed.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered. Please use a different one or login.")
        return email


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'excerpt', 'body', 'category', 'tag', 'image', 'read_time', 'is_published')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 8}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file is too large. Maximum allowed size is 5MB.')

            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image.content_type not in allowed_types:
                raise ValidationError('Only JPG, PNG, GIF, and WebP images are allowed.')

            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError('Invalid file extension. Only .jpg, .jpeg, .png, .gif, .webp are allowed.')

        return image


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Share your thoughts… (min 10 characters)'
            })
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 1:
            raise ValidationError("Comment is too short. Please write at least 10 characters.")
        if len(text) > 2000:
            raise ValidationError("Comment is too long. Maximum 2000 characters allowed.")
        return text


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'your@email.com',
                'class': 'form-input',
                'required': True
            })
        }