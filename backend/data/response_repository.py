from typing import Dict, Any, Optional
import requests
import base64
import json
import re
from urllib.parse import quote
from datetime import datetime
from config import settings

class ResponseRepository:
    """Repository for AI response data stored on GitHub"""
    
    def __init__(self):
        self.github_api_url = "https://api.github.com"
        self.repo_owner = settings.GITHUB_REPO_OWNER
        self.repo_name = settings.GITHUB_REPO_NAME
        self.token = settings.REPORTS_GITHUB_TOKEN
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def save_response(self, user_email: str, main_topic: str, response_type: str, 
                     response_data: Dict[str, Any], report_topic: Optional[str] = None, 
                     token_count: Optional[int] = None) -> str:
        """Save AI response to GitHub repository alongside HTML reports."""
        # Prepare response data
        response_data = {
            "user_email": user_email,
            "main_topic": main_topic,
            "response_type": response_type,
            "timestamp": datetime.now().isoformat(),
            "raw_response": response_data.get("raw_response", ""),
            "metadata": response_data.get("metadata", {})
        }
        
        # Add type-specific fields
        if response_type == "learning_plan":
            response_data["topics_extracted"] = self._extract_topics_from_plan(response_data["raw_response"])
            response_data["metadata"]["word_count"] = len(response_data["raw_response"].split())
            response_data["metadata"]["model_used"] = settings.OPENAI_MODEL
            response_data["metadata"]["temperature"] = settings.OPENAI_TEMPERATURE
            response_data["metadata"]["max_tokens"] = settings.OPENAI_MAX_TOKENS_PLAN
            if token_count:
                response_data["metadata"]["actual_tokens_used"] = token_count
            filename = "learning_plan_response"
        
        elif response_type == "report":
            response_data["report_topic"] = report_topic
            response_data["metadata"]["word_count"] = len(response_data["raw_response"].split())
            response_data["metadata"]["model_used"] = settings.OPENAI_MODEL
            response_data["metadata"]["temperature"] = settings.OPENAI_TEMPERATURE
            response_data["metadata"]["max_tokens"] = settings.OPENAI_MAX_TOKENS_REPORT
            response_data["metadata"]["links_found"] = self._count_links_in_response(response_data["raw_response"])
            if token_count:
                response_data["metadata"]["actual_tokens_used"] = token_count
            filename = f"{self._normalize_filename(report_topic)}_response"
        
        else:
            raise ValueError(f"Invalid response_type: {response_type}")
        
        # Convert to JSON string
        json_content = json.dumps(response_data, indent=2, ensure_ascii=False)
        
        # Upload to GitHub using report repository
        from .report_repository import ReportRepository
        report_repo = ReportRepository()
        github_url = report_repo.upload_report(user_email, main_topic, json_content, filename, "json")
        print(f"[Response Repository] Uploaded {response_type} response to GitHub: {github_url}")
        return github_url
    
    def load_response(self, user_email: str, main_topic: str, response_type: str, 
                     report_topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load previous AI response from GitHub repository."""
        try:
            # Generate the expected filename
            if response_type == "learning_plan":
                filename = "learning_plan_response.json"
            elif response_type == "report":
                if not report_topic:
                    raise ValueError("report_topic is required for report responses")
                filename = f"{self._normalize_filename(report_topic)}_response.json"
            else:
                raise ValueError(f"Invalid response_type: {response_type}")
            
            # Construct GitHub API URL
            user_dir = user_email.replace('@', '').replace('.', '')
            topic_dir = self._normalize_filename(main_topic)
            file_path = f"reports/{user_dir}/{topic_dir}/{filename}"
            
            url = f"{self.github_api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{quote(file_path)}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code != 200:
                print(f"[Response Repository] Response not found on GitHub: {response.status_code}")
                return None
            
            # Decode content from GitHub
            content_b64 = response.json()['content']
            content = base64.b64decode(content_b64).decode('utf-8')
            response_data = json.loads(content)
            
            print(f"[Response Repository] Loaded {response_type} response from GitHub: {file_path}")
            return response_data
        
        except Exception as e:
            print(f"[Response Repository] Error loading response from GitHub: {e}")
            return None
    
    def _normalize_filename(self, text: str) -> str:
        """Convert text to a safe filename by removing/replacing special characters."""
        # Convert to lowercase
        normalized = text.lower()
        # Replace spaces and special chars with underscores
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        normalized = re.sub(r'\s+', '_', normalized)
        # Remove leading/trailing underscores
        normalized = normalized.strip('_')
        return normalized
    
    def _extract_topics_from_plan(self, plan: str) -> list:
        """Extract topic titles from the OpenAI learning plan response."""
        topics = []
        for line in plan.splitlines():
            # Match lines like '1. **Topic**' or '1. Topic'
            match = re.match(r'^\s*\d+\.\s+\*?\*?(.+?)\*?\*?\s*$', line)
            if match:
                topic = match.group(1).strip()
                topics.append(topic)
        return topics
    
    def _count_links_in_response(self, response: str) -> int:
        """Count the number of links in a response."""
        # Count markdown-style links [text](url)
        markdown_links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', response))
        
        # Count our custom link format **Link: [text](url)**
        custom_links = len(re.findall(r'\*\*Link:\s*\[([^\]]+)\]\(([^)]+)\)\*\*', response))
        
        return markdown_links + custom_links 