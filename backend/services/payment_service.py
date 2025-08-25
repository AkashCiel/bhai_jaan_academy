import os
import paypalrestsdk
from typing import Dict, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PayPalService:
    def __init__(self):
        """Initialize PayPal service with sandbox configuration"""
        # Configure PayPal SDK globally
        paypalrestsdk.configure({
            'mode': 'live',  # Use live for production
            'client_id': os.getenv('PAYPAL_CLIENT_ID'),
            'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
        })
        
        # Payment configuration
        self.amount = "1.50"
        self.currency = "EUR"  # Using EUR for live payments
        self.description = "Bhai Jaan Academy Learning Plan"
        
        # Redirect URLs
        self.success_url = "https://bhaijaanacademy.com/?payment=success"  # Update to your live domain
        self.cancel_url = "https://bhaijaanacademy.com/?payment=cancel"    # Update to your live domain
    
    def create_payment(self, email: str, topic: str) -> Tuple[bool, str, Optional[str]]:
        """
        Create a PayPal payment for the learning plan
        
        Args:
            email: User's email address
            topic: Learning topic
            
        Returns:
            Tuple of (success, message, approval_url)
        """
        try:
            # Create payment data
            payment_data = {
                "intent": "SALE",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": self.success_url,
                    "cancel_url": self.cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Learning Plan: {topic}",
                            "sku": "learning-plan",
                            "price": self.amount,
                            "currency": self.currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": self.amount,
                        "currency": self.currency
                    },
                    "description": f"{self.description} for {topic}",
                    "custom": f"{email}|{topic}"  # Store both email and topic
                }]
            }
            
            # Create payment using correct SDK pattern
            payment = paypalrestsdk.Payment(payment_data)
            
            if payment.create():
                logger.info(f"Payment created successfully for {email} - {topic}")
                # Get approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        return True, "Payment created successfully", link.href
                
                return False, "Payment created but approval URL not found", None
            else:
                error_msg = f"Payment creation failed: {payment.error}"
                logger.error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error creating payment: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def verify_payment(self, payment_id: str, payer_id: str) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Verify and capture a PayPal payment
        
        Args:
            payment_id: PayPal payment ID
            payer_id: PayPal payer ID
            
        Returns:
            Tuple of (success, message, email, topic)
        """
        try:
            # Execute payment using correct SDK pattern
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logger.info(f"Payment {payment_id} executed successfully")
                
                # Extract email and topic from custom field
                email = None
                topic = None
                if payment.transactions and len(payment.transactions) > 0:
                    custom_data = payment.transactions[0]['custom']
                    if '|' in custom_data:
                        email, topic = custom_data.split('|', 1)
                        logger.info(f"Email extracted: {email}")
                        logger.info(f"Topic extracted: {topic}")
                    else:
                        # Fallback for old format (email only)
                        email = custom_data
                        logger.info(f"Email extracted: {email} (old format)")
                
                return True, "Payment verified successfully", email, topic
            else:
                error_msg = f"Payment execution failed: {payment.error}"
                logger.error(error_msg)
                return False, error_msg, None, None
                
        except Exception as e:
            error_msg = f"Error verifying payment: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None, None
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """
        Get payment details for logging/debugging
        
        Args:
            payment_id: PayPal payment ID
            
        Returns:
            Payment details dictionary or None
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return {
                "id": payment.id,
                "state": payment.state,
                "amount": payment.transactions[0]['amount']['total'] if payment.transactions else None,
                "currency": payment.transactions[0]['amount']['currency'] if payment.transactions else None,
                "email": payment.transactions[0]['custom'] if payment.transactions else None
            }
        except Exception as e:
            logger.error(f"Error getting payment details: {str(e)}")
            return None
