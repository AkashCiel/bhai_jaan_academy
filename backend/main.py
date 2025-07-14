from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Bhai Jaan Academy API is running"}

@app.post("/submit")
async def submit_user_data(user_data: UserSubmission):
    """Submit user email and topic, send email via Mailgun"""
    try:
        # Get Mailgun configuration from environment
        mailgun_api_key = os.getenv("MAILGUN_API_KEY")
        mailgun_domain = os.getenv("MAILGUN_DOMAIN")
        
        if not mailgun_api_key or not mailgun_domain:
            # For development, just log the submission
            print(f"User submitted - Email: {user_data.email}, Topic: {user_data.topic}")
            return {
                "success": True,
                "message": "Submission received! (Email service not configured)",
                "email": user_data.email,
                "topic": user_data.topic
            }
        
        # Create email content
        subject = f"Welcome to Bhai Jaan Academy - {user_data.topic}"
        html_content = f"""
        <html>
        <body>
            <h2>Welcome to Bhai Jaan Academy! 🎓</h2>
            <p>Thank you for signing up to learn about <strong>{user_data.topic}</strong>!</p>
            <p>We're excited to help you master this topic in just 30 days.</p>
            <p>Your personalized learning plan is being prepared and you'll receive your first lesson tomorrow.</p>
            <br>
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
                "message": "Welcome email sent successfully!",
                "email": user_data.email,
                "topic": user_data.topic
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