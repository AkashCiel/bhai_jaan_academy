from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import os
from dotenv import load_dotenv
import openai
import json
import re

# Load environment variables
load_dotenv()

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

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Bhai Jaan Academy API is running"}

@app.post("/submit")
async def submit_user_data(user_data: UserSubmission):
    """Submit user email and topic, generate AI learning plan, and send email via Mailgun"""
    try:
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
                return {
                    "success": False,
                    "message": "You already have a plan for this topic.",
                    "email": user_data.email,
                    "topic": sanitized_topic
                }
        # Generate AI learning plan
        learning_plan = generate_learning_plan(sanitized_topic)
        
        if learning_plan == "ERROR":
            return {
                "success": False,
                "message": "Sorry, this topic is not suitable for learning or may be inappropriate. Please try a different topic.",
                "email": user_data.email,
                "topic": sanitized_topic
            }
        
        # Get Mailgun configuration from environment
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        
        if not mailgun_api_key or not mailgun_domain:
            # For development, just log the submission and plan
            print(f"User submitted - Email: {user_data.email}, Topic: {user_data.topic}")
            print(f"Generated learning plan preview: {learning_plan[:200]}...")
            return {
                "success": True,
                "message": "Submission received and learning plan generated! (Email service not configured)",
                "email": user_data.email,
                "topic": sanitized_topic,
                "plan_preview": learning_plan[:500] + "..." if len(learning_plan) > 500 else learning_plan
            }
        
        # Create email content with the learning plan
        subject = f"Your 30-Day Learning Plan for {sanitized_topic} - Bhai Jaan Academy"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Bhai Jaan Academy! 🎓</h2>
            <p>Thank you for signing up to learn about <strong>{sanitized_topic}</strong>!</p>
            <p>We're excited to help you master this topic in just 30 days.</p>
            <br>
            <h3>Your Personalized 30-Day Learning Plan</h3>
            <div style="white-space: pre-wrap; font-family: Arial, sans-serif; line-height: 1.6;">
            {learning_plan}
            </div>
            <br>
            <p>You'll receive daily emails with detailed lessons and progress tracking.</p>
            <p>Best regards,</p>
            <p>The Bhai Jaan Academy Team</p>
        </body>
        </html>
        """
        
        # Send email using Mailgun
        mailgun_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"
        
        data = {
            'from': f'Bhai Jaan Academy <noreply@{mailgun_domain}>',
            'to': user_data.email,
            'subject': subject,
            'html': html_content
        }
        
        response = requests.post(
            mailgun_url,
            auth=("api", mailgun_api_key),
            data=data
        )
        
        if response.status_code == 200:
            # Add new user entry
            user_entry = {
                "email": user_data.email,
                "main_topic": sanitized_topic,
                "learning_plan": [t.strip() for t in learning_plan.split("\n") if t.strip()],
                "current_index": 0
            }
            users.append(user_entry)
            with open(users_file, "w") as f:
                json.dump(users, f, indent=2)
            return {
                "success": True,
                "message": "Welcome email with learning plan sent successfully!",
                "email": user_data.email,
                "topic": sanitized_topic,
                "plan_preview": learning_plan[:200] + "..." if len(learning_plan) > 200 else learning_plan
            }
        else:
            print(f"Mailgun error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Failed to send email")
            
    except Exception as e:
        print(f"Error processing submission: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 