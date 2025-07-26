import os
import openai

from config import settings
from services import user_service, report_service

def main():
    # Use service layer for scheduler operations
    users = user_service.load_users()
    updated_users = []
    for user in users:
        updated_user = report_service.generate_next_report(user)
        updated_users.append(updated_user)
    user_service.save_users(updated_users)
    print("[Scheduler] All users processed.")

if __name__ == "__main__":
    main() 