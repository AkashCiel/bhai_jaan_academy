from typing import List
from system_status_reports.message_builder import MessageBuilder
from services.discord_service import DiscordService
from config import settings

class NotificationService:
    def __init__(self):
        self.discord = DiscordService(settings.DISCORD_WEBHOOK_URL) if settings.DISCORD_WEBHOOK_URL else None
    
    def send_daily_report(self, users_processed: int, success_count: int, errors: List[str]) -> None:
        """Send daily scheduled run report"""
        if not self.discord:
            print("[Notification] Discord webhook not configured, skipping daily report")
            return
        
        message = MessageBuilder.build_daily_report(users_processed, success_count, errors)
        self.discord.send_embed(**message)
    
    def send_error_alert(self, error_type: str, details: str) -> None:
        """Send critical error alert"""
        if not self.discord:
            print("[Notification] Discord webhook not configured, skipping error alert")
            return
        
        message = MessageBuilder.build_error_alert(error_type, details)
        self.discord.send_embed(**message)
