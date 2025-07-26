#!/usr/bin/env python3
"""
AI response storage utilities for saving and loading OpenAI responses.
This module handles storing raw AI responses in GitHub repository for personalization and context.
"""

import json
import re
import requests
from datetime import datetime
from typing import Optional, Dict, Any

def normalize_filename(text: str) -> str:
    """
    Convert text to a safe filename by removing/replacing special characters.
    """
    # Convert to lowercase
    normalized = text.lower()
    # Replace spaces and special chars with underscores
    normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
    normalized = re.sub(r'\s+', '_', normalized)
    # Remove leading/trailing underscores
    normalized = normalized.strip('_')
    return normalized

def load_ai_response(user_email: str, main_topic: str, response_type: str, 
                      report_topic: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load previous AI response from GitHub repository.
    
    Args:
        user_email: User's email address
        main_topic: Main learning topic
        response_type: Type of response ("learning_plan" or "report")
        report_topic: Specific report topic (only for report responses)
    
    Returns:
        Response data dictionary or None if not found
    """
    try:
        # Generate the expected filename
        if response_type == "learning_plan":
            filename = "learning_plan_response.json"
        elif response_type == "report":
            if not report_topic:
                raise ValueError("report_topic is required for report responses")
            filename = f"{normalize_filename(report_topic)}_response.json"
        else:
            raise ValueError(f"Invalid response_type: {response_type}")
        
        # Construct GitHub API URL
        from report_uploads.github_report_uploader import GITHUB_API_URL, REPO_OWNER, REPO_NAME, get_github_headers
        from urllib.parse import quote
        
        user_dir = user_email.replace('@', '').replace('.', '')
        topic_dir = normalize_filename(main_topic)
        file_path = f"reports/{user_dir}/{topic_dir}/{filename}"
        
        url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{quote(file_path)}"
        response = requests.get(url, headers=get_github_headers())
        
        if response.status_code != 200:
            print(f"[Response Storage] Response not found on GitHub: {response.status_code}")
            return None
        
        # Decode content from GitHub
        import base64
        content_b64 = response.json()['content']
        content = base64.b64decode(content_b64).decode('utf-8')
        response_data = json.loads(content)
        
        print(f"[Response Storage] Loaded {response_type} response from GitHub: {file_path}")
        return response_data
    
    except Exception as e:
        print(f"[Response Storage] Error loading response from GitHub: {e}")
        return None

def save_ai_response(user_email: str, main_topic: str, response_type: str, raw_response: str, 
                      report_topic: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Save raw OpenAI response to GitHub repository alongside HTML reports.
    
    Args:
        user_email: User's email address
        main_topic: Main learning topic
        response_type: Type of response ("learning_plan" or "report")
        raw_response: Raw OpenAI response content
        report_topic: Specific report topic (only for report responses)
        metadata: Additional metadata to store
    
    Returns:
        GitHub URL of the uploaded response file
    """
    # Prepare response data
    response_data = {
        "user_email": user_email,
        "main_topic": main_topic,
        "response_type": response_type,
        "timestamp": datetime.now().isoformat(),
        "raw_response": raw_response,
        "metadata": metadata or {}
    }
    
    # Add type-specific fields
    if response_type == "learning_plan":
        response_data["topics_extracted"] = extract_topics_from_plan(raw_response)
        response_data["metadata"]["word_count"] = len(raw_response.split())
        response_data["metadata"]["model_used"] = "gpt-4o-mini"
        response_data["metadata"]["temperature"] = 0.7
        response_data["metadata"]["max_tokens"] = 2000
        filename = "learning_plan_response"
    
    elif response_type == "report":
        response_data["report_topic"] = report_topic
        response_data["metadata"]["word_count"] = len(raw_response.split())
        response_data["metadata"]["model_used"] = "gpt-4o-mini"
        response_data["metadata"]["temperature"] = 0.7
        response_data["metadata"]["max_tokens"] = 1800
        response_data["metadata"]["links_found"] = count_links_in_response(raw_response)
        filename = f"{normalize_filename(report_topic)}_response"
    
    else:
        raise ValueError(f"Invalid response_type: {response_type}")
    
    # Convert to JSON string
    json_content = json.dumps(response_data, indent=2, ensure_ascii=False)
    
    # Upload to GitHub
    try:
        from report_uploads.github_report_uploader import upload_report
        github_url = upload_report(user_email, main_topic, json_content, filename, "json")
        print(f"[Response Storage] Uploaded {response_type} response to GitHub: {github_url}")
        return github_url
    except Exception as e:
        print(f"[Response Storage] Error uploading to GitHub: {e}")
        raise

def extract_topics_from_plan(plan: str) -> list:
    """
    Extract topic titles from the OpenAI learning plan response.
    """
    topics = []
    for line in plan.splitlines():
        # Match lines like '1. **Topic**' or '1. Topic'
        match = re.match(r'^\s*\d+\.\s+\*?\*?(.+?)\*?\*?\s*$', line)
        if match:
            topic = match.group(1).strip()
            topics.append(topic)
    return topics

def count_links_in_response(response: str) -> int:
    """
    Count the number of links in a response.
    """
    # Count markdown-style links [text](url)
    markdown_links = len(re.findall(r'\[([^\]]+)\]\(([^)]+)\)', response))
    
    # Count our custom link format **Link: [text](url)**
    custom_links = len(re.findall(r'\*\*Link:\s*\[([^\]]+)\]\(([^)]+)\)\*\*', response))
    
    return markdown_links + custom_links

def get_user_learning_context(user_email: str, main_topic: str) -> Dict[str, Any]:
    """
    Get user's learning history for personalization from GitHub repository.
    
    Args:
        user_email: User's email address
        main_topic: Main learning topic
    
    Returns:
        Dictionary containing user's learning context
    """
    context = {
        "previous_reports": [],
        "learning_plan": None,
        "topics_completed": 0,
        "last_report_time": None
    }
    
    try:
        # Load learning plan response from GitHub
        learning_plan_data = load_ai_response(user_email, main_topic, "learning_plan")
        if learning_plan_data:
            context["learning_plan"] = learning_plan_data
            context["topics_completed"] = len(learning_plan_data.get("topics_extracted", []))
        
        # Load all report responses from GitHub
        # Note: This would require listing directory contents from GitHub API
        # For now, we'll load individual reports as needed
        # In a full implementation, you might want to cache this or implement directory listing
        
        # Get last report time from learning plan if available
        if context["learning_plan"]:
            context["last_report_time"] = context["learning_plan"]["timestamp"]
    
    except Exception as e:
        print(f"[Response Storage] Error getting learning context: {e}")
    
    return context 