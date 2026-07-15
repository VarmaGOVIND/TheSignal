import requests
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

class BrevoAPIEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        
        api_key = getattr(settings, 'BREVO_API_KEY', '')
        if not api_key:
            print("❌ BREVO_API_KEY missing!")
            return 0
            
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }
        
        num_sent = 0
        for message in email_messages:
            text_content = message.body
            html_content = ""
            
            if hasattr(message, 'alternatives') and message.alternatives:
                for content, mimetype in message.alternatives:
                    if mimetype == 'text/html':
                        html_content = content
                        break
            
            if not html_content:
                html_content = f"<p>{text_content}</p>".replace('\n', '<br>')

            payload = {
                "sender": {"email": message.from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'thesignalset@gmail.com')},
                "to": [{"email": email} for email in message.to],
                "subject": message.subject,
                "textContent": text_content,
                "htmlContent": html_content
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code in [200, 201, 202, 204]:
                    num_sent += 1
                else:
                    print(f"❌ Brevo API Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Brevo API Exception: {e}")
                
        return num_sent