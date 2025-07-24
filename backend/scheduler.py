import os
import openai
from report_scheduler_utils import load_users, save_users, process_user

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")

client = openai.OpenAI(api_key=OPENAI_API_KEY, timeout=120.0)

def main():
    users = load_users(USERS_FILE)
    updated_users = []
    for user in users:
        updated_user = process_user(user, client, MAILGUN_API_KEY, MAILGUN_DOMAIN, USERS_FILE)
        updated_users.append(updated_user)
    save_users(updated_users, USERS_FILE)
    print("[Scheduler] All users processed.")

if __name__ == "__main__":
    main() 