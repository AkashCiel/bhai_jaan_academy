from typing import List, Dict, Any, Optional
import os
import json
from .base_repository import BaseRepository
from config import settings
from services.github_sync_service import GitHubSyncService

class UserRepository(BaseRepository):
    def __init__(self):
        file_path = os.path.join(os.path.dirname(__file__), "..", settings.USERS_FILE)
        super().__init__(file_path)
        self.github_sync = GitHubSyncService()
    
    def _get_default_data(self) -> List[Dict[str, Any]]:
        return []
    
    def find_all(self) -> List[Dict[str, Any]]:
        """Get all users"""
        # Try to read from GitHub first, fall back to local file
        try:
            if self.github_sync.is_configured():
                content = self.github_sync.get_file_content("users.json")
                if content:
                    return json.loads(content)
        except Exception as e:
            print(f"[User Repository] Error reading from GitHub: {e}")
        
        # Send Discord notification instead of falling back
        try:
            from services.notification_service import NotificationService
            notification_service = NotificationService()
            notification_service.send_error_alert(
                "GitHub Repository Access Failure",
                "Unable to read users.json from bhai_jaan_academy_reports repository"
            )
        except Exception as notification_error:
            print(f"[User Repository] Failed to send notification: {notification_error}")
        
        raise Exception("Failed to load users from GitHub repository")
    
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
        
        # Sync to GitHub
        self._sync_to_github(users)
        
        return user
    
    def update(self, email: str, topic: str, updated_user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing user"""
        users = self.find_all()
        for i, user in enumerate(users):
            if user["email"] == email and user["main_topic"] == topic:
                users[i] = updated_user
                self._save_data(users)
                
                # Sync to GitHub
                self._sync_to_github(users)
                
                return updated_user
        return None
    
    def save_all(self, users: List[Dict[str, Any]]) -> None:
        """Save all users"""
        self._save_data(users)
        
        # Sync to GitHub
        self._sync_to_github(users)
    
    def delete(self, email: str, topic: str) -> bool:
        """Delete user by email and topic"""
        users = self.find_all()
        for i, user in enumerate(users):
            if user["email"] == email and user["main_topic"] == topic:
                del users[i]
                self._save_data(users)
                
                # Sync to GitHub
                self._sync_to_github(users)
                
                return True
        return False
    
    def _sync_to_github(self, users: List[Dict[str, Any]]) -> None:
        """Sync users data to GitHub repository"""
        try:
            if self.github_sync.is_configured():
                success = self.github_sync.sync_users_json(users)
                if success:
                    print("[User Repository] Successfully synced users.json to reports repository")
                else:
                    print("[User Repository] Failed to sync users.json to reports repository")
            else:
                print("[User Repository] GitHub sync not configured, skipping sync")
        except Exception as e:
            print(f"[User Repository] Error syncing to GitHub: {e}")
            # Don't fail the main operation if sync fails 