# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import os
from config import settings
from services import user_service, report_service, email_service
from services.payment_service import PayPalService



app = FastAPI(title="Bhai Jaan Academy API", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class UserSubmission(BaseModel):
    email: EmailStr
    topic: str

class PaymentVerification(BaseModel):
    payment_id: str
    payer_id: str



@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Bhai Jaan Academy API is running"}



# Initialize PayPal service
paypal_service = PayPalService()

@app.post("/create-payment")
async def create_payment(user_data: UserSubmission):
    """Create a PayPal payment for the learning plan"""
    try:
        print(f"[Payment] Creating payment for: email={user_data.email}, topic={user_data.topic}")
        
        # Check for duplicate using shared service
        is_duplicate, sanitized_topic, message = user_service.check_duplicate_user(user_data.email, user_data.topic)
        if is_duplicate:
            print(f"[Payment] Duplicate found for email={user_data.email}, topic={sanitized_topic}")
            return {
                "success": False,
                "message": message,
                "email": user_data.email,
                "topic": sanitized_topic
            }
        
        # Create PayPal payment
        success, message, approval_url = paypal_service.create_payment(user_data.email, sanitized_topic)
        
        if success:
            return {
                "success": True,
                "message": message,
                "approval_url": approval_url,
                "email": user_data.email,
                "topic": sanitized_topic
            }
        else:
            return {
                "success": False,
                "message": f"Payment creation failed: {message}",
                "email": user_data.email,
                "topic": sanitized_topic
            }
            
    except Exception as e:
        print(f"[Payment] Error creating payment: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error creating payment: {str(e)}",
            "email": user_data.email,
            "topic": user_data.topic
        }

@app.post("/verify-payment")
async def verify_payment(payment_data: PaymentVerification):
    """Verify and process payment, then register user"""
    try:
        print(f"[Payment] Verifying payment: payment_id={payment_data.payment_id}")
        
        # Verify payment with PayPal
        success, message, email, topic = paypal_service.verify_payment(payment_data.payment_id, payment_data.payer_id)
        
        if not success:
            return {
                "success": False,
                "message": f"Payment verification failed: {message}"
            }
        
        if not email:
            return {
                "success": False,
                "message": "Payment verified but email not found"
            }
        
        if not topic:
            return {
                "success": False,
                "message": "Payment verified but topic not found"
            }
        
        print(f"[Payment] Payment verified successfully for: email={email}, topic={topic}")
        
        # Generate learning plan using existing service
        result = report_service.generate_initial_learning_plan(email, topic)
        
        # Add payment information to result
        result['payment_id'] = payment_data.payment_id
        result['payment_verified'] = True
        
        return result
        
    except Exception as e:
        print(f"[Payment] Error verifying payment: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error verifying payment: {str(e)}"
        }

@app.post("/register-user-without-payment")
async def register_user_without_payment(user_data: UserSubmission):
    """Register user and generate learning plan without payment"""
    try:
        print(f"[Registration] Registering user without payment: email={user_data.email}, topic={user_data.topic}")
        
        # Check for duplicate using shared service
        is_duplicate, sanitized_topic, message = user_service.check_duplicate_user(user_data.email, user_data.topic)
        if is_duplicate:
            print(f"[Registration] Duplicate found for email={user_data.email}, topic={sanitized_topic}")
            return {
                "success": False,
                "message": message,
                "email": user_data.email,
                "topic": sanitized_topic
            }
        
        # Generate learning plan directly
        result = report_service.generate_initial_learning_plan(user_data.email, sanitized_topic)
        
        # Add payment bypass indicator
        if result.get('success'):
            result['payment_bypassed'] = True
            result['message'] = f"Learning plan created successfully! (Payments disabled) - {result['message']}"
        
        print(f"[Registration] User registered successfully: email={user_data.email}, topic={sanitized_topic}")
        return result
        
    except Exception as e:
        print(f"[Registration] Error registering user: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error registering user: {str(e)}",
            "email": user_data.email,
            "topic": user_data.topic
        }

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
        success_count = 0
        errors = []
        
        # Process each user using service
        for user in users:
            try:
                updated_user = report_service.generate_next_report(user)
                if updated_user:
                    updated_users.append(updated_user)
                    success_count += 1
            except Exception as e:
                error_msg = f"User {user.get('email', 'Unknown')}: {str(e)}"
                errors.append(error_msg)
                print(f"[Scheduler] Error processing user: {error_msg}")
        
        # Save updated users using service
        user_service.save_users([user for user in updated_users if user is not None])
        
        # Send daily report notification
        try:
            from services.notification_service import NotificationService
            notification_service = NotificationService()
            notification_service.send_daily_report(len(users), success_count, errors)
        except Exception as notification_error:
            print(f"[Scheduler] Failed to send daily report: {notification_error}")
        
        return {"status": "ok", "message": "Scheduler run complete.", "users_processed": len(users)}
    except Exception as e:
        # Send error alert notification
        try:
            from services.notification_service import NotificationService
            notification_service = NotificationService()
            notification_service.send_error_alert("Scheduler Failure", str(e))
        except Exception as notification_error:
            print(f"[Scheduler] Failed to send error alert: {notification_error}")
        
        print(f"Error in scheduler: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 