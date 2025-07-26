import os
import openai
from report_scheduler_utils import load_users, save_users, process_user
from config import settings

USERS_FILE = os.path.join(os.path.dirname(__file__), settings.USERS_FILE)
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, timeout=settings.OPENAI_TIMEOUT)

def main():
    users = load_users(USERS_FILE)
    updated_users = []
    for user in users:
        updated_user = process_user(user, client, settings.MAILGUN_API_KEY, settings.MAILGUN_DOMAIN, USERS_FILE)
        updated_users.append(updated_user)
    save_users(updated_users, USERS_FILE)
    print("[Scheduler] All users processed.")

if __name__ == "__main__":
    main() 