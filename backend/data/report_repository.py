from typing import Optional, Dict
import requests
import base64
import re
from urllib.parse import quote
from config import settings

class ReportRepository:
    """Repository for report files stored on GitHub"""
    
    def __init__(self):
        self.github_api_url = "https://api.github.com"
        self.repo_owner = settings.GITHUB_REPO_OWNER
        self.repo_name = settings.GITHUB_REPO_NAME
        self.branch = settings.GITHUB_BRANCH
        self.token = settings.REPORTS_GITHUB_TOKEN
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def upload_report(self, email: str, topic: str, content: str, 
                     filename: Optional[str] = None, content_type: str = "html") -> str:
        """
        Uploads content to the GitHub repo in the correct directory structure and returns the public URL.
        Supports both HTML and JSON content types.
        
        Args:
            email: User's email address
            topic: Main learning topic
            content: Content to upload (HTML or JSON string)
            filename: Optional filename (without extension)
            content_type: Type of content ("html" or "json")
        """
        user_dir = self._user_dir_from_email(email)
        topic_slug = self._slugify_topic(topic)
        dir_path = f"reports/{user_dir}/{topic_slug}"
        
        if filename:
            file_slug = self._slugify_topic(filename)
            file_name = f"{file_slug}.{content_type}"
        else:
            file_name = f"{topic}.{content_type}"
        
        file_path = f"{dir_path}/{file_name}"
        
        # Check if file exists to get its SHA (for update vs create)
        sha = self._get_file_sha(file_path)
        
        # Prepare commit payload
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        commit_msg = f"Add {content_type} file for {email} - {topic}"
        payload = {
            "message": commit_msg,
            "content": content_b64,
            "branch": self.branch
        }
        if sha:
            payload["sha"] = sha
        
        url = f"{self.github_api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{quote(file_path)}"
        r = requests.put(url, headers=self._get_headers(), json=payload)
        if r.status_code not in (200, 201):
            raise Exception(f"Failed to upload {content_type} file: {r.status_code} {r.text}")
        
        # Construct the public GitHub Pages URL
        public_url = f"https://{self.repo_owner.lower()}.github.io/{self.repo_name}/{dir_path}/{quote(file_name)}"
        return public_url
    
    def _slugify_topic(self, value: str) -> str:
        """
        Converts a string to a slug suitable for directory or file names (for topic).
        """
        value = value.strip()
        value = re.sub(r'[^a-zA-Z0-9\-_ ]', '', value)
        value = re.sub(r'\s+', '_', value)
        return value
    
    def _user_dir_from_email(self, email: str) -> str:
        """
        Extracts the username from the email (before @) and removes all special characters.
        """
        username = email.split('@')[0]
        username = re.sub(r'[^a-zA-Z0-9]', '', username)
        return username
    
    def _get_file_sha(self, path: str) -> Optional[str]:
        """
        Returns the SHA of a file in the repo if it exists, else None.
        """
        url = f"{self.github_api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{quote(path)}"
        r = requests.get(url, headers=self._get_headers())
        if r.status_code == 200:
            return r.json().get('sha')
        return None 