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
            'mode': 'sandbox',  # Use sandbox for testing
            'client_id': os.getenv('PAYPAL_CLIENT_ID'),
            'client_secret': os.getenv('PAYPAL_CLIENT_SECRET')
        })
        
        # Payment configuration
        self.amount = "99.00"
        self.currency = "USD"  # Using USD for sandbox testing (INR not supported in sandbox)
        self.description = "Bhai Jaan Academy Learning Plan"
        
        # Redirect URLs
        self.success_url = "https://akashciel.github.io/bhai_jaan_academy/?payment=success"
        self.cancel_url = "https://akashciel.github.io/bhai_jaan_academy/?payment=cancel"
    
    def create_hosted_button_payment(self, email: str, topic: str) -> Dict[str, any]:
        """
        Create a hosted button payment configuration
        
        Args:
            email: User's email address
            topic: Learning topic
            
        Returns:
            Dictionary with payment configuration
        """
        try:
            # For hosted buttons, we need to configure the button with custom data
            # The custom_id will be passed to the webhook
            custom_id = f"{email}|{topic}"
            
            payment_config = {
                "email": email,
                "topic": topic,
                "amount": self.amount,
                "currency": self.currency,
                "description": f"{self.description} for {topic}",
                "custom_id": custom_id,
                "button_id": "BAWT3J3MX5BW2"
            }
            
            logger.info(f"Hosted button payment config created for {email} - {topic}")
            return {
                "success": True,
                "config": payment_config,
                "message": "Hosted button payment configured"
            }
            
        except Exception as e:
            error_msg = f"Error creating hosted button payment config: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

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
                    "custom": email  # Store email in custom field
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
    
    def verify_payment(self, payment_id: str, payer_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Verify and capture a PayPal payment
        
        Args:
            payment_id: PayPal payment ID
            payer_id: PayPal payer ID
            
        Returns:
            Tuple of (success, message, email)
        """
        try:
            # Execute payment using correct SDK pattern
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logger.info(f"Payment {payment_id} executed successfully")
                
                # Extract email from custom field
                email = None
                if payment.transactions and len(payment.transactions) > 0:
                    email = payment.transactions[0].get('custom')
                
                return True, "Payment verified successfully", email
            else:
                error_msg = f"Payment execution failed: {payment.error}"
                logger.error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error verifying payment: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
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
                "amount": payment.transactions[0].amount.total if payment.transactions else None,
                "currency": payment.transactions[0].amount.currency if payment.transactions else None,
                "email": payment.transactions[0].get('custom') if payment.transactions else None
            }
        except Exception as e:
            logger.error(f"Error getting payment details: {str(e)}")
            return None
