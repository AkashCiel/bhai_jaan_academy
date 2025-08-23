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

class PayPalWebhookData(BaseModel):
    event_type: str
    resource: dict


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

@app.post("/configure-hosted-payment")
async def configure_hosted_payment(user_data: UserSubmission):
    """Configure hosted button payment with user data"""
    try:
        print(f"[Hosted Payment] Configuring payment for: email={user_data.email}, topic={user_data.topic}")
        
        # Check for duplicate using shared service
        is_duplicate, sanitized_topic, message = user_service.check_duplicate_user(user_data.email, user_data.topic)
        if is_duplicate:
            print(f"[Hosted Payment] Duplicate found for email={user_data.email}, topic={sanitized_topic}")
            return {
                "success": False,
                "message": message,
                "email": user_data.email,
                "topic": sanitized_topic
            }
        
        # Configure hosted button payment
        result = paypal_service.create_hosted_button_payment(user_data.email, sanitized_topic)
        
        if result.get('success'):
            return {
                "success": True,
                "message": result.get('message'),
                "config": result.get('config'),
                "email": user_data.email,
                "topic": sanitized_topic
            }
        else:
            return {
                "success": False,
                "message": f"Hosted payment configuration failed: {result.get('error')}",
                "email": user_data.email,
                "topic": sanitized_topic
            }
            
    except Exception as e:
        print(f"[Hosted Payment] Error configuring payment: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error configuring hosted payment: {str(e)}",
            "email": user_data.email,
            "topic": user_data.topic
        }

@app.post("/verify-payment")
async def verify_payment(payment_data: PaymentVerification):
    """Verify and process payment, then register user"""
    try:
        print(f"[Payment] Verifying payment: payment_id={payment_data.payment_id}")
        
        # Verify payment with PayPal
        success, message, email = paypal_service.verify_payment(payment_data.payment_id, payment_data.payer_id)
        
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
        
        # Get payment details to extract topic
        payment_details = paypal_service.get_payment_details(payment_data.payment_id)
        if not payment_details:
            return {
                "success": False,
                "message": "Could not retrieve payment details"
            }
        
        # Extract topic from payment description
        description = payment_details.get('description', '')
        topic = description.replace('Bhai Jaan Academy Learning Plan for ', '') if 'Bhai Jaan Academy Learning Plan for ' in description else 'Unknown Topic'
        
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

@app.post("/paypal-webhook")
async def paypal_webhook(request: Request):
    """Handle PayPal webhook notifications for payment events"""
    try:
        # Get the raw body for webhook verification
        body = await request.body()
        headers = dict(request.headers)
        
        print(f"[Webhook] Received PayPal webhook: {headers.get('paypal-transmission-id', 'unknown')}")
        
        # Parse the webhook data
        webhook_data = await request.json()
        print(f"[Webhook] Webhook data: {webhook_data}")
        
        # Check if this is a payment completion event
        if webhook_data.get('event_type') == 'PAYMENT.CAPTURE.COMPLETED':
            resource = webhook_data.get('resource', {})
            
            # Extract payment details
            payment_id = resource.get('id')
            amount = resource.get('amount', {}).get('value')
            currency = resource.get('amount', {}).get('currency_code')
            
            # Extract custom data (email and topic) from the payment
            custom_id = resource.get('custom_id', '')
            
            if custom_id and '|' in custom_id:
                email, topic = custom_id.split('|', 1)
                print(f"[Webhook] Payment completed for: email={email}, topic={topic}")
                
                # Check for duplicate user
                is_duplicate, sanitized_topic, message = user_service.check_duplicate_user(email, topic)
                if is_duplicate:
                    print(f"[Webhook] Duplicate found for email={email}, topic={sanitized_topic}")
                    return {"status": "duplicate", "message": message}
                
                # Generate learning plan
                result = report_service.generate_initial_learning_plan(email, sanitized_topic)
                
                if result.get('success'):
                    print(f"[Webhook] Learning plan generated successfully for {email}")
                    return {"status": "success", "message": "Learning plan generated"}
                else:
                    print(f"[Webhook] Failed to generate learning plan: {result.get('message')}")
                    return {"status": "error", "message": result.get('message')}
            else:
                print(f"[Webhook] No custom_id found in payment resource")
                return {"status": "error", "message": "No user data found in payment"}
        
        elif webhook_data.get('event_type') == 'PAYMENT.CAPTURE.DENIED':
            print(f"[Webhook] Payment denied: {webhook_data}")
            return {"status": "denied", "message": "Payment was denied"}
        
        else:
            print(f"[Webhook] Unhandled event type: {webhook_data.get('event_type')}")
            return {"status": "ignored", "message": "Event type not handled"}
            
    except Exception as e:
        print(f"[Webhook] Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")

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