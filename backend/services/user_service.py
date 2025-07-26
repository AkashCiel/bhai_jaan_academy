import json
import os
import re
from typing import List, Dict, Any, Optional
from config import settings

class UserService:
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(__file__), "..", settings.USERS_FILE)
    
    def load_users(self) -> List[Dict[str, Any]]:
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                return json.load(f)
        else:
            return []
    
    def save_users(self, users: List[Dict[str, Any]]) -> None:
        """Save users to JSON file"""
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)
    
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
        users = self.load_users()
        for user in users:
            if user["email"].lower() == email.lower() and user["main_topic"] == topic:
                return user
        return None
    
    def add_user(self, email: str, topic: str, learning_plan: List[str], plan_url: str, 
                 report_links: Dict[int, str] = None, last_report_time: str = None) -> Dict[str, Any]:
        """Add new user to the system"""
        users = self.load_users()
        
        user_entry = {
            "email": email,
            "main_topic": topic,
            "learning_plan": learning_plan,
            "current_index": 1 if report_links else 0,
            "plan_url": plan_url,
            "report_links": report_links or {},
            "last_report_time": last_report_time
        }
        
        users.append(user_entry)
        self.save_users(users)
        return user_entry
    
    def update_user_progress(self, user: Dict[str, Any], report_url: str, topic: str, 
                           current_index: int, last_report_time: str) -> Dict[str, Any]:
        """Update user's learning progress"""
        # Update report_links
        report_links = user.get("report_links", {})
        report_links[current_index] = report_url
        
        # Update user data
        user["current_index"] = current_index + 1
        user["last_report_time"] = last_report_time
        user["report_links"] = report_links
        
        # Save updated users
        users = self.load_users()
        for i, u in enumerate(users):
            if u["email"] == user["email"] and u["main_topic"] == user["main_topic"]:
                users[i] = user
                break
        self.save_users(users)
        
        return user
    
    def get_next_topic(self, user: Dict[str, Any]) -> Optional[tuple[int, str]]:
        """Get next topic for user"""
        idx = user.get("current_index", 0)
        topics = user.get("learning_plan", [])
        if idx < len(topics):
            return idx, topics[idx]
        return None, None
    
    def should_generate_report(self, user: Dict[str, Any]) -> bool:
        """Determine if a report should be generated for user"""
        import datetime
        
        now = datetime.datetime.now(datetime.timezone.utc)
        last_report_time = user.get("last_report_time")
        current_index = user.get("current_index", 0)
        
        # If current_index == 1 and last_report_time is today, skip
        if last_report_time:
            try:
                last_dt = datetime.datetime.fromisoformat(last_report_time)
            except Exception:
                last_dt = None
        else:
            last_dt = None
            
        if current_index == 1 and last_dt and self._is_same_utc_day(now, last_dt):
            return False
        return True
    
    def _is_same_utc_day(self, dt1, dt2):
        """Check if two datetime objects are on the same UTC day"""
        return dt1.date() == dt2.date() 