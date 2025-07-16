from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import os
from dotenv import load_dotenv
import openai
import json

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

2. A structured 30-day curriculum that progresses from beginner to advanced concepts.

3. Each day should include:
   - Learning objectives
   - Key concepts to focus on
   - Recommended resources or activities
   - Practice exercises or assignments

4. The plan should be practical, actionable, and suitable for self-paced learning.

Format the response as a well-structured learning plan that can be easily understood and followed.

If the topic is not suitable for learning or is inappropriate, respond with exactly "ERROR"."""

        response = client.chat.completions.create(
            model="gpt-4",
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
        # Generate AI learning plan
        learning_plan = generate_learning_plan(user_data.topic)
        
        if learning_plan == "ERROR":
            return {
                "success": False,
                "message": "Sorry, this topic is not suitable for learning or may be inappropriate. Please try a different topic.",
                "email": user_data.email,
                "topic": user_data.topic
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
                "topic": user_data.topic,
                "plan_preview": learning_plan[:500] + "..." if len(learning_plan) > 500 else learning_plan
            }
        
        # Create email content with the learning plan
        subject = f"Your 30-Day Learning Plan for {user_data.topic} - Bhai Jaan Academy"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Bhai Jaan Academy! 🎓</h2>
            <p>Thank you for signing up to learn about <strong>{user_data.topic}</strong>!</p>
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
            return {
                "success": True,
                "message": "Welcome email with learning plan sent successfully!",
                "email": user_data.email,
                "topic": user_data.topic,
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