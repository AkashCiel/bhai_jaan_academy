import os
from typing import Dict, Any
from config import settings
from config.constants import FEEDBACK_CONFIG

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
        # Generate feedback URLs for fallback template
        discord_feedback_url = FEEDBACK_CONFIG['DISCORD_CHANNEL_URL']
        email_feedback_url = f"mailto:{FEEDBACK_CONFIG['FEEDBACK_EMAIL']}?subject={FEEDBACK_CONFIG['FEEDBACK_EMAIL_SUBJECT'].replace(' ', '%20')}"
        
        # Use discord_link_html from variables if provided, otherwise compute it
        discord_link_html = variables.get('discord_link_html', '')
        if not discord_link_html:
            show_discord_links = FEEDBACK_CONFIG.get('SHOW_DISCORD_LINKS', False)
            discord_link_html = f'<a href="{discord_feedback_url}" style="display: inline-block; padding: 12px 24px; background-color: #5865F2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: background-color 0.3s;">Join our Discord Community</a>' if show_discord_links else ''
        
        return f"""
        <html>
        <body>
            <h2>Welcome to Bhai Jaan Academy! 🎓</h2>
            <p>Thank you for signing up to learn about <strong>{variables.get('topic', '')}</strong>!</p>
            <p>We're excited to help you master this topic in just 30 days.</p>
            <p>Your personalized learning plan is ready. <a href='{variables.get('plan_url', '')}'>Click here to view your plan</a>.</p>
            <p><em>The reports and links can take some time to be active, just try again in a few minutes :)</em></p>
            <br>
            <p>Remember, Rome wasn't built in a day!</p>
            <p>— The Bhai Jaan Academy Team</p>
            <br>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="color: #374151; margin-bottom: 15px;">Have feedback? We'd love to hear from you!</h3>
                <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                    {discord_link_html}
                    <a href="{email_feedback_url}" style="display: inline-block; padding: 12px 24px; background-color: #10B981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: background-color 0.3s;">Send us an Email</a>
                </div>
            </div>
        </body>
        </html>
        """
    elif template_name == 'report':
        # Generate feedback URLs for fallback template
        discord_feedback_url = FEEDBACK_CONFIG['DISCORD_CHANNEL_URL']
        email_feedback_url = f"mailto:{FEEDBACK_CONFIG['FEEDBACK_EMAIL']}?subject={FEEDBACK_CONFIG['FEEDBACK_EMAIL_SUBJECT'].replace(' ', '%20')}"
        
        # Use discord_link_html from variables if provided, otherwise compute it
        discord_link_html = variables.get('discord_link_html', '')
        if not discord_link_html:
            show_discord_links = FEEDBACK_CONFIG.get('SHOW_DISCORD_LINKS', False)
            discord_link_html = f'<a href="{discord_feedback_url}" style="display: inline-block; padding: 12px 24px; background-color: #5865F2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: background-color 0.3s;">Join our Discord Community</a>' if show_discord_links else ''
        
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
            <p><em>The reports and links can take some time to be active, just try again in a few minutes :)</em></p>
            <br>
            <p>Keep up the great work!</p>
            <p>— The Bhai Jaan Academy Team</p>
            <br>
            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="color: #374151; margin-bottom: 15px;">Have feedback? We'd love to hear from you!</h3>
                <div style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                    {discord_link_html}
                    <a href="{email_feedback_url}" style="display: inline-block; padding: 12px 24px; background-color: #10B981; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: background-color 0.3s;">Send us an Email</a>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        raise ValueError(f"Unknown template: {template_name}") 