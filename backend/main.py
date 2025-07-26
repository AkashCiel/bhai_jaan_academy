# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import os
import openai
import json
import re
from html_generation import generate_learning_plan_html, update_learning_plan_html, generate_topic_report_html
from report_uploads.github_report_uploader import upload_report
from response_storage import save_ai_response
import hashlib
import time
import datetime
import markdown
from report_scheduler_utils import load_users, save_users, is_same_utc_day, get_next_report_topic, generate_report_content, send_report_email, process_user
from config import settings
from utils.email_utils import load_email_template
from services import user_service, report_service, email_service

# Configure OpenAI client for v1.x (keeping for backward compatibility)
client = openai.OpenAI(
    api_key=settings.OPENAI_API_KEY,
    timeout=settings.OPENAI_TIMEOUT
)

app = FastAPI(title="Bhai Jaan Academy API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for request validation
class UserSubmission(BaseModel):
    email: EmailStr
    topic: str

def sanitize_topic(raw_topic: str) -> str:
    # Remove leading/trailing whitespace
    topic = raw_topic.strip()
    # Remove any HTML tags
    topic = re.sub(r'<[^>]+>', '', topic)
    # Remove dangerous/special characters except basic punctuation
    topic = re.sub(r'[^a-zA-Z0-9\s\-\_\.\,\(\)\[\]\:]', '', topic)
    # Collapse multiple spaces
    topic = re.sub(r'\s+', ' ', topic)
    # Limit length to 100 characters
    topic = topic[:100]
    # Optionally, normalize case (e.g., title case)
    topic = topic.title()
    return topic

def generate_learning_plan(topic: str) -> str:
    """
    Generate a 30-day learning plan using OpenAI GPT-4
    Returns the plan as a string, or "ERROR" if the topic is invalid
    """
    try:
        prompt = f"""Create a comprehensive 30-day learning plan for {topic}. 

The plan should include:
1. A list of 10 topics for each of the three expertise levels:
   - Beginner (10 topics)
   - Intermediate (10 topics) 
   - Advanced (10 topics)

If the topic is not suitable for learning or is inappropriate, respond with "ERROR"."""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert educational content creator specializing in creating structured learning plans."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=settings.OPENAI_MAX_TOKENS_PLAN,
            temperature=settings.OPENAI_TEMPERATURE
        )
        plan = response.choices[0].message.content.strip()
        print(f"OpenAI API raw response: {plan}")
        # Only treat as error if the response is exactly 'ERROR' or starts with 'ERROR'
        if plan.strip().upper() == "ERROR" or plan.strip().upper().startswith("ERROR"):
            return "ERROR"
        return plan
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"ERROR: {str(e)}"

def extract_topics_from_plan(plan: str) -> list:
    """Extract only the topic titles from the OpenAI learning plan response."""
    topics = []
    for line in plan.splitlines():
        # Match lines like '1. **Topic**' or '1. Topic'
        match = re.match(r'^\s*\d+\.\s+\*?\*?(.+?)\*?\*?\s*$', line)
        if match:
            topic = match.group(1).strip()
            topics.append(topic)
    return topics

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Bhai Jaan Academy API is running"}

@app.post("/submit")
async def submit_user_data(user_data: UserSubmission):
    try:
        print(f"[Submit] Received submission: email={user_data.email}, topic={user_data.topic}")
        
        # Use service layer for all operations
        sanitized_topic = user_service.sanitize_topic(user_data.topic)
        
        # Check for duplicate using service
        existing_user = user_service.find_user_by_email_and_topic(user_data.email, sanitized_topic)
        if existing_user:
            print(f"[Submit] Duplicate found for email={user_data.email}, topic={sanitized_topic}")
            return {
                "success": False,
                "message": "You already have a plan for this topic.",
                "email": user_data.email,
                "topic": sanitized_topic
            }
        
        # Generate initial learning plan using service
        result = report_service.generate_initial_learning_plan(user_data.email, sanitized_topic)
        return result
        
    except Exception as e:
        print(f"[Submit] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error processing submission: {str(e)}",
            "email": user_data.email,
            "topic": user_data.topic
        }
    except Exception as e:
        print(f"[Submit] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# --- Scheduler logic (refactored for reuse) ---
# def save_users(users):
#     with open(USERS_FILE, "w") as f:
#         json.dump(users, f, indent=2)

# def is_same_utc_day(dt1, dt2):
#     return dt1.date() == dt2.date()

# def get_next_report_topic(user):
#     idx = user.get("current_index", 0)
#     topics = user.get("learning_plan", [])
#     if idx < len(topics):
#         return idx, topics[idx]
#     return None, None

# def generate_report_content(topic):
#     prompt = f"""Write a comprehensive, beginner-friendly educational report on the topic: \"{topic}\".\nThe report should include:\n- An introduction to the topic\n- Key concepts and definitions\n- Real-world applications or examples\n- Common misconceptions or pitfalls\n- Further reading/resources (if appropriate)\nThe tone should be clear, engaging, and accessible to someone new to the subject."""
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are an expert educator and science communicator."},
#             {"role": "user", "content": prompt}
#         ],
#         max_tokens=1800,
#         temperature=0.7
#     )
#     return response.choices[0].message.content.strip()

# def send_report_email(user, plan_url, report_url, topic):
#     mailgun_api_key = os.getenv("MAILGUN_API_KEY")
#     mailgun_domain = os.getenv("MAILGUN_DOMAIN")
#     if not mailgun_api_key or not mailgun_domain:
#         print(f"[Scheduler] Email service not configured. Skipping email for {user['email']}")
#         return
#     subject = f"Your new learning report on {topic} is ready! - Bhai Jaan Academy"
#     html_email_content = f"""
#     <html>
#     <body>
#         <h2>Your new report is ready! 🎓</h2>
#         <p>Hi {user['email']},</p>
#         <p>Your next learning report on <strong>{topic}</strong> is now available.</p>
#         <ul>
#             <li><a href='{plan_url}'>View your full learning plan</a></li>
#             <li><a href='{report_url}'>Read your new report: {topic}</a></li>
#         </ul>
#         <br>
#         <p>Keep up the great work!</p>
#         <p>— The Bhai Jaan Academy Team</p>
#     </body>
#     </html>
#     """
#     response = requests.post(
#         f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
#         auth=("api", mailgun_api_key),
#         data={
#             "from": f"Bhai Jaan Academy <mailgun@{mailgun_domain}>",
#             "to": [user["email"]],
#             "subject": subject,
#             "html": html_email_content
#         }
#     )
#     print(f"[Scheduler] Email sent to {user['email']}: {response.status_code}")

# def process_user(user):
#     now = datetime.datetime.now(datetime.timezone.utc)
#     last_report_time = user.get("last_report_time")
#     current_index = user.get("current_index", 0)
#     # If current_index == 1 and last_report_time is today, skip
#     if last_report_time:
#         try:
#             last_dt = datetime.datetime.fromisoformat(last_report_time)
#         except Exception:
#             last_dt = None
#     else:
#         last_dt = None
#     if current_index == 1 and last_dt and is_same_utc_day(now, last_dt):
#         print(f"[Scheduler] Skipping {user['email']} (already sent today)")
#         return user  # No changes
#     idx, topic = get_next_report_topic(user)
#     if topic is None:
#         print(f"[Scheduler] No more topics for {user['email']}")
#         return user
#     print(f"[Scheduler] Generating report for {user['email']} on topic: {topic}")
#     try:
#         report_content_md = generate_report_content(topic)
#         report_content_html = markdown.markdown(report_content_md)
#         report_html = generate_topic_report_html(topic, user["email"], report_content_html)
#         # Upload report
#         plan_topic = user["main_topic"]
#         report_url = upload_report(user["email"], plan_topic, report_html, filename=topic)
#         # Update report_links
#         report_links = user.get("report_links", {})
#         report_links[str(idx)] = report_url
#         # Update learning plan HTML
#         updated_plan_html = update_learning_plan_html(
#             topic=plan_topic,
#             user_email=user["email"],
#             topics=user["learning_plan"],
#             report_links=report_links
#         )
#         plan_url = upload_report(user["email"], plan_topic, updated_plan_html)
#         # Update user progress
#         user["current_index"] = current_index + 1
#         user["last_report_time"] = now.isoformat()
#         user["plan_url"] = plan_url
#         user["report_links"] = report_links
#         # Send email
#         send_report_email(user, plan_url, report_url, topic)
#         print(f"[Scheduler] Report and email sent for {user['email']} on topic: {topic}")
#     except Exception as e:
#         print(f"[Scheduler] Error for {user['email']} on topic {topic}: {e}")
#         import traceback
#         traceback.print_exc()
#     return user

# --- API endpoint for scheduler trigger ---
from fastapi.responses import JSONResponse
@app.post("/run-scheduler")
async def run_scheduler(request: Request):
    try:
        # Use service layer for scheduler operations
        users = user_service.load_users()
        updated_users = []
        
        # Process each user using service
        for user in users:
            updated_user = report_service.generate_next_report(user)
            updated_users.append(updated_user)
        
        # Save updated users using service
        user_service.save_users(updated_users)
        
        return {"status": "ok", "message": "Scheduler run complete.", "users_processed": len(users)}
    except Exception as e:
        print(f"Error in scheduler: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 