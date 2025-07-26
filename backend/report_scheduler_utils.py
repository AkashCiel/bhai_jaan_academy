from services import user_service, report_service, email_service


def process_user(user):
    """Process a single user for report generation"""
    return report_service.generate_next_report(user) 