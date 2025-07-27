import os
from typing import Dict, Any
from config import settings

def load_email_template(template_name: str, variables: Dict[str, Any]) -> str:
    """
    Load and render email template with variables.
    
    Args:
        template_name: Name of the template (e.g., 'welcome', 'report')
        variables: Dictionary of variables to substitute
    
    Returns:
        Rendered HTML email content
    """
    template_path = getattr(settings, f"{template_name.upper()}_EMAIL_TEMPLATE")
    
    if not os.path.exists(template_path):
        # Fallback to hardcoded template if file doesn't exist
        return get_fallback_template(template_name, variables)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Simple variable substitution
    for key, value in variables.items():
        template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
    
    return template_content

def get_fallback_template(template_name: str, variables: Dict[str, Any]) -> str:
    """Fallback templates if files don't exist."""
    if template_name == 'welcome':
        return f"""
        <html>
        <body>
            <h2>Welcome to Bhai Jaan Academy! 🎓</h2>
            <p>Thank you for signing up to learn about <strong>{variables.get('topic', '')}</strong>!</p>
            <p>We're excited to help you master this topic in just 30 days.</p>
            <p>Your personalized learning plan is ready. <a href='{variables.get('plan_url', '')}'>Click here to view your plan</a>.</p>
            <p><em>If you cannot find the page, please come back in a few minutes.</em></p>
            <br>
            <p>Remember, Rome wasn't built in a day!</p>
            <p>— The Bhai Jaan Academy Team</p>
        </body>
        </html>
        """
    elif template_name == 'report':
        return f"""
        <html>
        <body>
            <h2>Your new report is ready! 🎓</h2>
            <p>Hi {variables.get('email', '')},</p>
            <p>Your next learning report on <strong>{variables.get('topic', '')}</strong> is now available.</p>
            <ul>
                <li><a href='{variables.get('plan_url', '')}'>View your full learning plan</a></li>
                <li><a href='{variables.get('report_url', '')}'>Read your new report: {variables.get('topic', '')}</a></li>
            </ul>
            <p><em>If you cannot find the page, please come back in a few minutes.</em></p>
            <br>
            <p>Keep up the great work!</p>
            <p>— The Bhai Jaan Academy Team</p>
        </body>
        </html>
        """
    else:
        raise ValueError(f"Unknown template: {template_name}") 