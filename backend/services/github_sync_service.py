import requests
import base64
import json
from typing import Dict, Any, Optional
from datetime import datetime
from config import settings

class GitHubSyncService:
    """Service for syncing files to the main GitHub repository"""
    
    def __init__(self):
        self.github_api_url = "https://api.github.com"
        self.repo_owner = settings.GITHUB_REPO_OWNER
        self.repo_name = settings.GITHUB_REPO_NAME
        self.branch = settings.GITHUB_BRANCH
        self.token = settings.REPORTS_GITHUB_TOKEN
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _get_file_sha(self, file_path: str) -> Optional[str]:
        """Get the SHA of an existing file in the repository"""
        try:
            url = f"{self.github_api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
            params = {"ref": self.branch}
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            
            if response.status_code == 200:
                return response.json()["sha"]
            elif response.status_code == 404:
                return None
            else:
                print(f"[GitHub Sync] Error getting file SHA: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[GitHub Sync] Exception getting file SHA: {e}")
            return None
    
    def commit_file(self, file_path: str, content: str, commit_message: str) -> bool:
        """
        Commit a file to the GitHub repository
        
        Args:
            file_path: Path to the file in the repository (e.g., "backend/users.json")
            content: File content as string
            commit_message: Commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.token:
                print("[GitHub Sync] MAIN_GITHUB_TOKEN not configured, skipping sync")
                return False
            
            # Get current file SHA if it exists
            sha = self._get_file_sha(file_path)
            
            # Prepare commit payload
            content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            
            payload = {
                "message": commit_message,
                "content": content_b64,
                "branch": self.branch
            }
            
            # Add SHA if file exists (for updates)
            if sha:
                payload["sha"] = sha
            
            # Make the API request
            url = f"{self.github_api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
            response = requests.put(url, headers=self._get_headers(), json=payload)
            
            if response.status_code in [200, 201]:
                print(f"[GitHub Sync] Successfully committed {file_path} to GitHub")
                return True
            else:
                print(f"[GitHub Sync] Error committing file: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[GitHub Sync] Exception committing file: {e}")
            return False
    
    def sync_users_json(self, users_data: list) -> bool:
        """
        Sync users.json to GitHub repository
        
        Args:
            users_data: List of user dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert users data to JSON string
            content = json.dumps(users_data, indent=2, ensure_ascii=False)
            
            # Create commit message with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            commit_message = f"Auto-sync users.json - {timestamp}"
            
            # Commit to GitHub
            return self.commit_file("users.json", content, commit_message)
            
        except Exception as e:
            print(f"[GitHub Sync] Exception syncing users.json: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if GitHub sync is properly configured"""
        return bool(self.token and self.repo_owner and self.repo_name) 