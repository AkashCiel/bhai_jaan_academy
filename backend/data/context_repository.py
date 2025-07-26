from typing import Dict, Any, Optional
import requests
import base64
import json
import re
from urllib.parse import quote
from datetime import datetime
from config import settings

class ContextRepository:
    """Repository for user context summaries stored on GitHub"""
    
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
    
    def save_context_summary(self, user_email: str, main_topic: str, summary_data: Dict[str, Any], 
                           token_count: Optional[int] = None) -> str:
        """Save context summary to GitHub repository."""
        # Prepare context data
        context_data = {
            "user_email": user_email,
            "main_topic": main_topic,
            "summary": summary_data.get("summary", ""),
            "topics_covered": summary_data.get("topics_covered", []),
            "last_updated": datetime.now().isoformat(),
            "report_count": summary_data.get("report_count", 0),
            "metadata": summary_data.get("metadata", {})
        }
        
        # Add token count if provided
        if token_count:
            context_data["metadata"]["actual_tokens_used"] = token_count
        
        # Convert to JSON string
        json_content = json.dumps(context_data, indent=2, ensure_ascii=False)
        
        # Upload to GitHub using report repository
        from .report_repository import ReportRepository
        report_repo = ReportRepository()
        github_url = report_repo.upload_report(user_email, main_topic, json_content, "context_summary", "json")
        print(f"[Context Repository] Uploaded context summary to GitHub: {github_url}")
        return github_url
    
    def load_context_summary(self, user_email: str, main_topic: str) -> Optional[Dict[str, Any]]:
        """Load context summary from GitHub repository."""
        try:
            # Construct GitHub API URL
            user_dir = user_email.replace('@', '').replace('.', '')
            topic_dir = self._normalize_filename(main_topic)
            file_path = f"reports/{user_dir}/{topic_dir}/context_summary.json"
            
            url = f"{self.github_api_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{quote(file_path)}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code != 200:
                print(f"[Context Repository] Context summary not found on GitHub: {response.status_code}")
                return None
            
            # Decode content from GitHub
            content_b64 = response.json()['content']
            content = base64.b64decode(content_b64).decode('utf-8')
            context_data = json.loads(content)
            
            print(f"[Context Repository] Loaded context summary from GitHub: {file_path}")
            return context_data
        
        except Exception as e:
            print(f"[Context Repository] Error loading context summary from GitHub: {e}")
            return None
    
    def update_context_summary(self, user_email: str, main_topic: str, new_report_content: str, 
                             new_topic: str, learning_plan: list) -> str:
        """Update context summary with new report content."""
        try:
            # Load existing context summary
            existing_context = self.load_context_summary(user_email, main_topic)
            
            # Prepare update data
            update_data = {
                "existing_summary": existing_context.get("summary", "") if existing_context else "",
                "new_report_content": new_report_content,
                "new_topic": new_topic,
                "learning_plan": learning_plan,
                "current_topics_covered": existing_context.get("topics_covered", []) if existing_context else [],
                "current_report_count": existing_context.get("report_count", 0) if existing_context else 0
            }
            
            # Generate new summary using AI service
            from services.context_service import ContextService
            context_service = ContextService()
            new_summary_data, token_count = context_service.generate_context_summary(update_data)
            
            # Save updated context summary
            return self.save_context_summary(user_email, main_topic, new_summary_data, token_count)
            
        except Exception as e:
            print(f"[Context Repository] Error updating context summary: {e}")
            # Return empty context if update fails
            return ""
    
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