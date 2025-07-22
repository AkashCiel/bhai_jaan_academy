import os
import requests
import json
import time

NETLIFY_ACCESS_TOKEN = os.getenv("NETLIFY_ACCESS_TOKEN")
NETLIFY_SITE_ID = os.getenv("NETLIFY_SITE_ID")

# Validate environment variables
if not NETLIFY_ACCESS_TOKEN:
    raise ValueError("NETLIFY_ACCESS_TOKEN environment variable is not set")
if not NETLIFY_SITE_ID:
    raise ValueError("NETLIFY_SITE_ID environment variable is not set (you can use your site name like 'bhai-jaan-academy-reports')")


def submit_form_to_netlify(email: str, topic: str) -> dict:
    """
    Submit form data to Netlify Forms API
    Note: This requires a form to be created first in your Netlify site
    """
    try:
        print(f"[Netlify Forms] Submitting form: email={email}, topic={topic}")
        
        # For now, let's just return a success response since we need to set up the form first
        # In a real implementation, you would submit to a specific form endpoint
        print(f"[Netlify Forms] Form submission simulated successfully")
        
        return {
            "success": True,
            "message": "Form data received",
            "email": email,
            "topic": topic
        }
        
    except Exception as e:
        print(f"[Netlify Forms] Exception: {e}")
        raise


def deploy_html_to_netlify(filename: str, html_content: str) -> str:
    """
    Deploys an HTML file to Netlify using their API and returns the public URL.
    Uses Netlify's deploy API to upload files directly.
    """
    try:
        print(f"[Netlify Deploy] Deploying file: {filename}")
        
        # Create a temporary directory structure for the file
        file_data = {
            "path": f"reports/{filename}",
            "content": html_content
        }
        
        # Prepare the deploy payload
        deploy_payload = {
            "files": [file_data]
        }
        
        # Netlify deploy API endpoint
        url = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}/deploys"
        
        headers = {
            "Authorization": f"Bearer {NETLIFY_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        print(f"[Netlify Deploy] Deploying to: {url}")
        print(f"[Netlify Deploy] Headers: {headers}")
        
        response = requests.post(url, headers=headers, json=deploy_payload)
        
        print(f"[Netlify Deploy] Response status: {response.status_code}")
        print(f"[Netlify Deploy] Response text: {response.text}")
        
        if not response.ok:
            raise Exception(f"Failed to deploy to Netlify: {response.text}")
        
        # Parse the response to get the deploy URL
        deploy_data = response.json()
        deploy_url = deploy_data.get("url")
        
        if not deploy_url:
            raise Exception("No deploy URL returned from Netlify")
        
        # Construct the public URL for the specific file
        public_url = f"{deploy_url}/reports/{filename}"
        print(f"[Netlify Deploy] Public URL: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"[Netlify Deploy] Exception: {e}")
        raise 