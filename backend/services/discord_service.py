import requests
from typing import Dict, Optional, List
from datetime import datetime

class DiscordService:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_message(self, content: str) -> bool:
        """Send simple text message to Discord"""
        try:
            payload = {"content": content}
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code in [200, 204]:
                print(f"[Discord] Successfully sent message: {content[:50]}...")
                return True
            else:
                print(f"[Discord] Error sending message: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[Discord] Exception sending message: {e}")
            return False
    
    def send_embed(self, title: str, description: str, color: int = 0x00ff00, fields: List[Dict] = None) -> bool:
        """Send rich embed message to Discord"""
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.now().isoformat()
            }
            
            if fields:
                embed["fields"] = fields
            
            payload = {"embeds": [embed]}
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                print(f"[Discord] Successfully sent embed: {title}")
                return True
            else:
                print(f"[Discord] Error sending embed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"[Discord] Exception sending embed: {e}")
            return False
