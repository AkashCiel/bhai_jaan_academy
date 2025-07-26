from typing import List, Dict, Any, Optional
import os
from .base_repository import BaseRepository
from config import settings

class UserRepository(BaseRepository):
    def __init__(self):
        file_path = os.path.join(os.path.dirname(__file__), "..", settings.USERS_FILE)
        super().__init__(file_path)
    
    def _get_default_data(self) -> List[Dict[str, Any]]:
        return []
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all users"""
        return self._load_data()
    
    def find_by_email_and_topic(self, email: str, topic: str) -> Optional[Dict[str, Any]]:
        """Find user by email and topic"""
        users = self.find_all()
        for user in users:
            if user["email"].lower() == email.lower() and user["main_topic"] == topic:
                return user
        return None
    
    def save(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Save a new user"""
        users = self.find_all()
        users.append(user)
        self._save_data(users)
        return user
    
    def update(self, email: str, topic: str, updated_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing user"""
        users = self.find_all()
        for i, user in enumerate(users):
            if user["email"] == email and user["main_topic"] == topic:
                users[i] = updated_user
                self._save_data(users)
                return updated_user
        return None
    
    def save_all(self, users: List[Dict[str, Any]]) -> None:
        """Save all users"""
        self._save_data(users)
    
    def delete(self, email: str, topic: str) -> bool:
        """Delete user by email and topic"""
        users = self.find_all()
        for i, user in enumerate(users):
            if user["email"] == email and user["main_topic"] == topic:
                del users[i]
                self._save_data(users)
                return True
        return False 