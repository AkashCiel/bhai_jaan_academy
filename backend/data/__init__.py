from .user_repository import UserRepository
from .response_repository import ResponseRepository
from .report_repository import ReportRepository

# Global repository instances
user_repository = UserRepository()
response_repository = ResponseRepository()
report_repository = ReportRepository()

__all__ = ['user_repository', 'response_repository', 'report_repository'] 