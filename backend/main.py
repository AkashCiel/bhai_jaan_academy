# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os
from config import settings
from services import user_service, report_service, email_service



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