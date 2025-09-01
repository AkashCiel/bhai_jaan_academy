import json
import os
import re
from typing import List, Dict, Any, Optional
from config import settings
from data import user_repository

class UserService:
    def load_users(self) -> List[Dict[str, Any]]:
        """Load users using repository"""
        return user_repository.find_all()
    
    def save_users(self, users: List[Dict[str, Any]]) -> None:
        """Save users using repository"""
        user_repository.save_all(users)
    
    def sanitize_topic(self, raw_topic: str) -> str:
        """Sanitize topic input"""
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
    
    def find_user_by_email_and_topic(self, email: str, topic: str) -> Optional[Dict[str, Any]]:
        """Find existing user by email and topic"""
        return user_repository.find_by_email_and_topic(email, topic)
    
    def add_user(self, email: str, topic: str, learning_plan: List[str], plan_url: str, 
                 report_links: Optional[Dict[int, str]] = None, last_report_time: Optional[str] = None) -> Dict[str, Any]:
        """Add new user to the system"""
        user_entry = {
            "email": email,
            "main_topic": topic,
            "learning_plan": learning_plan,
            "current_index": 1 if report_links else 0,
            "plan_url": plan_url,
            "report_links": report_links or {},
            "last_report_time": last_report_time
        }
        
        return user_repository.save(user_entry)
    
    def update_user_progress(self, user: Dict[str, Any], report_url: str, topic: str, 
                           current_index: int, last_report_time: str) -> Optional[Dict[str, Any]]:
        """Update user's learning progress"""
        # Update report_links
        report_links = user.get("report_links", {})
        report_links[current_index] = report_url
        
        # Update user data
        updated_user = {
            **user,
            "current_index": current_index + 1,
            "last_report_time": last_report_time,
            "report_links": report_links
        }
        
        return user_repository.update(user["email"], user["main_topic"], updated_user)
    
    def get_next_topic(self, user: Dict[str, Any]) -> tuple[int | None, str | None]:
        """Get next topic for user"""
        idx = user.get("current_index", 0)
        topics = user.get("learning_plan", [])
        if idx < len(topics):
            return (idx, topics[idx])
        return None, None
    
    # Keep this for reference, but not used in the current implementation
    # def should_generate_report(self, user: Dict[str, Any]) -> bool:
    #     """Determine if a report should be generated for user"""
    #     import datetime
        
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
            
    #     if current_index == 1 and last_dt and self._is_same_utc_day(now, last_dt):
    #         return False
    #     return True
    
    def _is_same_utc_day(self, dt1, dt2):
        """Check if two datetime objects are on the same UTC day"""
        return dt1.date() == dt2.date() 

    def check_duplicate_user(self, email: str, topic: str) -> tuple[bool, str, str]:
        """
        Check if user already has a plan for the given topic
        
        Args:
            email: User's email address
            topic: Learning topic
            
        Returns:
            Tuple of (is_duplicate, sanitized_topic, message)
        """
        sanitized_topic = self.sanitize_topic(topic)
        existing_user = self.find_user_by_email_and_topic(email, sanitized_topic)
        
        if existing_user:
            return True, sanitized_topic, "You already have a plan for this topic."
        
        return False, sanitized_topic, "" 