import requests
from typing import Dict, Any
from config import settings
from config.constants import FEEDBACK_CONFIG
from utils.email_utils import load_email_template

class EmailService:
    def __init__(self):
        self.mailgun_api_key = settings.MAILGUN_API_KEY
        self.mailgun_domain = settings.MAILGUN_DOMAIN
    
    def is_email_configured(self) -> bool:
        """Check if email service is configured"""
        return bool(self.mailgun_api_key and self.mailgun_domain)
    
    def send_welcome_email(self, email: str, topic: str, plan_url: str) -> bool:
        """Send welcome email with learning plan"""
        if not self.is_email_configured():
            print(f"[Email Service] Email service not configured. Skipping welcome email for {email}")
            return False
        
        # Generate feedback URLs
        discord_feedback_url = FEEDBACK_CONFIG['DISCORD_CHANNEL_URL']
        email_feedback_url = f"mailto:{FEEDBACK_CONFIG['FEEDBACK_EMAIL']}?subject={FEEDBACK_CONFIG['FEEDBACK_EMAIL_SUBJECT'].replace(' ', '%20')}"
        
        subject = f"Your 30-Day Learning Plan for {topic} - Bhai Jaan Academy"
        html_email_content = load_email_template('welcome', {
            'topic': topic,
            'plan_url': plan_url,
            'discord_feedback_url': discord_feedback_url,
            'email_feedback_url': email_feedback_url
        })
        
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"Bhai Jaan Academy <mailgun@{self.mailgun_domain}>",
                    "to": [email],
                    "subject": subject,
                    "html": html_email_content
                }
            )
            
            print(f"[Email Service] Welcome email sent to {email}: {response.status_code}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"[Email Service] Error sending welcome email to {email}: {e}")
            return False
    
    def send_report_email(self, user: Dict[str, Any], topic: str, plan_url: str, report_url: str) -> bool:
        """Send report notification email"""
        if not self.is_email_configured():
            print(f"[Email Service] Email service not configured. Skipping report email for {user['email']}")
            return False
        
        # Generate feedback URLs
        discord_feedback_url = FEEDBACK_CONFIG['DISCORD_CHANNEL_URL']
        email_feedback_url = f"mailto:{FEEDBACK_CONFIG['FEEDBACK_EMAIL']}?subject={FEEDBACK_CONFIG['FEEDBACK_EMAIL_SUBJECT'].replace(' ', '%20')}"
        
        subject = f"Your new learning report on {topic} is ready! - Bhai Jaan Academy"
        html_email_content = load_email_template('report', {
            'email': user['email'],
            'topic': topic,
            'plan_url': plan_url,
            'report_url': report_url,
            'discord_feedback_url': discord_feedback_url,
            'email_feedback_url': email_feedback_url
        })
        
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": f"Bhai Jaan Academy <mailgun@{self.mailgun_domain}>",
                    "to": [user["email"]],
                    "subject": subject,
                    "html": html_email_content
                }
            )
            
            print(f"[Email Service] Report email sent to {user['email']}: {response.status_code}")
            return response.status_code == 200
            
        except Exception as e:
            print(f"[Email Service] Error sending report email to {user['email']}: {e}")
            return False 