# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import os
import openai
import json
import re
from html_generation import generate_learning_plan_html, update_learning_plan_html, generate_topic_report_html
from report_uploads.github_report_uploader import upload_report
import hashlib
import time
import datetime
import markdown

# Configure OpenAI client for v1.x
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=120.0  # 2 minutes timeout
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
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert educational content creator specializing in creating structured learning plans."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
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
        sanitized_topic = sanitize_topic(user_data.topic)
        # Load users.json
        import os, json
        users_file = os.path.join(os.path.dirname(__file__), "users.json")
        if os.path.exists(users_file):
            with open(users_file, "r") as f:
                users = json.load(f)
        else:
            users = []
        # Check for duplicate (same email + sanitized topic)
        for user in users:
            if user["email"].lower() == user_data.email.lower() and user["main_topic"] == sanitized_topic:
                print(f"[Submit] Duplicate found for email={user_data.email}, topic={sanitized_topic}")
                return {
                    "success": False,
                    "message": "You already have a plan for this topic.",
                    "email": user_data.email,
                    "topic": sanitized_topic
                }
        # Generate AI learning plan
        print(f"[Submit] Generating learning plan for topic: {sanitized_topic}")
        learning_plan = generate_learning_plan(sanitized_topic)
        print(f"[Submit] Learning plan generated.")
        if learning_plan == "ERROR":
            print(f"[Submit] OpenAI returned ERROR for topic: {sanitized_topic}")
            return {
                "success": False,
                "message": "Sorry, this topic is not suitable for learning or may be inappropriate. Please try a different topic.",
                "email": user_data.email,
                "topic": sanitized_topic
            }
        # Extract only topic titles
        topic_titles = extract_topics_from_plan(learning_plan)
        # Generate the initial learning plan HTML (no report links)
        html_content = generate_learning_plan_html(
            topic=sanitized_topic,
            user_email=user_data.email,
            topics=topic_titles
        )
        # Upload HTML report to GitHub and get public URL
        public_url = upload_report(user_data.email, sanitized_topic, html_content)

        # --- New: Generate and upload first topic report ---
        first_topic = topic_titles[0] if topic_titles else None
        report_links = {}
        last_report_time = None
        if first_topic:
            print(f"[Submit] Generating report for first topic: {first_topic}")
            report_prompt = f"""Write a comprehensive, beginner-friendly educational report on the topic: \"{first_topic}\".\nThe report should include:\n- An introduction to the topic\n- Key concepts and definitions\n- Real-world applications or examples\n- Common misconceptions or pitfalls\n- Further reading/resources (if appropriate)\nThe tone should be clear, engaging, and accessible to someone new to the subject."""
            try:
                report_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert educator and science communicator."},
                        {"role": "user", "content": report_prompt}
                    ],
                    max_tokens=1800,
                    temperature=0.7
                )
                report_content = report_response.choices[0].message.content.strip()
                # Convert markdown to HTML
                report_content_html = markdown.markdown(report_content)
                report_html = generate_topic_report_html(
                    topic=first_topic,
                    user_email=user_data.email,
                    report_content=report_content_html
                )
                # Upload the report HTML
                report_url = upload_report(user_data.email, sanitized_topic + "/" + first_topic, report_html)
                report_links[0] = report_url
                last_report_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
                print(f"[Submit] First topic report uploaded: {report_url}")
            except Exception as e:
                print(f"[Submit] Error generating/uploading first topic report: {e}")
        # --- End new ---

        # Update the learning plan HTML to link the first topic
        updated_html_content = update_learning_plan_html(
            topic=sanitized_topic,
            user_email=user_data.email,
            topics=topic_titles,
            report_links=report_links
        )
        # Upload the updated learning plan HTML (overwrite previous)
        updated_public_url = upload_report(user_data.email, sanitized_topic, updated_html_content)

        # Add new user entry
        user_entry = {
            "email": user_data.email,
            "main_topic": sanitized_topic,
            "learning_plan": topic_titles,
            "current_index": 0,
            "plan_url": updated_public_url,
            "report_links": report_links,  # topic index to report URL
            "last_report_time": last_report_time
        }
        users.append(user_entry)
        with open(users_file, "w") as f:
            json.dump(users, f, indent=2)
        print(f"[Submit] User entry added to users.json.")
        # Delay email to allow GitHub Pages to deploy
        print("[Submit] Waiting 5 minutes before sending email to allow GitHub Pages to deploy...")
        time.sleep(300)
        # Send email with the plan URL
        subject = f"Your 30-Day Learning Plan for {sanitized_topic} - Bhai Jaan Academy"
        html_email_content = f"""
        <html>
        <body>
            <h2>Welcome to Bhai Jaan Academy! 🎓</h2>
            <p>Thank you for signing up to learn about <strong>{sanitized_topic}</strong>!</p>
            <p>We're excited to help you master this topic in just 30 days.</p>
            <p>Your personalized learning plan is ready. <a href='{updated_public_url}'>Click here to view your plan</a>.</p>
            <br>
            <p>remember, Rome wasn't built in a day!</p>
            <p>— The Bhai Jaan Academy Team</p>
        </body>
        </html>
        """
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        if not mailgun_api_key or not mailgun_domain:
            print(f"[Submit] Email service not configured.")
            return {
                "success": True,
                "message": "Submission received and learning plan generated! (Email service not configured)",
                "email": user_data.email,
                "topic": sanitized_topic,
                "plan_url": updated_public_url
            }
        import requests
        print(f"[Submit] Sending email to {user_data.email}")
        response = requests.post(
            f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
            auth=("api", mailgun_api_key),
            data={
                "from": f"Bhai Jaan Academy <mailgun@{mailgun_domain}>",
                "to": [user_data.email],
                "subject": subject,
                "html": html_email_content
            }
        )
        print(f"[Submit] Mailgun response: {response.status_code} {response.text}")
        if response.status_code == 200:
            print(f"[Submit] Email sent successfully.")
            return {
                "success": True,
                "message": "Welcome email with learning plan link sent successfully!",
                "email": user_data.email,
                "topic": sanitized_topic,
                "plan_url": updated_public_url
            }
        else:
            print(f"[Submit] Failed to send email. Plan URL: {updated_public_url}")
            return {
                "success": False,
                "message": f"Failed to send email. Plan URL: {updated_public_url}",
                "email": user_data.email,
                "topic": sanitized_topic,
                "plan_url": updated_public_url
            }
    except Exception as e:
        print(f"[Submit] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 