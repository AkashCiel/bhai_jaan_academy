from .user_repository import UserRepository
from .response_repository import ResponseRepository
from .report_repository import ReportRepository
from .context_repository import ContextRepository

# Global repository instances
user_repository = UserRepository()
response_repository = ResponseRepository()
report_repository = ReportRepository()
context_repository = ContextRepository()

__all__ = ['user_repository', 'response_repository', 'report_repository', 'context_repository'] 