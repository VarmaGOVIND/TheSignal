import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TheSignal.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()


if not User.objects.filter(username='govind').exists():
    try:
        User.objects.create_superuser(
            username='govind',
            email='govindvarmasets@gmail.com',
            password='Govind@2026'
        )
        print("✅ Govind (Admin) created successfully!")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
else:
    print("⚠️ Admin already exists!")