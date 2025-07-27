from .ai_service import AIService
from .user_service import UserService
from .email_service import EmailService
from .report_service import ReportService
from .github_sync_service import GitHubSyncService

# Global service instances
ai_service = AIService()
user_service = UserService()
email_service = EmailService()
report_service = ReportService()
github_sync_service = GitHubSyncService()

__all__ = ['ai_service', 'user_service', 'email_service', 'report_service', 'github_sync_service'] 